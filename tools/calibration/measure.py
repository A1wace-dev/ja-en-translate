import importlib.util, sys, json, collections
from pathlib import Path
SK=Path(__file__).resolve().parents[2] / "skills" / "ja-en-translate" / "scripts"
def load(n):
    sp=importlib.util.spec_from_file_location(n, SK/f"{n}.py"); m=importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
tone=load("tone_lint"); fid=load("fidelity_check")
docs=Path(sys.argv[1]); ctx=sys.argv[2] if len(sys.argv)>2 else None
stats={"ja":collections.Counter(),"en":collections.Counter()}; chars={"ja":0,"en":0}; docs_hit={"ja":collections.Counter(),"en":collections.Counter()}
scores={"ja":[],"en":[]}; fidc=collections.Counter(); fid_docs=0; ndocs=0
raw={"ja":collections.Counter(),"en":collections.Counter()}
for ja in sorted(docs.glob("*.ja.md")):
    en=ja.with_name(ja.name.replace(".ja.md",".en.md"))
    ndocs+=1
    for lang,p in (("ja",ja),("en",en)):
        t=p.read_text(encoding="utf-8"); chars[lang]+=len(t)
        r=tone.lint(t,lang,ctx); scores[lang].append(r["score"])
        for f in r["findings"]:
            stats[lang][f["rule"]]+=1
        for rule in {f["rule"] for f in r["findings"]}: docs_hit[lang][rule]+=1
    r=fid.check(en.read_text(encoding="utf-8"), ja.read_text(encoding="utf-8"))
    hi=[f["rule"] for f in r["findings"] if f["severity"]=="high"]
    if hi: fid_docs+=1
    for x in set(f["rule"]+":"+f["severity"] for f in r["findings"]): fidc[x]+=1
print(f"docs={ndocs} context={ctx}")
for lang in ("ja","en"):
    sc=sorted(scores[lang]); print(f"\n[{lang}] chars={chars[lang]} median score={sc[len(sc)//2]} p10={sc[len(sc)//10]}")
    for rule,n in stats[lang].most_common(): print(f"  {rule:22s} findings={n:6d}  per1k={n*1000/chars[lang]:6.2f}  docs={docs_hit[lang][rule]}/{ndocs}")
print(f"\n[fidelity EN→JA human pairs] docs with any high finding: {fid_docs}/{ndocs}")
for k,v in fidc.most_common(): print(f"  {k:30s} docs={v}")
