import { NextRequest, NextResponse } from "next/server";
import { readDocContent } from "@/lib/pageTree";

export async function GET(req: NextRequest) {
  const relPath = req.nextUrl.searchParams.get("path");
  if (!relPath) {
    return NextResponse.json({ error: "Missing path" }, { status: 400 });
  }

  // Prevent path traversal
  if (relPath.includes("..") || relPath.startsWith("/")) {
    return NextResponse.json({ error: "Invalid path" }, { status: 400 });
  }

  const doc = readDocContent(relPath);
  if (!doc) {
    return NextResponse.json({ error: "Not found" }, { status: 404 });
  }

  return NextResponse.json(doc);
}
