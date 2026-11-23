# SPDX-License-Identifier: Apache-2.0
"""Modern LaTeX edition of a СИПРОД printout: the ЕСПД structure (approval sheet, title, аннотация, numbered
sections and clauses, tables, change register) rebuilt from the line-printer layout, all-capitals text recased
with abbreviations and designations kept, formatter hyphenation undone, «» quotes, № and initials typeset.
   latexify.py LISTING.lst OUT.tex"""
import os, re, sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from printout import sheets, inner

KEEP = set("""ОСПО ВК ТУ ОТК МЛ МН КС ГОСТ ОС ЭВМ АЦПУ АЦД МД НМД НМЛ НМБ МБ ОП ОЗУ ЕС СМ БЭСМ ИТМ БЕМШ МВК ЛУ ПЭ
КЗ КТ ВУ ИР ПМ РК РМР ТР УУ АУ ГП НУ ВС ЛИТЕРА МАКРО ПЗУ ТТЛ ЭСЛ ЕСКД ЕСПД ОТД КП ППО ТЗ РП ИП ЦП ПВВ УВВ СВС
АРМ МКП АВОСТ ЭК ИЫ ЦЕРН ОИЯИ ИТМИВТ ВЦ ДВК ОИ ПК ЭК""".split())
NAMES = {"ДИСПАК": "Диспак", "ЭЛЬБРУС": "Эльбрус", "ДИМИП": "Димип", "ДОКЭБ": "ДОКЭБ", "ФОРТРАН": "Фортран",
         "АЛГОЛ": "Алгол", "ПАСКАЛЬ": "Паскаль", "АССЕМБЛЕР": "ассемблер", "АВТОКОД": "автокод",
         "РЕФАЛ": "Рефал", "ДУБНА": "Дубна", "БЕСМ": "БЭСМ"}
VOWELS = set("АЕЁИОУЫЭЮЯ")

def tex_escape(s):
    for a, b in (("\\", r"\textbackslash{}"), ("&", r"\&"), ("%", r"\%"), ("$", r"\$"), ("#", r"\#"),
                 ("_", r"\_"), ("{", r"\{"), ("}", r"\}"), ("^", r"\^{}"), ("~", r"\~{}")):
        s = s.replace(a, b)
    return s

def is_abbrev(w):
    if w in KEEP or any(c.isdigit() for c in w) or re.search(r"[A-Z]", w):
        return True
    letters = [c for c in w if c.isalpha()]
    return 1 < len(letters) <= 4 and sum(c in VOWELS for c in letters) == 0

def recase_word(w, cap):
    if not re.search(r"[А-ЯЁ]", w):
        return w
    core = re.sub(r"[^А-ЯЁA-Z0-9]", "", w)
    if core in NAMES:
        return w.replace(core, NAMES[core])
    if is_abbrev(core):
        return w
    # compound with hyphen: recase each part
    if "-" in w and not any(c.isdigit() for c in w):
        parts = w.split("-")
        return "-".join(recase_word(p, cap and i == 0) for i, p in enumerate(parts))
    low = w.lower()
    if cap:
        m = re.search(r"[а-яё]", low)
        if m:
            low = low[:m.start()] + low[m.start()].upper() + low[m.start() + 1:]
    return low

LAT = str.maketrans("АВСЕНКМОРТХУ", "ABCEHKMOPTXY")
PROT = "\x02"

def normalise(text):
    """Fixes on the uppercase source before recasing: spacing after commas, typewriter ’ for Ъ, units, Latin
    words typed with Cyrillic look-alikes."""
    text = re.sub(r",(?=[А-ЯЁA-Z])", ", ", text)
    text = re.sub(r"\s+([.,;:])(?=\s|$)", r"\1", text)
    text = re.sub(r"(?<![А-ЯЁ])СМ\.(?=\s)", PROT + "см." + PROT, text)
    text = re.sub(r"(?<![А-ЯЁ])П\.\s?(?=\d)", PROT + "п.~" + PROT, text)
    text = re.sub(r"(?<=[А-ЯЁ])’(?=[ЕЁЮЯ])", "Ъ", text)
    text = re.sub(r"\(\s*(\d+)\s*\+-\s*(\d+)\s*\)\s*О\s*С\b", PROT + r"(\1±\2)~°C" + PROT, text)
    text = re.sub(r"\(\s*(\d+)\s*\+-\s*(\d+)\s*\)", r"(\1±\2)", text)
    text = re.sub(r"\bГПА\b", PROT + "гПа" + PROT, text)
    def lat(m):
        w = m.group(0)
        if re.search(r"[A-Z]", w) and re.search(r"[А-ЯЁ]", w) and not re.search(r"[^A-ZАВСЕНКМОРТХУ0-9]", w):
            return w.translate(LAT)
        return w
    text = re.sub(r"[A-ZА-ЯЁ0-9]+", lat, text)
    return text

