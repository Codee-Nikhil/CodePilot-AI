"use client";

import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { oneDark, oneLight } from "react-syntax-highlighter/dist/esm/styles/prism";

const PRISM_ALIASES: Record<string, string> = { html: "markup", dockerfile: "docker" };

interface Props {
  code: string;
  language: string | null;
  dark: boolean;
}

export default function Highlighter({ code, language, dark }: Props) {
  const lang = language ? (PRISM_ALIASES[language] ?? language) : "text";
  return (
    <SyntaxHighlighter
      language={lang}
      style={dark ? oneDark : oneLight}
      showLineNumbers
      customStyle={{ margin: 0, borderRadius: 0, background: "transparent", fontSize: "0.8125rem" }}
    >
      {code}
    </SyntaxHighlighter>
  );
}
