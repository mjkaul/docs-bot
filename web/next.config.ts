import type { NextConfig } from "next";
import path from "path";

// __dirname here is web/ — one level up is the repo root with content/ and graph/
const CONTENT_ROOT = path.resolve(__dirname, "../content/enriched");
const GRAPH_PATH = path.resolve(__dirname, "../graph/docs_graph.ttl");

const nextConfig: NextConfig = {
  turbopack: {
    root: path.resolve(__dirname),
  },
  env: {
    CONTENT_ROOT,
    GRAPH_PATH,
  },
};

export default nextConfig;
