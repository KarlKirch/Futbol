from pathlib import Path

source = Path("add_core_ux.py").read_text(encoding="utf-8")
marker = "# Refresh only countdown text between full data refreshes."

if marker not in source:
    raise SystemExit("Core UX marker not found")

prefix = source.split(marker, 1)[0]

fixed_tail = r'''# Refresh only countdown text between full data refreshes.
interval_anchor = '''setInterval(() => {

  if (
    currentUser &&
    currentPlayer
  ) {
    loadAll();
  }

}, 60000);'''

interval_replacement = '''setInterval(() => {

  if (
    currentUser &&
    currentPlayer
  ) {
    loadAll();
  }

}, 60000);

setInterval(() => {
  if (currentUser && currentPlayer) {
    refreshCountdowns();
  }
}, 30000);'''

if "refreshCountdowns();\n  }\n}, 30000);" not in text:
    if interval_anchor not in text:
        raise SystemExit("Interval anchor not found")
    text = text.replace(interval_anchor, interval_replacement, 1)

path.write_text(text, encoding="utf-8")
'''

exec(compile(prefix + fixed_tail, "add_core_ux_fixed.py", "exec"))
