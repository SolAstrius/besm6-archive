# Rebuild everything from the published volume images:
#   make            fetch images, build dispak, run the 1988 print jobs, make facsimile and LaTeX PDFs
#   make listings   only the line-printer listings (docs/4023/*.lst)
DISPAK_REPO   = https://github.com/besm6/dispak
DISPAK_COMMIT = f21ea8780dad397b436151f2328ead4f8e617494
TECTONIC     ?= $(if $(wildcard build/bin/tectonic),$(CURDIR)/build/bin/tectonic,tectonic)
UV           ?= uv
DOCS          = 130528:ИЫ.00110-01_28_01_Технические_условия \
                130551:ИЫ.00110-01_51_01_Порядок_и_методика_испытаний \
                130530:ИЫ.00110-01_30_01_Формуляр

all: listings facsimile latex

disks/.ok:
	tools/fetch_disks.sh && touch $@

build/dispak-src:
	git clone -q $(DISPAK_REPO) $@ && git -C $@ checkout -q $(DISPAK_COMMIT)

build/dispak/dispak/dispak: build/dispak-src
	cmake -S build/dispak-src -B build/dispak -DCMAKE_BUILD_TYPE=Release >/dev/null
	$(MAKE) -C build/dispak dispak 2099 >/dev/null
	ln -sf ../build/dispak/dispak/2099 volumes/2099

listings: disks/.ok build/dispak/dispak/dispak
	python3 tools/tape4023_docs.py docs/4023
	cd docs/4023 && python3 ../../tools/index_printouts.py > INDEX.md

facsimile:
	mkdir -p docs/4023/facsimile
	for d in $(DOCS); do c=$${d%%:*}; n=$${d#*:}; \
	  $(UV) run -q --with fpdf2 python tools/facsimile.py docs/4023/$$c.lst docs/4023/facsimile/$$n.pdf "$$n"; done

latex:
	mkdir -p docs/4023/tex docs/4023/modern
	for d in $(DOCS); do c=$${d%%:*}; n=$${d#*:}; \
	  python3 tools/latexify.py docs/4023/$$c.lst docs/4023/tex/$$n.tex && \
	  (cd docs/4023/tex && $(TECTONIC) -X compile --outdir ../modern $$n.tex); done

.PHONY: all listings facsimile latex
