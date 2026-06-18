import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "DocsBot — Knowledge Graph Demo",
  description: "A docs-as-code + knowledge graph framework demo, built with Claude.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="h-full">
      <body className="h-full bg-white text-gray-900 antialiased">
        {children}
      </body>
    </html>
  );
}
