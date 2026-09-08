import { createClient } from "npm:@supabase/supabase-js@2";

const CORS_HEADERS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type, x-cron-token",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
};

function json(payload: unknown, status = 200) {
  return new Response(JSON.stringify(payload), {
    status,
    headers: { ...CORS_HEADERS, "Content-Type":"application/json", "Cache-Control":"no-store" },
  });
}

Deno.serve(async (req: Request) => {
  if (req.method === "OPTIONS") return new Response("ok", { status:200, headers:CORS_HEADERS });
  if (req.method !== "POST") return json({ ok:false, error:"Method not allowed" }, 405);

  try {
    const supabaseUrl = Deno.env.get("SUPABASE_URL");
    const serviceRole = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY");
    if (!supabaseUrl || !serviceRole) throw new Error("Supabase serveri seaded puuduvad");

    const token = String(req.headers.get("x-cron-token") || "");
    if (!token) return json({ ok:false, error:"Unauthorized" }, 401);

    const admin = createClient(supabaseUrl, serviceRole, { auth:{ persistSession:false, autoRefreshToken:false } });
    const check = await admin.rpc("check_live_cron_token", { p_token:token });
    if (check.error || check.data !== true) return json({ ok:false, error:"Unauthorized" }, 401);

    const response = await fetch(`${supabaseUrl}/functions/v1/ucl-live-fast`, {
      method:"POST",
      headers:{
        "Content-Type":"application/json",
        "Authorization":`Bearer ${serviceRole}`,
        "apikey":serviceRole,
      },
      body:JSON.stringify({ force:false }),
    });
    const text = await response.text();
    if (!response.ok) return new Response(text, { status:response.status, headers:{ ...CORS_HEADERS, "Content-Type":"application/json", "Cache-Control":"no-store" } });
    return new Response(text, { status:200, headers:{ ...CORS_HEADERS, "Content-Type":"application/json", "Cache-Control":"no-store" } });
  } catch (error) {
    console.error("ucl-live-cron", error);
    return json({ ok:false, error:error instanceof Error ? error.message : String(error) }, 502);
  }
});
