#!/usr/bin/env python3
"""Run a SPARQL query against graph/docs_graph.ttl. Usage: query.py '<sparql>'"""
import sys
from pathlib import Path
from rdflib import Graph

g = Graph()
g.parse(Path(__file__).resolve().parent.parent / "graph" / "docs_graph.ttl")
for row in g.query(sys.argv[1]):
    print(" | ".join(str(v) for v in row))
