from pathlib import Path

p = Path("src/generate.py")
s = p.read_text(encoding="utf-8")
s = s.replace('<section class="b g\'>', '<section class="b g">')
p.write_text(s, encoding="utf-8")
exec(compile(s, str(p), "exec"), {"__name__": "__main__", "__file__": str(p)})