def recase(text, start=True):
    """Sentence case for all-capitals Russian; abbreviations, designations and Latin words are kept."""
    text = normalise(text)
    text = re.sub(r"\b([А-ЯЁ])\.\s?([А-ЯЁ])\.\s?([А-ЯЁ]{2,})", lambda m: f"{m[1]}.~{m[2]}.~{m[3][0]}{m[3][1:].lower()}", text)
    out, cap = [], start
    for tok in re.split(r"(\s+)", text):
        if not tok or tok.isspace():
            out.append(tok); continue
        if "~" in tok and re.match(r"[А-ЯЁ]\.~", tok):
            out.append(tok); cap = False; continue
        if PROT in tok:
            out.append(tok.replace(PROT, "")); cap = False; continue
        out.append(recase_word(tok, cap or tok.startswith(('"', "("))) if tok.startswith('"') else recase_word(tok, cap))
        stripped = tok.rstrip("»\"')")
        if stripped.endswith((".", "!", "?")) and not re.search(r"\b[А-ЯЁ]\.$", stripped) \
                and not re.match(r"^(\d+\.)+$", stripped) and not stripped.endswith(("Т.Е.", "Т.Д.", "Т.П.", "СМ.", "ТАБЛ.")):
            cap = True
        elif re.match(r"^(\d+\.)+$", tok) or re.match(r"^[А-Я]\)$|^\d+\)$", tok) or tok in ("-", "--"):
            cap = True
        else:
            cap = False
    return "".join(out)

def typography(s):
    out = []
    for i, c in enumerate(s):
        if c == '"':
            prev = s[i - 1] if i else " "
            out.append("«" if prev.isspace() or prev in "(«[" else "»")
        else:
            out.append(c)
    s = "".join(out)
    s = re.sub(r"\bN\s?(\d)", "№\x01\\1", s)
    s = re.sub(r"\s+-\s+", " --- ", s)
    s = re.sub(r"\s+", " ", s)
    return s

def make_tex(text, start=True):
    t = tex_escape(typography(recase(text, start)))
    return t.replace(r"\~{}", "~").replace("\x01", "\\,")

# ---------------------------------------------------------------------------------------------------------------

def dehyphen(lines, vocab):
    """Join lines of one paragraph; a line-final hyphen is the formatter's unless the hyphenated compound appears
    unbroken elsewhere or both halves are long words."""
    out = ""
    for line in lines:
        line = line.strip()
        if out.endswith("-") and line:
            a = re.search(r"([А-ЯЁA-Z]+)-$", out)
            b = re.match(r"([А-ЯЁA-Z]+)", line)
            if a and b:
                joined, comp = a[1] + b[1], a[1] + "-" + b[1]
                if vocab[comp] or (not vocab[joined] and len(a[1]) >= 5 and len(b[1]) >= 5):
                    out += line
                else:
                    out = out[:-1] + line
                continue
        out = (out + " " + line) if out else line
    return out

TABLE_RULE = re.compile(r"^\s*-{6,}[-I ]*$")

