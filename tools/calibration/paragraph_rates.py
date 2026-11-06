import importlib.util, sys, collections
from pathlib import Path
SK=Path(__file__).resolve().parents[2] / "skills" / "ja-en-translate" / "scripts"
sp=importlib.util.spec_from_file_location("f", SK/"fidelity_check.py"); fid=importlib.util.module_from_spec(sp); sp.loader.exec_module(fid)
docs=Path(sys.argv[1]); tot=0; c=collections.Counter(); docrules=collections.Counter(); n=0
for ja in sorted(docs.glob("*.ja.md")):
    en=ja.with_name(ja.name.replace(".ja.md",".en.md")); n+=1
    r=fid.check(en.read_text(encoding="utf-8"), ja.read_text(encoding="utf-8"))
    if r["paragraphs_aligned"]: tot+=len(fid.paragraphs(fid.split_code(fid.strip_frontmatter(en.read_text(encoding="utf-8")))[0]))
    for f in r["findings"]:
        key=f["rule"]+":"+f["severity"]
        if f["where"] and f["where"].startswith("paragraph"): c[key]+=1
        else: docrules[key]+=1
print(f"docs={n} aligned paragraphs={tot}")
for k,v in c.most_common(): print(f"  per-paragraph {k:28s} {v:5d}  rate={v/tot:.2%}")
for k,v in docrules.most_common(): print(f"  document     {k:28s} docs={v}")
