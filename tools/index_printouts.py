# SPDX-License-Identifier: Apache-2.0
"""Markdown index of the printouts in the current directory: document number, title, numbered pages, duplicates."""
import glob, hashlib, re

print("| listing | document | title | numbered pages | same as |\n|---|---|---|---|---|")
seen = {}
for f in sorted(glob.glob("*.lst")):
    t = open(f, encoding="utf-8").read()
    L = [l.strip(" I") for l in t.split("\n")]
    i = next((k for k, l in enumerate(L) if "ОБЩЕЕ СИСТЕМНОЕ ПРОГРАММНОЕ ОБЕСПЕЧЕНИЕ" in l), None)
    title = []
    if i is not None:
        for l in L[i + 1:i + 20]:
            if re.search(r"ЛИСТ УТВЕРЖДЕНИЯ|ИЫ\.\d{5}", l):
                break
            if l.strip():
                title.append(l.strip())
    num = re.search(r"ИЫ\.\d{5}-\d\d \d\d \d\d", t)
    pages = len(re.findall(r"^I\s+-\s+\d+\s+-\s+I", t, re.M))
    h = hashlib.md5(re.sub(r"\d\d\.\d\d\.\d\d М1", "", t).encode()).hexdigest()
    dup = seen.setdefault(h, f)
    print(f"| {f} | {num.group(0) if num else ''} | {' / '.join(title)} | {pages} | {dup if dup != f else ''} |")
