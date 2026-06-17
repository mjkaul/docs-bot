#!/usr/bin/env bash
# Sparse-checkout a subset of kubernetes/website docs (CC-BY 4.0) into content/raw/.
# Subset chosen to exercise the knowledge graph: concepts (semantic backbone),
# tasks (procedural topics linking to concepts), glossary (controlled vocabulary).
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
RAW_DIR="$REPO_ROOT/content/raw"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

SUBSET=(
  content/en/docs/concepts/overview
  content/en/docs/concepts/workloads
  content/en/docs/concepts/services-networking
  content/en/docs/tasks/run-application
  content/en/docs/reference/glossary
)

echo ">> Sparse-cloning kubernetes/website (blobless, depth 1)..."
git clone --filter=blob:none --depth 1 --sparse \
  https://github.com/kubernetes/website.git "$WORK/website"
git -C "$WORK/website" sparse-checkout set "${SUBSET[@]}"

echo ">> Copying markdown into $RAW_DIR ..."
rm -rf "$RAW_DIR"; mkdir -p "$RAW_DIR"
for path in "${SUBSET[@]}"; do
  rel="${path#content/en/docs/}"
  (cd "$WORK/website/$path" && find . -name '*.md' | while read -r f; do
    mkdir -p "$RAW_DIR/$rel/$(dirname "$f")"
    cp "$f" "$RAW_DIR/$rel/$f"
  done)
done

COUNT=$(find "$RAW_DIR" -name '*.md' | wc -l)
echo ">> Done: $COUNT markdown files in content/raw/ (CC-BY 4.0, The Kubernetes Authors)"
