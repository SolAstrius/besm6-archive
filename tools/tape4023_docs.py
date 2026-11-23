# SPDX-License-Identifier: Apache-2.0
"""Rebuild and run the documentation-printing jobs of tape 4023 under dispak.
Each job (passport ШИФР 1305xx, ЛЕНТ 31(СИПРОД)) is a Монитор-80 Fortran run of the СИПРОД formatter with the
document source inline. СИПРОД is mounted from volume 2248, zones 2702-2731, as ЛЕНТ 31(2248-2702); the
installation's own monitor variant ЗСХ is replaced by dispak's Монитор-80 (ЗС5), and 2048 is mounted as tape 41.
   tape4023_docs.py OUTDIR"""
import os, re, subprocess, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import besm6vol as b

H = str.maketrans("ABCEHKMOPTXY", "АВСЕНКМОРТХУ")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def decks():
    """[(job code, card index, cards)] for every complete formatting job (header to its *END FILE)."""
    text = "".join(b.koi7_lines(w) for z, s, w in b.zones(os.path.join(ROOT, "disks/tape23.bin")))
    cs = b.cards(text)
    T = [c.translate(H) for c in cs]
    for i, t in enumerate(T):                 # a header glued to the end of the previous record
        k = t.find("ШИФР 1305")
        if k > 0:
            cs[i], T[i] = cs[i][k:], t[k:]
    head = lambda i: re.match(r"ШИФР (1305\d\d)", T[i]) and any("31(СИПРОД)" in x for x in T[i:i + 8])
    starts = [i for i in range(len(T)) if head(i)]
    out = []
    for n, i in enumerate(starts):
        stop = starts[n + 1] if n + 1 < len(starts) else len(T)
        j = next((k for k in range(i + 1, stop) if T[k].strip().startswith("*ЕND FILЕ")), None)
        if j is not None:
            out.append((re.match(r"ШИФР (1305\d\d)", T[i]).group(1), i, cs[i:j + 1]))
        else:
            print("incomplete deck", T[i][:30], "at card", i)
    return out

def job(cards):
    d = list(cards)
    d[0] = re.sub(r"(ШИФ[РP] \d+)\s*З\S+", r"\1 ЗС5", d[0].translate(H))
    d = [x.replace("31(CИПPOД)", "31(2248-2702)").replace("31(СИПРОД)", "31(2248-2702)") for x in d]
    k = next(n for n, x in enumerate(d) if "31(2248-2702)" in x)
    d.insert(k + 1, "ЛЕН 41(2048)^")
    return "\n".join(d + ["``````", "ЕКОНЕЦ"]) + "\n"

if __name__ == "__main__":
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    env = dict(os.environ, BESM6_PATH=os.path.join(ROOT, "volumes"))
    exe = os.path.join(ROOT, "build/dispak/dispak/dispak")
    seen = {}
    for code, pos, cards in decks():
        seen[code] = seen.get(code, 0) + 1
        name = f"{code}" + (f"-{seen[code]}" if seen[code] > 1 else "")
        src = os.path.join(out, name + ".b6")
        open(src, "w").write(job(cards))
        r = subprocess.run([exe, src], capture_output=True, text=True, env=env, timeout=900)
        open(os.path.join(out, name + ".lst"), "w").write(r.stdout)
        title = [l.strip(" I") for l in r.stdout.split("\n") if re.search(r"ИЫ\.\d{5}-\d\d \d\d \d\d", l)][:1]
        print(name, len(cards), "cards ->", r.stdout.count("\n"), "lines", (r.stderr.strip()[:60] or ""), title)
