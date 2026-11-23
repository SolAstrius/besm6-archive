# БЭСМ-6 / Эльбрус-1КБ volume images

Tools and findings from the published БЭСМ-6 disk and tape images
([besm6.github.io/download/disks](https://github.com/besm6/besm6.github.io/tree/master/download/disks)),
and the system-software documentation of the **Эльбрус-1КБ** (ИТМиВТ, 1988) printed again from tape 4023.

## Эльбрус-1КБ documentation (`docs/4023/`)

Tape 4023 holds the documentation of the Эльбрус-1КБ общее системное программное обеспечение (ИЫ.00110-01) as
complete print jobs: a Монитор-80 Fortran job that calls the formatter library СИПРОД (`ЛЕНТ 31(СИПРОД)`, dated
02.10.81) with the document source inline. СИПРОД survives on volume 2248 (zones 2702–2731), so the jobs run in
[dispak](https://github.com/besm6/dispak) as they were written, with three changes to the passport: tape 31 is
mounted as `31(2248-2702)`, volume 2048 as tape 41, and the installation's monitor variant ЗСХ is replaced by
Монитор-80 (ЗС5). All 18 jobs end with «КОНЕЦ ЗАДАЧИ».

| | |
|---|---|
| `*.b6` | the job decks as run |
| `*.lst` | the line-printer output: framed ЕСПД sheets, justified text, page numbers |
| `INDEX.md` | what each listing prints |
| `facsimile/` | PDF facsimiles: one printed sheet per A4 page, monospace, text selectable |
| `tex/`, `modern/` | LaTeX edition (XeLaTeX via Tectonic): sections, clauses and tables rebuilt, text recased |

Facsimile and LaTeX editions are made for the three documents not published elsewhere:

- **Технические условия**, ИЫ.00110-01 28 01 (22 sheets + approval sheet): the system software as a manufactured
  product under customer acceptance. Magnetic tape type В4502-12 (ГОСТ 20958-80), media at most 18 months old,
  copies made only from a duplicate, duplicates re-checked by checksum yearly, marking of copy/duplicate/original,
  seals, packaging ПЭ4.170.149-17, приёмо-сдаточные and type tests before the представитель заказчика, climatic
  conditions per ГОСТ 16325-76; four tapes МЛ1–МЛ4; about 600 thousand machine words.
- **Порядок и методика испытаний**, ИЫ.00110-01 51 01 (55 sheets): the acceptance test procedure, with the
  control tasks and dialogue transcripts.
- **Формуляр**, ИЫ.00110-01 30 01 (29 sheets): the product log book with its blank forms for acceptance, packing,
  periodic checksum checks, storage and changes.

The other listings print the description (13 01), programmer's and system programmer's guides (33 01, 34 01,
32 02), specification and list of operating documents (20 01) and the «Текст программы» approval sheets
(12 01–03); most of these are transcribed on the besm6 wiki.

Other material on tape 4023 (`notes/4023/`): the ДИСПАК change log 1989–1990, the Эльбрус-1КБ control task
«КЗАСС», a Russian catalogue of a scientific Fortran library with CERN Program Library numbering, output formats
of a multigroup neutron-transport code, and operator screens.

## Rebuilding

```sh
make listings     # fetch and verify the images, build dispak at a pinned commit, run the 18 jobs
make facsimile    # needs uv (fpdf2); font: Courier New, or FACSIMILE_FONT=/path/to/mono.ttf
make latex        # needs Tectonic and the ParaType PT Serif / PT Sans / PT Mono fonts
```

## Tools

- `tools/besm6vol.py`: volume images (zones of 1032 little-endian 64-bit words, four header zones first, 48-bit
  machine word) and text decoding: GOST 10859 bytes, KOI-7 bytes, 6-bit ТЕКСТ, and the compressed KOI-7 card
  text of the 1988–90 tapes (`0x80+n` = n spaces, LF between records).
- `tools/tape4023_docs.py`: finds the СИПРОД print jobs on tape 4023, rebuilds and runs them.
- `tools/printout.py`, `tools/facsimile.py`, `tools/latexify.py`, `tools/index_printouts.py`: listings to PDF and
  LaTeX.
- `tools/fetch_disks.sh`: the images with SHA-256 checks, linked into `volumes/` by volume number.
- `index/zones.tsv`, `index/strings.tsv`: every zone of every image classified, and its word-like strings.

## Licence

The tools are Apache-2.0 (`LICENSE.txt`, `NOTICE`). The documents in `docs/4023/` are ИТМиВТ's; see `NOTICE`.
