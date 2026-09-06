from pathlib import Path

path = Path("index.html")
text = path.read_text(encoding="utf-8")

# Add a helper that clears a stale local anonymous session and creates a fresh one.
helper_anchor = "async function init() {\n"
helper_code = r'''async function createFreshAnonymousSession() {

  try {
    await sb.auth.signOut({ scope: "local" });
  } catch (error) {
    // A deleted anonymous user can make sign-out fail server-side.
    // Local cleanup/sign-in below is still the recovery path.
  }

  const signIn = await sb.auth.signInAnonymously();

  if (signIn.error) {
    throw signIn.error;
  }

  currentUser = signIn.data.session.user;
  return signIn.data.session;
}

'''

if "async function createFreshAnonymousSession()" not in text:
    if helper_anchor not in text:
        raise SystemExit("init anchor not found")
    text = text.replace(helper_anchor, helper_code + helper_anchor, 1)

# Validate a persisted session against Supabase Auth. This fixes browsers that still
# hold a token for an anonymous user that an admin has since deleted.
old_session = '''    let session =
      sessionResult.data.session;

    if (!session) {

      const signIn =
        await sb.auth.signInAnonymously();

      if (signIn.error) {
        throw signIn.error;
      }

      session =
        signIn.data.session;
    }

    currentUser =
      session.user;'''

new_session = '''    let session =
      sessionResult.data.session;

    if (session) {

      const userCheck =
        await sb.auth.getUser();

      if (
        userCheck.error ||
        !userCheck.data ||
        !userCheck.data.user
      ) {
        session =
          await createFreshAnonymousSession();
      }
    }

    if (!session) {
      session =
        await createFreshAnonymousSession();
    }

    currentUser =
      session.user;'''

if old_session in text:
    text = text.replace(old_session, new_session, 1)
elif "const userCheck =" not in text:
    raise SystemExit("session block not found")

# Also recover directly if the name insert hits the players -> auth.users FK.
old_insert = '''  const result =
    await sb
      .from("players")
      .insert({
        id: currentUser.id,
        display_name: name
      })
      .select()
      .single();

  if (result.error) {'''

new_insert = '''  let result =
    await sb
      .from("players")
      .insert({
        id: currentUser.id,
        display_name: name
      })
      .select()
      .single();

  if (result.error && result.error.code === "23503") {

    try {
      const freshSession =
        await createFreshAnonymousSession();

      currentUser =
        freshSession.user;

      result =
        await sb
          .from("players")
          .insert({
            id: currentUser.id,
            display_name: name
          })
          .select()
          .single();

    } catch (error) {
      errorBox.textContent =
        friendlyError(error);
      return;
    }
  }

  if (result.error) {'''

if old_insert in text:
    text = text.replace(old_insert, new_insert, 1)
elif 'result.error.code === "23503"' not in text:
    raise SystemExit("player insert block not found")

# Make the old FK error readable if it ever appears for another reason.
old_friendly = '''  if (msg.includes("duplicate key")) {
    return "See nimi on juba kasutusel.";
  }
'''
new_friendly = '''  if (msg.includes("duplicate key")) {
    return "See nimi on juba kasutusel.";
  }

  if (
    msg.includes("players_id_fkey") ||
    msg.includes("foreign key constraint")
  ) {
    return "Sisselogimisseanss aegus. Värskenda lehte ja proovi uuesti.";
  }
'''
if "Sisselogimisseanss aegus." not in text:
    if old_friendly not in text:
        raise SystemExit("friendlyError anchor not found")
    text = text.replace(old_friendly, new_friendly, 1)

path.write_text(text, encoding="utf-8")
