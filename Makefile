# docs_bot Makefile
#
# Pipeline targets (run in order for a full build):
#   make scrape   → pull Kubernetes docs into content/raw/
#   make enrich   → classify and tag into content/enriched/
#   make graph    → compile enriched docs into graph/docs_graph.ttl (RDF)
#   make publish  → push enriched docs to Confluence (needs .env)
#
# ABI / Naas integration targets (run once after cloning ABI):
#   make abi-install  → symlink the docsbot module into the ABI repo
#   make abi-load     → push docs_graph.ttl into ABI's Oxigraph triple store
#
# ABI_DIR must point to your local clone of jupyter-naas/abi.
# Set it in your shell or pass it on the command line:
#   make abi-install ABI_DIR=../abi

ABI_DIR ?= ../abi

.PHONY: all scrape scrape-k8s scrape-ray enrich graph publish dry-run chat install abi-install abi-load

# Default: rebuild the full docs pipeline (no publish, no ABI).
all: scrape enrich graph

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------

install:
	pip install -r requirements.txt

# ---------------------------------------------------------------------------
# Docs pipeline
# ---------------------------------------------------------------------------

scrape: scrape-ray

scrape-ray:
	bash scripts/scrape_ray_docs.sh

scrape-k8s:
	bash scripts/scrape_k8s_docs.sh

enrich:
	python3 scripts/enrich_metadata.py

graph:
	python3 scripts/build_graph.py

dry-run:
	python3 scripts/publish_confluence.py --dry-run

publish:
	python3 scripts/publish_confluence.py

# chat: launch the DocsBot agent in interactive REPL mode.
# Pass a question directly: make chat Q="Which tasks mention statefulset?"
chat:
	@if [ -n "$(Q)" ]; then \
		python3 docsbot.py "$(Q)"; \
	else \
		python3 docsbot.py; \
	fi

# ---------------------------------------------------------------------------
# ABI integration
# ---------------------------------------------------------------------------

# abi-install: symlink the docsbot Python package into the ABI repo root so
# that `import docsbot` works inside ABI's virtual environment.
#
# We use a symlink rather than a copy so edits to abi_module/docsbot/ here
# are immediately reflected inside ABI — no re-install needed.
#
# After running this target you must also add the docsbot module entry to
# $(ABI_DIR)/config.yaml (see README.md for the exact YAML snippet).
abi-install:
	@if [ ! -d "$(ABI_DIR)" ]; then \
		echo "ERROR: ABI_DIR=$(ABI_DIR) does not exist."; \
		echo "Clone https://github.com/jupyter-naas/abi there first, or set ABI_DIR."; \
		exit 1; \
	fi
	@# Remove a stale symlink before (re)creating — ln -sf on a directory
	@# creates a link-inside-the-target on macOS, so we remove first.
	rm -f "$(ABI_DIR)/docsbot"
	ln -s "$(CURDIR)/abi_module/docsbot" "$(ABI_DIR)/docsbot"
	@echo "✅ Symlinked abi_module/docsbot → $(ABI_DIR)/docsbot"
	@echo ""
	@echo "Next steps:"
	@echo "  1. Add the docsbot entry to $(ABI_DIR)/config.yaml  (see README.md)"
	@echo "  2. Start ABI:  cd $(ABI_DIR) && make dev"
	@echo "  3. Load the graph:  make abi-load ABI_DIR=$(ABI_DIR)"

# abi-load: push the compiled RDF graph into ABI's running Oxigraph instance.
#
# Requires:
#   - ABI to be running (make dev in the ABI repo)
#   - graph/docs_graph.ttl to exist (make graph)
#   - the docsbot module installed (make abi-install)
#
# The script runs inside ABI's virtual environment so it can import naas_abi_core.
abi-load:
	@if [ ! -f "graph/docs_graph.ttl" ]; then \
		echo "ERROR: graph/docs_graph.ttl not found. Run 'make graph' first."; \
		exit 1; \
	fi
	@if [ ! -d "$(ABI_DIR)" ]; then \
		echo "ERROR: ABI_DIR=$(ABI_DIR) does not exist."; \
		exit 1; \
	fi
	@echo "Loading graph/docs_graph.ttl into ABI's triple store..."
	cd "$(ABI_DIR)" && uv run python -m docsbot.pipelines.LoadGraphPipeline
