import webpush from "npm:web-push@3.6.7";
import { createClient } from "npm:@supabase/supabase-js@2";

const APP_URL = "https://karlkirch.github.io/Futbol/";

Deno.serve(async (req: Request) => {
  try {
    if (req.method !== "POST") {
      return new Response(JSON.stringify({ ok: false, error: "Method not allowed" }), {
        status: 405,
        headers: { "Content-Type": "application/json" },
      });
    }

    const supabaseUrl = Deno.env.get("SUPABASE_URL");
    const serviceRole = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY");
    if (!supabaseUrl || !serviceRole) throw new Error("Supabase serveri seaded puuduvad");

    const admin = createClient(supabaseUrl, serviceRole, {
      auth: { persistSession: false, autoRefreshToken: false },
    });

    const { data: settings, error: settingsError } = await admin
      .rpc("server_get_push_settings")
      .single();
    if (settingsError) throw settingsError;

    const suppliedToken = req.headers.get("x-futbol-cron") || "";
    if (!settings?.cron_token || suppliedToken !== settings.cron_token) {
      return new Response(JSON.stringify({ ok: false, error: "Unauthorized" }), {
        status: 401,
        headers: { "Content-Type": "application/json" },
      });
    }

    if (!settings?.vapid_public || !settings?.vapid_private) {
      throw new Error("Web Push seaded puuduvad");
    }

    webpush.setVapidDetails(APP_URL, settings.vapid_public, settings.vapid_private);

    let sentSubscriptions = 0;
    let removedSubscriptions = 0;

    async function deliver(row: any, payload: string, ttl = 3600): Promise<boolean> {
      try {
        await webpush.sendNotification(
          {
            endpoint: row.endpoint,
            keys: { p256dh: row.p256dh, auth: row.auth },
          },
          payload,
          { TTL: ttl, urgency: "high" }
        );
        sentSubscriptions += 1;
        return true;
      } catch (error: any) {
        const statusCode = Number(error?.statusCode || error?.status || 0);
        if (statusCode === 404 || statusCode === 410) {
          await admin.from("push_subscriptions").delete().eq("id", row.subscription_id);
          removedSubscriptions += 1;
        }
        return false;
      }
    }

    const { data: dueRows, error: dueError } = await admin.rpc(
      "server_get_due_prediction_reminders"
    );
    if (dueError) throw dueError;

    const reminderGroups = new Map<string, any[]>();
    for (const row of dueRows || []) {
      const key = `${row.user_id}|${row.kickoff_at}`;
      if (!reminderGroups.has(key)) reminderGroups.set(key, []);
      reminderGroups.get(key)!.push(row);
    }

    let reminderUsers = 0;
    for (const rows of reminderGroups.values()) {
      const first = rows[0];
      const missing = Number(first.missing_count || 0);
      if (!missing) continue;

      const payload = JSON.stringify({
        title: "Futbol – Champions League",
        body: missing === 1
          ? "Mängud algavad umbes tunni pärast. Sul on 1 mäng ennustamata."
          : `Mängud algavad umbes tunni pärast. Sul on ${missing} mängu ennustamata.`,
        url: APP_URL,
        tag: `futbol-reminder-${first.user_id}-${first.kickoff_at}`,
      });

      let delivered = false;
      for (const row of rows) delivered = (await deliver(row, payload, 3600)) || delivered;

      if (delivered) {
        await admin.rpc("server_mark_prediction_reminder_sent", {
          p_user_id: first.user_id,
          p_kickoff_at: first.kickoff_at,
        });
        reminderUsers += 1;
      }
    }

    const { data: reportRows, error: reportError } = await admin.rpc(
      "server_get_due_round_reports"
    );
    if (reportError) throw reportError;

    const reportGroups = new Map<string, any[]>();
    for (const row of reportRows || []) {
      const key = `${row.user_id}|${row.round_number}`;
      if (!reportGroups.has(key)) reportGroups.set(key, []);
      reportGroups.get(key)!.push(row);
    }

    let roundReportUsers = 0;
    for (const rows of reportGroups.values()) {
      const first = rows[0];
      const points = Number(first.round_points || 0);
      const exact = Number(first.exact_scores || 0);
      const rank = first.rank_after ? ` Koht tabelis: ${first.rank_after}.` : "";
      const winner = first.round_winner
        ? ` Vooru parim: ${first.round_winner} (${Number(first.round_winner_points || 0)} p).`
        : "";

      const payload = JSON.stringify({
        title: `Futbol – ${first.round_name || `${first.round_number}. voor`} läbi`,
        body: `Said ${points} punkti, täpseid skoore ${exact}.${rank}${winner}`,
        url: APP_URL,
        tag: `futbol-round-${first.user_id}-${first.round_number}`,
      });

      let delivered = false;
      for (const row of rows) delivered = (await deliver(row, payload, 86400)) || delivered;

      if (delivered) {
        await admin.rpc("server_mark_round_report_sent", {
          p_user_id: first.user_id,
          p_round_number: Number(first.round_number),
        });
        roundReportUsers += 1;
      }
    }

    return new Response(JSON.stringify({
      ok: true,
      reminder_users: reminderUsers,
      round_report_users: roundReportUsers,
      sent_subscriptions: sentSubscriptions,
      removed_subscriptions: removedSubscriptions,
    }), {
      status: 200,
      headers: { "Content-Type": "application/json" },
    });
  } catch (error) {
    return new Response(JSON.stringify({
      ok: false,
      error: error instanceof Error ? error.message : String(error),
    }), {
      status: 500,
      headers: { "Content-Type": "application/json" },
    });
  }
});
