import fs from "fs";
import path from "path";
import matter from "gray-matter";

const CONTENT_ROOT =
  process.env.CONTENT_ROOT ??
  path.resolve(process.cwd(), "content/enriched");

const SECTION_LABELS: Record<string, string> = {
  "ray-overview": "Overview",
  "ray-core": "Ray Core",
  serve: "Ray Serve",
  train: "Ray Train",
  tune: "Ray Tune",
  data: "Ray Data",
  "ray-observability": "Observability",
};

export interface PageMeta {
  id: string;
  title: string;
  topic_type: string;
  path: string; // relative path from content/enriched, e.g. "ray-core/actors/named-actors.md"
}

export interface SectionTree {
  section: string;
  label: string;
  pages: PageMeta[];
}

function readMeta(filePath: string, relPath: string): PageMeta | null {
  try {
    const raw = fs.readFileSync(filePath, "utf-8");
    const { data } = matter(raw);
    return {
      id: data.id ?? relPath,
      title: data.title ?? path.basename(filePath, ".md"),
      topic_type: data.topic_type ?? "concept",
      path: relPath,
    };
  } catch {
    return null;
  }
}

function walkSection(sectionDir: string, sectionName: string): PageMeta[] {
  const pages: PageMeta[] = [];

  function walk(dir: string) {
    const entries = fs.readdirSync(dir, { withFileTypes: true });
    for (const entry of entries) {
      const full = path.join(dir, entry.name);
      if (entry.isDirectory()) {
        walk(full);
      } else if (entry.name.endsWith(".md")) {
        const relPath = path.relative(CONTENT_ROOT, full);
        const meta = readMeta(full, relPath);
        if (meta) pages.push(meta);
      }
    }
  }

  walk(sectionDir);
  return pages.sort((a, b) => a.title.localeCompare(b.title));
}

export function buildPageTree(): SectionTree[] {
  const sections: SectionTree[] = [];
  const order = [
    "ray-overview",
    "ray-core",
    "serve",
    "train",
    "tune",
    "data",
    "ray-observability",
  ];

  for (const section of order) {
    const dir = path.join(CONTENT_ROOT, section);
    if (!fs.existsSync(dir)) continue;
    const pages = walkSection(dir, section);
    if (pages.length === 0) continue;
    sections.push({
      section,
      label: SECTION_LABELS[section] ?? section,
      pages,
    });
  }

  return sections;
}

export function readDocContent(relPath: string): { meta: PageMeta; body: string } | null {
  const full = path.join(CONTENT_ROOT, relPath);
  if (!fs.existsSync(full)) return null;
  try {
    const raw = fs.readFileSync(full, "utf-8");
    const { data, content } = matter(raw);
    return {
      meta: {
        id: data.id ?? relPath,
        title: data.title ?? path.basename(full, ".md"),
        topic_type: data.topic_type ?? "concept",
        path: relPath,
      },
      body: content,
    };
  } catch {
    return null;
  }
}
