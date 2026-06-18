import fs from "fs";
import path from "path";
import { Store, Parser } from "n3";

const GRAPH_PATH =
  process.env.GRAPH_PATH ??
  path.resolve(process.cwd(), "graph/docs_graph.ttl");

let _store: Store | null = null;

export function getStore(): Store {
  if (_store) return _store;

  const ttl = fs.readFileSync(GRAPH_PATH, "utf-8");
  const store = new Store();
  const parser = new Parser({ format: "Turtle" });
  const quads = parser.parse(ttl);
  store.addQuads(quads);
  _store = store;
  return store;
}
