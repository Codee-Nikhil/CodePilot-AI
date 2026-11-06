"use client";

import { useMemo, useState } from "react";
import { ChevronDown, ChevronRight, File, Folder } from "lucide-react";
import { Input } from "@/components/ui/input";
import { buildTree, type TreeNode } from "@/lib/file-tree";
import { cn } from "@/lib/utils";
import type { FileNode } from "@/types/repo";

interface TreeProps {
  files: FileNode[];
  selected: string | null;
  onSelect: (path: string) => void;
  selectable?: boolean;
  selectedSet?: Set<string>;
  onToggleSelect?: (path: string) => void;
}

const ROW = "flex w-full items-center gap-2 rounded px-2 py-1 text-left text-sm hover:bg-accent";

export function FileTree({ files, selected, onSelect, selectable, selectedSet, onToggleSelect }: TreeProps) {
  const [query, setQuery] = useState("");
  const tree = useMemo(() => buildTree(files), [files]);
  const q = query.trim().toLowerCase();
  const matches = useMemo(() => (q ? files.filter((f) => f.path.toLowerCase().includes(q)).slice(0, 100) : null), [files, q]);

  const row = (path: string, name: string, isFile: boolean, depth: number) => (
    <button
      type="button"
      title={path}
      style={{ paddingLeft: `${depth * 12 + 8}px` }}
      onClick={() => (isFile ? onSelect(path) : undefined)}
      className={cn(ROW, selected === path && "bg-accent font-medium")}
    >
      {selectable && isFile && (
        <input
          type="checkbox"
          checked={selectedSet?.has(path) ?? false}
          onChange={(e) => {
            e.stopPropagation();
            onToggleSelect?.(path);
          }}
          onClick={(e) => e.stopPropagation()}
          className="shrink-0"
        />
      )}
      {isFile ? <File className="h-4 w-4 shrink-0 text-muted-foreground" /> : <Folder className="h-4 w-4 shrink-0 text-muted-foreground" />}
      <span className="truncate">{name}</span>
    </button>
  );

  return (
    <div>
      <div className="border-b p-2">
        <Input type="search" aria-label="Search files" placeholder="Search files…" value={query} onChange={(e) => setQuery(e.target.value)} />
      </div>
      <div className="max-h-[40vh] overflow-y-auto p-2 lg:max-h-[70vh]">
        {matches ? (
          matches.length ? (
            <ul>{matches.map((f) => <li key={f.path}>{row(f.path, f.path, true, 0)}</li>)}</ul>
          ) : (
            <p className="p-2 text-sm text-muted-foreground">No files match.</p>
          )
        ) : (
          <ul>
            {tree.map((node) => (
              <TreeItem key={node.path} node={node} depth={0} renderRow={row} />
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}

function TreeItem({ node, depth, renderRow }: { node: TreeNode; depth: number; renderRow: (path: string, name: string, isFile: boolean, depth: number) => React.ReactNode }) {
  const [open, setOpen] = useState(depth === 0);

  if (node.type === "file") {
    return <li>{renderRow(node.path, node.name, true, depth)}</li>;
  }

  return (
    <li>
      <button
        type="button"
        style={{ paddingLeft: `${depth * 12 + 8}px` }}
        onClick={() => setOpen(!open)}
        aria-expanded={open}
        className={ROW}
      >
        {open ? <ChevronDown className="h-4 w-4 shrink-0" /> : <ChevronRight className="h-4 w-4 shrink-0" />}
        <Folder className="h-4 w-4 shrink-0 text-muted-foreground" />
        <span className="truncate">{node.name}</span>
      </button>
      {open && (
        <ul>
          {node.children.map((child) => (
            <TreeItem key={child.path} node={child} depth={depth + 1} renderRow={renderRow} />
          ))}
        </ul>
      )}
    </li>
  );
}
