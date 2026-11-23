# SPDX-License-Identifier: Apache-2.0
"""БЭСМ-6 volume images (SIMH/dispak format) and text decoding.
A volume file is a run of zones of 1032 64-bit little-endian words (four header zones first); the first 8 words of a zone are service words,
then 1024 data words. A machine word is the low 48 bits (bits 49-50 are the convolution).
Text forms decoded: GOST 10859 bytes (6 per word), KOI-7 bytes (6 per word), 6-bit ТЕКСТ (8 per word)."""
import os, re, struct

# GOST 10859 code points 000-177 (as Unicode; '\0' = no character) and the 6-bit ТЕКСТ code -> GOST mapping.
GOST = '0123456789+-/,. ⏨↑()×=;[]*‘’≠<>:АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЫЬЭЮЯDFGIJLNQRSUVWZ‾⩽⩾∨∧⊃¬÷≡%◇|―_!"Ъ°′\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00␤\\\x00\x00'
T2G = [15, 14, 33, 54, 36, 52, 35, 40, 18, 19, 25, 41, 43, 62, 38, 12, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 59, 13, 47, 11, 10, 58, 39, 32, 34, 49, 63, 37, 64, 65, 45, 66, 67, 42, 68, 44, 69, 46, 48, 70, 71, 72, 50, 73, 74, 75, 53, 51, 76, 56, 60, 57, 55, 61]
G2U = [ord(c) for c in GOST]

KOI7 = "юабцдефгхийклмнопярстужвьызшэщчъ"

def gost_char(c):
    u = G2U[c] if c < len(G2U) else 0
    return chr(u) if u else None

def koi7_char(c):
    c &= 0x7F
    if 0x60 <= c <= 0x7F:
        return KOI7[c - 0x60].upper() if c != 0x7F else "Ъ"
    if 32 <= c < 0x60:
        return chr(c)
    return None

def zones(path):
    """Logical zones: physical zone n+4 (the first four are a header), little-endian 64-bit words (as dispak's
    volume tools read them)."""
    d = open(path, "rb").read()
    zs = 1032 * 8
    for z in range(len(d) // zs - 4):
        raw = d[(z + 4) * zs:(z + 5) * zs]
        words = [int.from_bytes(raw[i:i + 8], "little") & ((1 << 48) - 1) for i in range(64, zs, 8)]
        yield z, raw[:64], words

def word_bytes(words):
    return b"".join(w.to_bytes(6, "big") for w in words)

def decode(words, form):
    if form == "text":
        out = []
        for w in words:
            for s in range(42, -1, -6):
                out.append(gost_char(T2G[(w >> s) & 63]) or "\0")
        return "".join(out)
    b = word_bytes(words)
    f = gost_char if form == "gost" else koi7_char
    return "".join((f(c) or "\0") if form != "gost" or c != 0o214 else "\n" for c in b)

def score(s):
    """Share of characters in printable runs of 6+ that contain letters."""
    runs = re.findall(r"[^\0]{6,}", s)
    good = sum(len(r) for r in runs if sum(ch.isalpha() for ch in r) >= len(r) // 3)
    return good / max(1, len(s))

VOW = set("АЕИОУЫЭЮЯAEIOUY")
def wordiness(s):
    """Share of characters in plausible words (3+ letters, 20-75% vowels), times a spacing check."""
    if not s:
        return 0.0
    toks = re.findall(r"[A-Za-zА-Яа-яЁё]{3,}", s)
    good = sum(len(t) for t in toks if 0.2 <= sum(c.upper() in VOW for c in t) / len(t) <= 0.75)
    sp = s.count(" ") / len(s)
    return good / len(s) * (1.0 if 0.04 <= sp <= 0.6 else 0.3)

def best(words):
    out = []
    for f in ("gost", "koi7", "text"):
        s = decode(words, f)
        out.append((wordiness(s), f, s))
    return max(out)

def survey(path):
    rows = []
    for z, svc, w in zones(path):
        nz = sum(1 for x in w if x)
        if nz == 0:
            rows.append((z, "zero", 0.0, "")); continue
        if len(set(w)) <= 2:
            rows.append((z, "fill", 0.0, oct(w[0]))); continue
        sc, f, s = best(w)
        snippet = re.sub(r"\s+", " ", s.replace("\0", " ")).strip()
        rows.append((z, f if sc > 0.25 else "bin", round(sc, 2), snippet[:160] if sc > 0.25 else ""))
    return rows

def strings(words, minlen=10):
    """Word-like runs in each encoding: [(form, text)]."""
    out = []
    for f in ("gost", "koi7", "text"):
        s = decode(words, f)
        seps = "\0" if f != "text" else "\0"
        for r in re.split(r"\0+", s) if f != "text" else re.split(r"(?:[^А-ЯA-Z0-9 .,()*/:;=+\-]){1,}", s):
            r = re.sub(r"\s+", " ", r).strip()
            if len(r) >= minlen and wordiness(r) >= 0.55 and len(set(r)) > 5:
                out.append((f, r))
    return out

def koi7_lines(words):
    """KOI-7 card text as written by the ДИСПАК-era tools: a byte 0x80+n is a run of n spaces (cards are padded to
    80 columns this way), LF ends a record, NUL is padding."""
    out = []
    for c in word_bytes(words):
        if c == 0:
            continue
        if c == 10:
            out.append("\n")
        elif c >= 0x80:
            out.append(" " * (c - 0x80))
        else:
            ch = koi7_char(c)
            out.append(ch if ch else "")
    return "".join(out)

def cards(text):
    """Card images from koi7_lines text: short whitespace-only records are separators between cards and are dropped;
    a blank card (padded to 80 columns) is kept as an empty line."""
    out = []
    for line in text.split("\n"):
        if not line.strip() and len(line) < 40:
            continue
        out.append(line.rstrip())
    return out
