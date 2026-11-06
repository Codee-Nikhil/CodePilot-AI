"use client";

import { useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Button } from "@/components/ui/button";

const MARKDOWN_STYLES =
  "[&_h1]:text-2xl [&_h1]:font-semibold [&_h1]:mt-0 [&_h2]:text-xl [&_h2]:font-semibold [&_h2]:mt-6 " +
  "[&_h3]:text-lg [&_h3]:font-semibold [&_h3]:mt-4 [&_p]:my-3 [&_ul]:list-disc [&_ul]:pl-6 [&_ol]:list-decimal [&_ol]:pl-6 " +
  "[&_pre]:my-3 [&_pre]:overflow-x-auto [&_pre]:rounded-md [&_pre]:bg-muted [&_pre]:p-3 [&_code]:font-mono [&_code]:text-[0.85em] " +
  "[&_a]:underline [&_a]:underline-offset-4";

export function ReadmePreview({ content }: { content: string }) {
  const [view, setView] = useState<"preview" | "source">("preview");

  function download() {
    const blob = new Blob([content], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "README.md";
    a.click();
    URL.revokeObjectURL(url);
  }

  async function copy() {
    await navigator.clipboard.writeText(content);
  }

  return (
    <div className="space-y-3">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div className="flex gap-1 rounded-md border p-1">
          <Button size="sm" variant={view === "preview" ? "secondary" : "ghost"} onClick={() => setView("preview")}>Preview</Button>
          <Button size="sm" variant={view === "source" ? "secondary" : "ghost"} onClick={() => setView("source")}>Markdown</Button>
        </div>
        <div className="flex gap-2">
          <Button size="sm" variant="outline" onClick={copy}>Copy</Button>
          <Button size="sm" variant="outline" onClick={download}>Download .md</Button>
        </div>
      </div>
      <div className="rounded-lg border p-4">
        {view === "preview" ? (
          <div className={MARKDOWN_STYLES}>
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{content}</ReactMarkdown>
          </div>
        ) : (
          <pre className="overflow-x-auto whitespace-pre-wrap font-mono text-sm">{content}</pre>
        )}
      </div>
    </div>
  );
}
