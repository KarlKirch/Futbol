import webpush from "npm:web-push@3.6.7";
import { createClient } from "npm:@supabase/supabase-js@2";

const APP_URL = "https://karlkirch.github.io/Futbol/?tab=chat";
const CORS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
};

function json(data: unknown, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { ...CORS, "Content-Type": "application/json" },
  });
}

Deno.serve(async (req: Request) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: CORS });
  if (req.method !== "POST") return json({ ok: false, error: "Method not allowed" }, 405);

  try {
    const supabaseUrl = Deno.env.get("SUPABASE_URL");
    const anonKey = Deno.env.get("SUPABASE_ANON_KEY");
    const serviceRole = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY");
    const authorization = req.headers.get("Authorization") || "";
    if (!supabaseUrl || !anonKey || !serviceRole || !authorization) {
      return json({ ok: false, error: "Unauthorized" }, 401);
    }

    const userClient = createClient(supabaseUrl, anonKey, {
      global: { headers: { Authorization: authorization } },
      auth: { persistSession: false, autoRefreshToken: false },
    });
    const { data: userData, error: userError } = await userClient.auth.getUser();
    if (userError || !userData.user) return json({ ok: false, error: "Unauthorized" }, 401);

    // A restored Futbol account can have a different Supabase Auth id than its player id.
    // Authorize against the linked Futbol player, not directly against auth.uid().
    const { data: playerRows, error: playerError } = await userClient.rpc("get_current_player");
    if (playerError) return json({ ok: false, error: "Player lookup failed" }, 403);
    const currentPlayer = Array.isArray(playerRows) ? playerRows[0] : playerRows;
    const currentPlayerId = String(currentPlayer?.id || "");
    if (!currentPlayerId) return json({ ok: false, error: "Player not linked" }, 403);

    const body = await req.json().catch(() => ({}));
    const messageId = Number(body?.message_id || 0);
    if (!Number.isInteger(messageId) || messageId <= 0) return json({ ok: false, error: "Invalid message" }, 400);

    const admin = createClient(supabaseUrl, serviceRole, {
      auth: { persistSession: false, autoRefreshToken: false },
    });

    const { data: message, error: messageError } = await admin
      .from("chat_messages")
      .select("id,user_id,message,created_at")
      .eq("id", messageId)
      .single();
    if (messageError || !message) return json({ ok: false, error: "Message not found" }, 404);
    if (String(message.user_id) !== currentPlayerId) return json({ ok: false, error: "Forbidden" }, 403);

    const age = Date.now() - new Date(message.created_at).getTime();
    if (!Number.isFinite(age) || age < -60000 || age > 120000) {
      return json({ ok: true, skipped: "stale" });
    }

    const { data: claimed, error: claimError } = await admin.rpc("server_claim_chat_push", { p_message_id: messageId });
    if (claimError) throw claimError;
    if (!claimed) return json({ ok: true, skipped: "duplicate" });

    const [{ data: sender }, { data: settings, error: settingsError }, { data: subscriptions, error: subsError }] = await Promise.all([
      admin.from("players").select("display_name").eq("id", message.user_id).maybeSingle(),
      admin.rpc("server_get_push_settings").single(),
      admin.from("push_subscriptions")
        .select("id,user_id,endpoint,p256dh,auth")
        .eq("chat_enabled", true)
        .neq("user_id", userData.user.id),
    ]);
    if (settingsError) throw settingsError;
    if (subsError) throw subsError;
    if (!settings?.vapid_public || !settings?.vapid_private) throw new Error("Web Push settings missing");

    webpush.setVapidDetails("https://karlkirch.github.io/Futbol/", settings.vapid_public, settings.vapid_private);

    const senderName = String(sender?.display_name || "Keegi").trim() || "Keegi";
    const raw = String(message.message || "").replace(/\s+/g, " ").trim();
    const bodyText = raw.length > 140 ? raw.slice(0, 137) + "…" : raw;
    const payload = JSON.stringify({
      title: `Futbol Chat · ${senderName}`,
      body: bodyText || "Uus sõnum chatis.",
      url: APP_URL,
      tag: "futbol-chat-latest",
    });

    let sent = 0;
    let removed = 0;
    let failed = 0;
    for (const row of subscriptions || []) {
      try {
        await webpush.sendNotification(
          { endpoint: row.endpoint, keys: { p256dh: row.p256dh, auth: row.auth } },
          payload,
          { TTL: 86400, urgency: "high" },
        );
        sent += 1;
      } catch (error: any) {
        failed += 1;
        const statusCode = Number(error?.statusCode || error?.status || 0);
        console.error("chat push delivery failed", { subscription_id: row.id, statusCode });
        if (statusCode === 404 || statusCode === 410) {
          await admin.from("push_subscriptions").delete().eq("id", row.id);
          removed += 1;
        }
      }
    }

    return json({ ok: true, sent, removed, failed });
  } catch (error) {
    console.error("send-chat-notification", error);
    return json({ ok: false, error: error instanceof Error ? error.message : String(error) }, 500);
  }
});