def blocks(body):
    """Group body lines (blank interleave removed) into ('par'|'head'|'table'|'center'|'item', lines, indent)."""
    lines = [l for l in body if l.strip()]
    if not lines:
        return []
    ind = lambda l: len(l) - len(l.lstrip())
    margin = Counter(ind(l) for l in lines if len(l.strip()) > 50).most_common(1)
    margin = margin[0][0] if margin else 14
    out, i = [], 0
    while i < len(lines):
        l = lines[i]
        s = l.strip()
        if re.match(r"^\s*-{3,}(\s+-{3,})*\s*$", l) and "I" not in l and len(s) < 60:
            j = i + 1
            while j < len(lines):
                t = lines[j].strip()
                if re.match(r"^((\d+\.)+)\s", t) or len(lines[j].rstrip()) >= 74 or t.startswith("("):
                    break
                if not (re.match(r"^-{3,}(\s+-{3,})*$", t) or re.search(r"\S\s{5,}\S", t) or len(t) < 50):
                    break
                j += 1
            out.append(("pre", lines[i:j], margin)); i = j; continue
        if TABLE_RULE.match(l) or (l.count("I") >= 2 and "  I" in l):
            j = i
            while j < len(lines) and (TABLE_RULE.match(lines[j]) or lines[j].count("I") >= 1 and " I" in lines[j]
                                      or (j > i and not lines[j].strip())):
                j += 1
            out.append(("table", lines[i:j], margin)); i = j; continue
        num = re.match(r"^((\d+\.)+)\s+(.*)$", s)
        nxt = lines[i + 1] if i + 1 < len(lines) else ""
        cont = nxt and ind(nxt) == margin and not re.match(r"^((\d+\.)+)\s", nxt.strip())
        if num and num[1].count(".") <= 2 and not cont and len(s) < 70 and not s.endswith((",", ";", ":")):
            out.append(("head", [s], num[1].count("."))); i += 1; continue
        if ind(l) > margin + 8 and len(s) < 60 and not cont and s.upper() == s:
            out.append(("center", [s], ind(l))); i += 1; continue
        # paragraph: first line, then continuation lines at the margin
        j = i + 1
        while j < len(lines) and ind(lines[j]) == margin and not TABLE_RULE.match(lines[j]) \
                and not (lines[j].count("I") >= 2 and "  I" in lines[j]):
            j += 1
        kind = "item" if re.match(r"^(-|\d+\)|[А-Я]\))\s", s) else "par"
        if kind == "par" and ind(l) <= margin and out and out[-1][0] in ("par", "item"):
            out[-1] = (out[-1][0], out[-1][1] + lines[i:j], out[-1][2])     # continuation across a page or a mis-split
        else:
            out.append((kind, lines[i:j], ind(l)))
        i = j
    return out

def pre_tex(lines):
    """Column-aligned block kept as monospace, text recased and spacing kept. In a table the I bars become │ and
    cells are recased separately: a cell starts capitalised only on the block's first text line."""
    left = min(len(l) - len(l.lstrip()) for l in lines if l.strip())
    table = sum(1 for l in lines if l.count("I") >= 2) >= 2
    out, first = [], True
    for l in lines:
        t = l[left:].rstrip()
        if not t.strip():
            out.append(""); continue
        if table:
            parts = re.split(r"(I)", t)
            cells = []
            for part in parts:
                if part == "I":
                    cells.append("│")
                elif part.strip() and not re.fullmatch(r"[-\s]+", part):
                    cells.append(re.sub(r'"([^"]*)"', r"«\1»", recase(part, first)))
                else:
                    cells.append(part.replace("-", "─") if re.fullmatch(r"[-\s]+", part) and "-" in part else part)
            t = "".join(cells)
            if re.search(r"[А-ЯЁа-яё]", l):
                first = False
        else:
            t = re.sub(r'"([^"]*)"', r"«\1»", recase(t, True))
        out.append(t)
    return "\\begin{center}\\small\n\\begin{BVerbatim}\n" + "\n".join(out) + "\n\\end{BVerbatim}\n\\end{center}\n"

