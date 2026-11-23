# SPDX-License-Identifier: Apache-2.0
"""СИПРОД line-printer listings (dispak output): framed ЕСПД sheets and their text."""
import re

BORDER = re.compile(r"^\.-{20,}\.$")

def sheets(text):
    """Framed sheets, each a list of lines from one '.---.' border to the next (inclusive)."""
    out, cur = [], None
    for line in text.lstrip("﻿").split("\n"):
        line = line.rstrip()
        if BORDER.match(line):
            if cur is None:
                cur = [line]
            else:
                cur.append(line)
                out.append(cur)
                cur = None
        elif cur is not None:
            cur.append(line)
    return out

def inner(sheet):
    """Text lines of a sheet with the frame removed; the formatter's interleaved blank lines are kept as ''."""
    out = []
    for line in sheet[1:-1]:
        s = line[1:] if line.startswith("I") else line
        s = s[:-1] if s.endswith("I") and len(s) > 80 else s
        out.append(s.rstrip())
    return out
