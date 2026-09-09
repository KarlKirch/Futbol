import webpush from "npm:web-push@3.6.7";

const APP_URL = "https://karlkirch.github.io/Futbol/wod/app.html";

function getSecretKey(): string {
  const raw = Deno.env.get("SUPABASE_SECRET_KEYS");
  if (raw) {
    const parsed = JSON.parse(raw);
    if (parsed?.default) return parsed.default;
  }
  const legacy = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY");
  if (legacy) return legacy;
  throw new Error("Supabase secret key puudub");
}

async function adminFetch(path: string, init: RequestInit = {}) {
  const base = Deno.env.get("SUPABASE_URL");
  if (!base) throw new Error("SUPABASE_URL puudub");
  const secret = getSecretKey();
  const headers = new Headers(init.headers || {});
  headers.set("apikey", secret);
  if (!headers.has("Content-Type")) headers.set("Content-Type", "application/json");
  const res = await fetch(base + "/rest/v1/" + path, { ...init, headers });
  const text = await res.text();
  let data: any = null;
  try { data = text ? JSON.parse(text) : null; } catch { data = text; }
  if (!res.ok) throw new Error(typeof data === "string" ? data : JSON.stringify(data));
  return data;
}

Deno.serve(async (req: Request) => {
  try {
    if (req.method !== "POST") {
      return Response.json({ ok: false, error: "Method not allowed" }, { status: 405 });
    }

    const settingsRows = await adminFetch("rpc/server_get_push_settings", {
      method: "POST",
      body: "{}",
    });
    const settings = Array.isArray(settingsRows) ? settingsRows[0] : settingsRows;

    const suppliedToken = req.headers.get("x-wod-cron") || "";
    if (!settings?.cron_token || suppliedToken !== settings.cron_token) {
      return Response.json({ ok: false, error: "Unauthorized" }, { status: 401 });
    }
    if (!settings?.vapid_public || !settings?.vapid_private) {
      throw new Error("Web Push seaded puuduvad");
    }

    webpush.setVapidDetails(APP_URL, settings.vapid_public, settings.vapid_private);

    const nowIso = new Date().toISOString();
    const notifications = await adminFetch(
      "wod_notifications?select=id,user_id,training_id,kind,title,body,url,tag,attempts&sent_at=is.null&due_at=lte." +
      encodeURIComponent(nowIso) + "&order=due_at.asc&limit=100"
    );

    let processed = 0;
    let sentSubscriptions = 0;
    let removedSubscriptions = 0;

    for (const n of notifications || []) {
      const subs = await adminFetch(
        "wod_push_subscriptions?select=id,endpoint,p256dh,auth&user_id=eq." + encodeURIComponent(n.user_id)
      );

      const payload = JSON.stringify({
        title: n.title,
        body: n.body,
        url: n.url || APP_URL,
        tag: n.tag || `crossfit-${n.id}`,
      });

      for (const sub of subs || []) {
        try {
          await webpush.sendNotification(
            {
              endpoint: sub.endpoint,
              keys: { p256dh: sub.p256dh, auth: sub.auth },
            },
            payload,
            { TTL: n.kind === "training_reminder" ? 43200 : 3600, urgency: "high" }
          );
          sentSubscriptions += 1;
        } catch (error: any) {
          const statusCode = Number(error?.statusCode || error?.status || 0);
          if (statusCode === 404 || statusCode === 410) {
            await adminFetch("wod_push_subscriptions?id=eq." + sub.id, { method: "DELETE" });
            removedSubscriptions += 1;
          }
        }
      }

      await adminFetch("wod_notifications?id=eq." + n.id, {
        method: "PATCH",
        headers: { Prefer: "return=minimal" },
        body: JSON.stringify({
          sent_at: new Date().toISOString(),
          attempts: Number(n.attempts || 0) + 1,
        }),
      });
      processed += 1;
    }

    return Response.json({
      ok: true,
      processed,
      sent_subscriptions: sentSubscriptions,
      removed_subscriptions: removedSubscriptions,
    });
  } catch (error) {
    return Response.json({
      ok: false,
      error: error instanceof Error ? error.message : String(error),
    }, { status: 500 });
  }
});