def table_tex(tlines, vocab):
    """Box table with I column bars and dashed row rules -> longtable; else a monospace block."""
    bars = Counter()
    for l in tlines:
        for m in re.finditer("I", l):
            bars[m.start()] += 1
    rows_with = sum(1 for l in tlines if "I" in l)
    cols = sorted(p for p, c in bars.items() if c >= max(2, rows_with * 0.6))
    sets = Counter(tuple(m.start() for m in re.finditer("I", l)) for l in tlines if "I" in l)
    dominant = sets.most_common(1)[0][1] if sets else 0
    if len(cols) < 1 or rows_with < 3 or dominant < rows_with * 0.6:
        return pre_tex(tlines)
    # a header whose bars are not the body's (spanning or split header cells) cannot be cut into the body columns
    rules = [k for k, l in enumerate(tlines) if TABLE_RULE.match(l)]
    head = tlines[:rules[1]] if len(rules) > 1 else []
    colset = set(cols)
    if any(not set(m.start() for m in re.finditer("I", l)) <= colset for l in head if "I" in l):
        return pre_tex(tlines)
    if any(c < len(l) and l[c] not in " I" for l in head if not TABLE_RULE.match(l) for c in cols):   # a header cell spans body columns
        return pre_tex(tlines)
    left = min(len(l) - len(l.lstrip()) for l in tlines if l.strip())
    edges = [left] + [c + 1 for c in cols]
    def cells(l):
        out, prev = [], left
        for c in cols:
            out.append(l[prev:c]); prev = c + 1
        out.append(l[prev:])
        return [x.strip() for x in out]
    groups, cur = [], []
    for l in tlines:
        if TABLE_RULE.match(l) or re.match(r"^[\s\-I]+$", l) and "--" in l:
            if cur:
                groups.append(cur); cur = []
        elif l.strip():
            c = [re.sub(r"-{3,}", "", x).strip() for x in cells(l)]
            if cur and re.match(r"^\d+\.\s", c[0]):
                groups.append(cur); cur = []
            cur.append(c)
    if cur:
        groups.append(cur)
    n = len(cols) + 1
    rows = []
    for g in groups:
        merged = []
        for k in range(n):
            merged.append(dehyphen([r[k] for r in g if k < len(r) and r[k]], vocab))
        if any(merged):
            rows.append(merged)
    if not rows:
        return ""
    right = max(len(l.rstrip()) for l in tlines)
    widths = [b - a for a, b in zip(edges, edges[1:] + [right + 1])]
    tot = sum(widths)
    spec = "|" + "|".join(f">{{\\raggedright\\arraybackslash\\hsize={n * w / tot:.3f}\\hsize}}X" for w in widths) + "|"
    out = ["\\begin{center}\\small\\begin{tabularx}{\\linewidth}{" + spec + "}\\hline"]
    for k, r in enumerate(rows):
        cellsx = [make_tex(c) if c else "" for c in r]
        if k == 0:
            cellsx = ["\\small\\bfseries\\hspace{0pt}" + c if c else "" for c in cellsx]
        out.append(" & ".join(cellsx) + r" \\ \hline")
    out.append("\\end{tabularx}\\end{center}\n")
    return "\n".join(out)

def approval(sheet):
    """Fields of the approval sheet (ЛУ) and the title sheet."""
    lines = [l.strip() for l in inner(sheet) if l.strip()]
    return lines

