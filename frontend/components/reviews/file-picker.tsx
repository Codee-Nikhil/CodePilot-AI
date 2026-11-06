"use client";

import { Button } from "@/components/ui/button";
import { FileTree } from "@/components/explorer/file-tree";
import type { FileNode } from "@/types/repo";

const MAX_FILES = 15;

interface Props {
  files: FileNode[];
  selected: Set<string>;
  onToggle: (path: string) => void;
  onStart: () => void;
  starting: boolean;
}

export function FilePicker({ files, selected, onToggle, onStart, starting }: Props) {
  return (
    <div className="space-y-3">
      <div className="rounded-lg border">
        <FileTree files={files} selected={null} onSelect={() => {}} selectable selectedSet={selected} onToggleSelect={onToggle} />
      </div>
      <div className="flex items-center justify-between">
        <p className="text-sm text-muted-foreground">
          {selected.size} of {MAX_FILES} max selected
        </p>
        <Button onClick={onStart} disabled={selected.size === 0 || selected.size > MAX_FILES || starting}>
          {starting ? "Starting…" : "Review selected files"}
        </Button>
      </div>
      {selected.size > MAX_FILES && (
        <p role="alert" className="text-sm text-destructive">Select at most {MAX_FILES} files per review.</p>
      )}
    </div>
  );
}
