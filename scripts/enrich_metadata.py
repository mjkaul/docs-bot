#!/usr/bin/env python3
"""Enrich raw Ray docs with graph-ready metadata (Iantosca step 2).

Reads content/raw/ (.md and .rst), writes content/enriched/ (.md) with:
  - topic_type  : concept / task / reference / section / glossary_term
  - stable id   : derived from section + file path
  - subjects    : primary subject from section path + inherited from mentioned terms
  - mentions    : glossary term ids found by text search (not shortcodes — Ray has none)
  - references  : internal docs links extracted from Markdown relative hrefs
  - cleaned body: RST/MyST directives stripped, inline roles converted to plain text

K8s vs Ray differences handled here:
  - K8s: Hugo frontmatter supplies title + type; tooltip shortcodes mark mentions.
  - Ray: No frontmatter → title extracted from first RST/MD heading.
         No shortcodes → mentions found by scanning body text for glossary patterns.
         Mixed .rst/.md → both parsed, output normalised to .md.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Optional

import yaml

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "content" / "raw"
ENRICHED = ROOT / "content" / "enriched"
TAXONOMY = ROOT / "taxonomy" / "taxonomy.yaml"
GLOSSARY = ROOT / "taxonomy" / "glossary.yaml"

# ---------------------------------------------------------------------------
# RST / MyST cleaning patterns
# ---------------------------------------------------------------------------

# RST section adornment lines: three or more repeated special characters alone
# on a line.  These are title underlines/overlines — not content.
# e.g. "=========" or "--------"
RST_ADORNMENT_RE = re.compile(r"^[=\-~^\"'`#*+_!]{3,}\s*$")

# RST reference labels: ".. _label-name:" on its own line
RST_LABEL_RE = re.compile(r"^\.\.\s+_[^:]+:\s*$")

# MyST reference labels: "(label)=" on its own line
MYST_LABEL_RE = re.compile(r"^\([a-zA-Z0-9_-]+\)=\s*$")

# RST inline roles: :role:`text` or :role:`display text <target>`
# Covers :ref:, :doc:, :class:, :func:, :meth:, :attr:, :mod:, :obj:, etc.
RST_ROLE_RE = re.compile(
    r":(?:ref|doc|class|func|meth|attr|mod|data|exc|obj|type"
    r"|py:\w+|option|term|envvar|program):"
    r"`(?:([^`<]+?)\s*<[^>]+>|([^`]+))`"
)

# RST double-backtick inline code: ``code`` → `code`
RST_DBL_BACKTICK_RE = re.compile(r"``([^`]+)``")

# MyST inline roles: {role}`text` or {role}`display <target>`
MYST_ROLE_RE = re.compile(
    r"\{(?:ref|doc|class|func|meth|attr)\}`(?:([^`<]+?)\s*<[^>]+>|([^`]+))`"
)

# Admonition directives whose body we want to keep as a blockquote.
# RST: ".. note::\n   body text"
RST_ADMONITION_RE = re.compile(
    r"\.\.\s+(note|tip|warning|important|caution|attention)::\s*\n"
    r"((?:[ \t]+[^\n]*\n?)*)",
    re.MULTILINE,
)

# MyST admonitions: ":::{note}\n...\n:::"
MYST_ADMONITION_RE = re.compile(
    r":::\{(note|tip|warning|important)\}(.*?):::",
    re.DOTALL,
)

# RST code blocks: ".. code-block:: python\n   <indented code>"
# Also matches testcode, doctest, highlight.
RST_CODE_RE = re.compile(
    r"\.\.\s+(?:code-block|code|testcode|doctest|highlight)::[^\n]*\n"
    r"((?:[ \t]+[^\n]*\n?)*)",
    re.MULTILINE,
)

# RST testoutput and similar blocks to strip entirely
RST_TESTOUTPUT_RE = re.compile(
    r"\.\.\s+testoutput::[^\n]*\n(?:[ \t]+[^\n]*\n?)*",
    re.MULTILINE,
)

# RST directives whose entire block (directive + body) should be removed.
# These are either auto-generated content or layout directives with no prose value.
RST_STRIP_BLOCK_RE = re.compile(
    r"\.\.\s+(?:"
    r"toctree|autosummary|literalinclude|image|figure|"
    r"currentmodule|autoclass|autofunction|automodule|"
    r"versionadded|versionchanged|deprecated|"
    r"tab-set|tab-item"
    r")::[^\n]*\n(?:[ \t]+[^\n]*\n?)*",
    re.MULTILINE,
)

# Remaining bare ".. directive::" lines and ".. " comments not caught above
RST_BARE_DIRECTIVE_RE = re.compile(r"^\.\.[^\n]*$", re.MULTILINE)

# Relative Markdown links pointing to other docs pages.
# Captures the href for normalization into a canonical path.
MD_LINK_RE = re.compile(r"\[(?:[^\]]*)\]\(((?:\.\.?/)[^)#\s]+)\)")


# ---------------------------------------------------------------------------
# Title extraction
# ---------------------------------------------------------------------------

def extract_title_rst(text: str) -> str:
    """
    Return the document title from an RST file.

    RST uses adornment characters (=, -, ~, etc.) as underlines (and optionally
    overlines) to mark headings.  The document title is the first heading at the
    highest level — typically the one using '=' underlines.

    Two forms:
      Underline only:   Title text         Overline + underline:  ========
                        ===========                                Title text
                                                                   ========
    """
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Skip blank lines, reference labels, and comment lines
        if (not stripped
                or RST_LABEL_RE.match(stripped)
                or stripped.startswith(".. ")):
            i += 1
            continue

        # Overline + underline: current line is all adornment chars
        if RST_ADORNMENT_RE.match(stripped) and i + 2 < len(lines):
            candidate = lines[i + 1].strip()
            if candidate and RST_ADORNMENT_RE.match(lines[i + 2].strip()):
                return candidate

        # Underline only: next line is all adornment chars
        if i + 1 < len(lines) and RST_ADORNMENT_RE.match(lines[i + 1].strip()):
            if stripped:
                return stripped

        i += 1
    return ""


def extract_title_md(text: str) -> str:
    """
    Return the document title from a Markdown / MyST file.

    Looks for the first '# Heading' line, skipping MyST reference labels
    ('(label)=') and blank lines that precede it.
    """
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or MYST_LABEL_RE.match(stripped):
            continue
        if stripped.startswith("# "):
            return stripped[2:].strip()
        # First non-blank, non-label line that isn't an h1 — give up
        break
    return ""


# ---------------------------------------------------------------------------
# Body cleaning
# ---------------------------------------------------------------------------

def _dedent_block(text: str) -> str:
    """Remove the common leading whitespace from an indented block."""
    lines = [l for l in text.splitlines() if l.strip()]
    if not lines:
        return text
    indent = min(len(l) - len(l.lstrip()) for l in lines)
    return "\n".join(l[indent:] for l in text.splitlines())


def clean_rst_body(text: str) -> str:
    """
    Convert RST markup to approximate plain-text / Markdown.

    Not a full RST parser — pragmatically strips the patterns that appear most
    often in the Ray docs corpus.  The result won't be perfect Markdown but it
    will be readable and suitable for term-mention scanning and Confluence publishing.
    """
    # 1. Strip directives that carry no prose (toctree, autosummary, image, etc.)
    text = RST_STRIP_BLOCK_RE.sub("", text)

    # 2. Strip testoutput blocks
    text = RST_TESTOUTPUT_RE.sub("", text)

    # 3. Convert admonition blocks to blockquotes so prose is preserved
    def admonition_sub(m: re.Match) -> str:
        label = m.group(1).title()
        body = _dedent_block(m.group(2)).strip()
        return f"\n> **{label}:** {body}\n"
    text = RST_ADMONITION_RE.sub(admonition_sub, text)

    # 4. Convert code blocks to Markdown fences
    def code_sub(m: re.Match) -> str:
        body = _dedent_block(m.group(1)).strip()
        return f"\n```\n{body}\n```\n" if body else ""
    text = RST_CODE_RE.sub(code_sub, text)

    # 5. Strip remaining bare directive lines (.. comment, .. TODO:, etc.)
    text = RST_BARE_DIRECTIVE_RE.sub("", text)

    # 6. Strip reference labels
    text = re.sub(RST_LABEL_RE.pattern, "", text, flags=re.MULTILINE)

    # 7. Strip adornment lines (section underlines / overlines)
    text = re.sub(RST_ADORNMENT_RE.pattern, "", text, flags=re.MULTILINE)

    # 8. Convert inline roles to plain text: :ref:`Display <target>` → "Display"
    text = RST_ROLE_RE.sub(lambda m: (m.group(1) or m.group(2) or "").strip(), text)

    # 9. Convert double-backtick inline code to single-backtick Markdown style
    text = RST_DBL_BACKTICK_RE.sub(r"`\1`", text)

    # 10. Convert RST external hyperlinks: `Display text <url>`_ → [Display text](url)
    #     and anonymous: `Display text <url>`__ → same
    text = re.sub(r"`([^`<]+?)\s*<([^>]+)>`_+", r"[\1](\2)", text)

    # 10. Collapse excessive blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def clean_md_body(text: str) -> str:
    """
    Strip MyST-specific markup from a Markdown file.

    MyST (Markdown + Sphinx) adds reference labels and directives not valid
    in plain Markdown.  This function removes them while keeping prose.
    """
    # 1. Strip MyST reference labels: "(label)=" on its own line
    text = re.sub(MYST_LABEL_RE.pattern, "", text, flags=re.MULTILINE)

    # 2. Convert MyST admonitions to blockquotes: ":::{note}\nbody\n:::"
    def myst_admonition_sub(m: re.Match) -> str:
        label = m.group(1).title()
        body = m.group(2).strip()
        return f"\n> **{label}:** {body}\n"
    text = MYST_ADMONITION_RE.sub(myst_admonition_sub, text)

    # 3. Strip MyST fenced directives: ```{literalinclude} ...``` (code-like blocks)
    text = re.sub(r"```\{[^}]+\}[^\n]*\n.*?```", "[code example]", text, flags=re.DOTALL)

    # 4. Convert MyST inline roles to plain text: {ref}`Display <target>` → "Display"
    text = MYST_ROLE_RE.sub(lambda m: (m.group(1) or m.group(2) or "").strip(), text)

    # 5. Collapse excessive blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


# ---------------------------------------------------------------------------
# Topic type classification
# ---------------------------------------------------------------------------

# Files that are navigation containers — they just list links to child pages.
SECTION_FILENAMES = frozenset({
    "index.rst", "index.md",
    "user-guide.rst", "user-guides.rst",   # top-level TOC in data/train
    "examples.rst",                         # example gallery pages
    "ray-libraries.rst",                    # overview of all libraries
    "use-cases.rst",                        # landing page
    "overview.rst", "overview.md",          # section overviews
})

# Subdirectory names whose contents are procedural how-to material.
TASK_SUBDIRS = frozenset({
    "user-guides", "tutorials", "production-guide", "advanced-guides",
})

# Filename substrings that strongly signal a task (how-to) page.
TASK_PATTERNS = (
    "getting-started", "getting_started",
    "quickstart",
    "how-to",
    # Data manipulation verbs
    "loading-data", "saving-data", "transforming-data", "iterating-over",
    "joining-data", "shuffling-data", "mixing-data", "aggregating-data",
    "working-with",
    # Serve operational pages
    "develop-and-deploy", "configure-serve", "autoscaling-guide",
    "http-guide", "model-composition", "model-multiplexing",
    "multi-app", "resource-allocation",
    # Train framework-specific guides
    "getting-started-pytorch", "getting-started-lightgbm",
    "getting-started-xgboost", "getting-started-jax",
    "getting-started-transformers",
    "distributed-tensorflow",
    # Observability how-tos
    "monitoring",
)

# Filename substrings that signal a concept (explanatory) page.
CONCEPT_PATTERNS = (
    "key-concepts", "concepts",
    "walkthrough",     # Ray Core walkthrough is conceptual despite the name
    "internals",
    "architecture",
    "fault-tolerance", "fault_tolerance",
    "handling-dependencies",
    "namespaces",
    "configure",
    "actors", "tasks", "objects",
    "scheduling",
    "miscellaneous",
    "advanced-topics",
    "cross-language",
    "type-hint",
    "ray-dag",
    "data-internals",
    "comparisons",
)


def classify_topic_type(section: str, rel: Path, title: str) -> str:
    """
    Classify a Ray docs page into one of the five topic types.

    Priority order:
      1. Explicit section/index filenames → section
      2. Parent subdirectory name → task (user-guides/, tutorials/, etc.)
      3. Filename pattern → task or concept
      4. Title keywords → task
      5. Default → concept  (most Ray pages are explanatory)
    """
    filename = rel.name.lower()
    parts = [p.lower() for p in rel.parts]

    # --- section -------------------------------------------------------
    if filename in SECTION_FILENAMES:
        return "section"

    # --- subdirectory-based task classification -------------------------
    # files in user-guides/, tutorials/, production-guide/ are how-to pages
    if len(parts) > 1 and parts[-2] in TASK_SUBDIRS:
        return "task"

    # --- filename-based ------------------------------------------------
    for pat in TASK_PATTERNS:
        if pat in filename:
            return "task"

    for pat in CONCEPT_PATTERNS:
        if pat in filename:
            return "concept"

    # --- title keyword fallback ----------------------------------------
    title_lower = title.lower()
    task_title_signals = (
        "get started", "getting started", "quickstart",
        "tutorial", "how to", "step-by-step",
        "configuring", "deploying", "serving",
    )
    if any(sig in title_lower for sig in task_title_signals):
        return "task"

    return "concept"


# ---------------------------------------------------------------------------
# Subject derivation
# ---------------------------------------------------------------------------

# Maps the top-level section directory name to a subject ID in taxonomy.yaml.
SECTION_TO_SUBJECT: dict[str, str] = {
    "ray-core": "core",
    "serve": "serve",
    "train": "train",
    "tune": "tune",
    "data": "data",
    "ray-observability": "observability",
    "ray-overview": "core",   # overview pages are Ray Core context
}


def primary_subject(section: str) -> Optional[str]:
    return SECTION_TO_SUBJECT.get(section)


# ---------------------------------------------------------------------------
# Canonical path + stable topic ID
# ---------------------------------------------------------------------------

def canonical_path(section: str, rel: Path) -> str:
    """
    Build the canonical URL path for a Ray doc page.

    Mirrors the docs.ray.io URL structure: /en/latest/<section>/<path>
    Index files map to the section root (no filename in path).

    Examples:
      ray-core / actors.rst  →  /en/latest/ray-core/actors
      serve / getting_started.md  →  /en/latest/serve/getting_started
      data / index.rst  →  /en/latest/data/
    """
    # Strip the file extension
    p = rel.with_suffix("").as_posix()
    # Index files resolve to the directory
    if p == "index":
        return f"/en/latest/{section}/"
    return f"/en/latest/{section}/{p}"


def topic_id(section: str, rel: Path) -> str:
    """
    Build a stable dot-separated ID for use as the RDF node local name.

    Examples:
      ray-core / actors.rst                  →  ray-core.actors
      ray-core / actors / async_api.rst      →  ray-core.actors.async_api
      serve / getting_started.md             →  serve.getting_started
    """
    p = rel.with_suffix("").as_posix()
    if p == "index":
        return section
    return f"{section}.{p.replace('/', '.')}"


def source_url(section: str, rel: Path) -> str:
    """GitHub permalink for the source file."""
    return (
        f"https://github.com/ray-project/ray/blob/master"
        f"/doc/source/{section}/{rel.as_posix()}"
    )


# ---------------------------------------------------------------------------
# Glossary term mention detection
# ---------------------------------------------------------------------------

def build_term_matchers(
    glossary: list[dict],
) -> list[tuple[str, list[str], re.Pattern]]:
    """
    Pre-compile case-insensitive word-boundary regexes for each glossary term.

    Returns a list of (term_id, subjects, pattern) tuples.
    Patterns are sorted by length (longest first) to prefer specific matches.
    """
    matchers = []
    for term in glossary:
        term_id = term["id"]
        subjects = term.get("subjects") or []
        # Build an alternation over all patterns for this term.
        # Sort patterns longest-first to avoid "actor" shadowing "ray actor".
        patterns = sorted(term.get("patterns") or [term["label"]], key=len, reverse=True)
        # re.escape handles hyphens and underscores; \b gives word boundaries.
        alts = "|".join(re.escape(p) for p in patterns)
        regex = re.compile(rf"\b(?:{alts})\b", re.IGNORECASE)
        matchers.append((term_id, subjects, regex))
    return matchers


def find_mentions(
    body: str,
    matchers: list[tuple[str, list[str], re.Pattern]],
) -> list[str]:
    """
    Return sorted list of glossary term IDs whose patterns appear in body text.

    Each term is reported at most once regardless of how many times it appears.
    """
    found = []
    for term_id, _subjects, regex in matchers:
        if regex.search(body):
            found.append(term_id)
    return sorted(found)


# ---------------------------------------------------------------------------
# Reference extraction (Markdown internal links only)
# ---------------------------------------------------------------------------

def extract_md_references(body: str, section: str, rel: Path) -> list[str]:
    """
    Extract internal cross-references from Markdown relative links.

    Converts relative hrefs like "../actors" or "./key-concepts" into canonical
    paths so build_graph.py can resolve them to topic URIs.

    RST :ref: and :doc: roles are Sphinx-specific and can't be resolved without
    the full Sphinx build environment — those are skipped.
    """
    refs = []
    for href in MD_LINK_RE.findall(body):
        # Strip any .html or .rst suffix that may appear in the href
        href = re.sub(r"\.(html|rst|md)$", "", href)
        # Resolve the relative path against the current file's directory
        base_dir = rel.parent
        try:
            resolved = (Path(section) / base_dir / href).resolve()
            # Convert back to a canonical /en/latest/... path
            # resolved is an absolute filesystem path — we want the part
            # relative to the section root
            rel_resolved = resolved.relative_to(Path(section).resolve())
            canon = f"/en/latest/{section}/{rel_resolved.as_posix()}"
            refs.append(canon)
        except (ValueError, OSError):
            pass  # skip un-resolvable relative links
    return sorted(set(refs))


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    taxonomy = yaml.safe_load(TAXONOMY.read_text())
    known_subjects = {s["id"] for s in taxonomy["subjects"]}

    glossary_data = yaml.safe_load(GLOSSARY.read_text())
    glossary_terms = glossary_data.get("terms") or []
    term_matchers = build_term_matchers(glossary_terms)
    # Map term_id → list of subject IDs so we can inherit subjects from mentions
    term_subjects: dict[str, list[str]] = {
        t["id"]: t.get("subjects") or [] for t in glossary_terms
    }

    # Collect both .md and .rst files
    files = sorted(
        list(RAW.rglob("*.md")) + list(RAW.rglob("*.rst"))
    )
    if not files:
        sys.exit(
            "No files in content/raw/ — run scripts/scrape_ray_docs.sh first"
        )

    ENRICHED.mkdir(parents=True, exist_ok=True)

    new_subjects: set[str] = set()
    count = 0

    for f in files:
        rel = f.relative_to(RAW)
        # First path component is the section (ray-core, serve, etc.)
        section = rel.parts[0]
        # Relative path within the section
        rel_in_section = Path(*rel.parts[1:])

        raw_text = f.read_text(encoding="utf-8", errors="replace")
        suffix = f.suffix.lower()

        # ── Extract title ──────────────────────────────────────────────
        if suffix == ".rst":
            title = extract_title_rst(raw_text)
        else:
            title = extract_title_md(raw_text)

        # Fallback: derive title from filename
        if not title:
            title = rel_in_section.stem.replace("-", " ").replace("_", " ").title()

        # ── Clean body ────────────────────────────────────────────────
        if suffix == ".rst":
            body = clean_rst_body(raw_text)
        else:
            body = clean_md_body(raw_text)

        # ── Classify ──────────────────────────────────────────────────
        ttype = classify_topic_type(section, rel_in_section, title)

        # ── Subjects ──────────────────────────────────────────────────
        # Start with the section's primary subject
        subjects: list[str] = []
        prim = primary_subject(section)
        if prim:
            subjects.append(prim)

        # ── Mentions (text search against glossary) ────────────────────
        mentions = find_mentions(body, term_matchers)

        # Inherit additional subjects from mentioned terms
        for m in mentions:
            for s in term_subjects.get(m) or []:
                if s not in subjects:
                    subjects.append(s)

        new_subjects.update(s for s in subjects if s not in known_subjects)

        # ── References ────────────────────────────────────────────────
        # Only extract from .md files — RST cross-refs require Sphinx to resolve
        if suffix == ".md":
            refs = extract_md_references(body, section, rel_in_section)
        else:
            refs = []

        # ── Build enriched frontmatter ─────────────────────────────────
        meta = {
            "id": topic_id(section, rel_in_section),
            "title": title,
            "topic_type": ttype,
            "description": "",          # Ray docs have no summary field
            "subjects": subjects,
            "mentions": mentions,
            "references": refs,
            "canonical_path": canonical_path(section, rel_in_section),
            "source": source_url(section, rel_in_section),
            "license": "Apache 2.0, The Ray Authors",
        }

        # ── Write to content/enriched/ as .md ─────────────────────────
        # Output is always .md for compatibility with build_graph.py and
        # publish_confluence.py, even if the source was .rst.
        out_rel = rel_in_section.with_suffix(".md")
        out = ENRICHED / section / out_rel
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(
            "---\n"
            + yaml.dump(meta, sort_keys=False, allow_unicode=True)
            + "---\n\n"
            + body
            + "\n"
        )
        count += 1

    if new_subjects:
        print(
            f">> New subjects beyond taxonomy: {sorted(new_subjects)}\n"
            "   Add them to taxonomy/taxonomy.yaml if you want them labelled."
        )
    print(f">> Enriched {count} topics → content/enriched/")


if __name__ == "__main__":
    main()