def build(lst):
    pages = sheets(open(lst, encoding="utf-8").read())
    vocab = Counter(w for p in pages for l in inner(p) for w in re.findall(r"[А-ЯЁA-Z]+(?:-[А-ЯЁA-Z]+)?", l))
    lu, title = approval(pages[0]), approval(pages[1])
    docno = next((l for l in title if re.match(r"ИЫ\.\d{5}-\d\d \d\d \d\d$", l)), "")
    sheets_n = next((l for l in title if l.startswith("ЛИСТОВ")), "")
    year = next((l for l in title if re.match(r"^19\d\d$", l)), "")
    names = [l for l in title if l not in (docno, sheets_n, year) and not l.startswith(("УТВЕРЖДЕН", "ИЫ.", "ЛИТЕРА"))]
    tex = []
    # ---- approval sheet
    agreed = [l for l in lu]
    def after(key, n=2):
        k = next((i for i, l in enumerate(lu) if l.startswith(key)), None)
        return lu[k + 1:k + 1 + n] if k is not None else []
    cust = [l for l in lu if "ЗАКАЗЧИКА" in l]
    tex.append(r"\begin{titlepage}\small")
    m = re.search(r"СОГЛАСОВАНО\s+УТВЕРЖДАЮ", " ".join(lu))
    left, right = [], []
    for l in lu[:6]:
        parts = re.split(r"\s{3,}", l)
        if len(parts) == 2:
            left.append(parts[0]); right.append(parts[1])
    tex.append(r"\noindent\begin{minipage}[t]{0.45\linewidth}" + r"\\".join(make_tex(x) for x in left) +
               r"\end{minipage}\hfill\begin{minipage}[t]{0.45\linewidth}\raggedleft " +
               r"\\".join(make_tex(x) for x in right) + r"\end{minipage}")
    tex.append(r"\vspace*{\fill}\begin{center}")
    for l in names:
        tex.append(r"{\large " + make_tex(l) + r"}\\[0.6em]")
    tex.append(r"\vspace{1em}{\large\bfseries " + tex_escape(docno) + r"}\\[0.4em]")
    tex.append(make_tex(sheets_n) + r"\end{center}\vspace*{\fill}")
    dev = lu[next((i for i, l in enumerate(lu) if "ПРЕДСТАВИТЕЛИ" in l), len(lu)):]
    devlines = [x for x in dev if not re.match(r"^(19\d\d|ЛИТЕРА.*)$", x)]
    if len(devlines) > 1 and devlines[0] == "ПРЕДСТАВИТЕЛИ":
        devlines[:2] = [devlines[0] + " " + devlines[1]]
    tex.append(r"\begin{flushright}\begin{tabular}{r}" + r"\\".join(make_tex(x) for x in devlines) +
               r"\end{tabular}\end{flushright}")
    tex.append(r"\begin{center}" + year + r"\end{center}\end{titlepage}")
    # ---- body: running heads removed per sheet, then one stream (paragraphs continue across sheets)
    stream, toc_at = [], None
    for p in pages[2:]:
        content = [l for l in inner(p) if l.strip()]
        while content and (re.match(r"^\s*-\s*\d+\s*-\s*$", content[0]) or
                           re.match(r"^\s*ИЫ\.\d{5}-\d\d \d\d \d\d\s*$", content[0])):
            content = content[1:]
        if any(l.strip() == "СОДЕРЖАНИЕ" for l in content[:3]):
            if toc_at is None:
                toc_at = len(stream)
            continue
        stream += content
    pending_toc = toc_at
    for kind, ls, x in blocks(stream):
        s = " ".join(l.strip() for l in ls)
        if pending_toc is not None and kind == "head":
            tex.append(r"\tableofcontents\clearpage"); pending_toc = None
        if kind == "head":
            num = re.match(r"^((\d+\.)+)\s+(.*)$", s)
            level = ["section", "subsection", "subsubsection"][min(x, 3) - 1]
            t = f"{tex_escape(num[1])}~{make_tex(num[3].rstrip('.'))}"
            tex.append(f"\\{level}*{{{t}}}\\addcontentsline{{toc}}{{{level}}}{{{t}}}")
        elif kind == "center":
            if re.match(r"^(ТАБЛИЦА|ПРОДОЛЖЕНИЕ ТАБЛ)", s):
                tex.append(r"\begin{flushright}\small " + make_tex(s) + r"\end{flushright}")
            elif s in ("АННОТАЦИЯ",) or s.startswith(("ПРИЛОЖЕНИЕ", "ПЕРЕЧЕНЬ", "ЛИСТ РЕГИСТРАЦИИ")):
                tex.append(f"\\section*{{{make_tex(s)}}}\\addcontentsline{{toc}}{{section}}{{{make_tex(s)}}}")
            else:
                tex.append(r"\begin{center}" + make_tex(s) + r"\end{center}")
        elif kind == "table":
            tex.append(table_tex(ls, vocab))
        elif kind == "pre":
            tex.append(pre_tex(ls))
        else:
            text = dehyphen(ls, vocab)
            num = re.match(r"^((\d+\.){2,})\s+(.*)$", text)
            if num:
                tex.append(f"\\par\\textbf{{{tex_escape(num[1])}}} {make_tex(num[3])}\\par")
            elif kind == "item":
                tex.append(r"\par\hangindent=1.5em " + make_tex(text) + r"\par")
            else:
                tex.append(make_tex(text) + "\n")
    return docno, names, "\n".join(tex)

PREAMBLE = r"""\documentclass[11pt,a4paper]{article}
\usepackage{fontspec}
\usepackage{polyglossia}
\setdefaultlanguage{russian}
\setmainfont{PT Serif}
\setsansfont{PT Sans}
\setmonofont{PT Mono}
\newfontfamily\cyrillicfont{PT Serif}
\newfontfamily\cyrillicfonttt{PT Mono}
\usepackage[margin=25mm]{geometry}
\usepackage{tabularx,longtable,fancyvrb}
\usepackage[hidelinks]{hyperref}
\setlength{\parindent}{1.25em}
\setlength{\emergencystretch}{3em}
\setlength{\parskip}{0.3em}
\renewcommand{\arraystretch}{1.25}
\hypersetup{pdftitle={%s},pdfsubject={%s}}
\begin{document}
"""

if __name__ == "__main__":
    docno, names, body = build(sys.argv[1])
    title = " ".join(names)
    open(sys.argv[2], "w").write(PREAMBLE % (tex_escape(docno), tex_escape(title)) + body + "\n\\end{document}\n")
    print(sys.argv[2], docno, title)
