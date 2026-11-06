export interface TreeNode {
  name: string;
  path: string;
  type: "file" | "dir";
  children: TreeNode[];
}

export function buildTree(files: { path: string }[]): TreeNode[] {
  const root: TreeNode = { name: "", path: "", type: "dir", children: [] };

  for (const { path } of files) {
    const parts = path.split("/");
    let node = root;
    parts.forEach((part, i) => {
      const type = i === parts.length - 1 ? "file" : "dir";
      let child = node.children.find((c) => c.name === part && c.type === type);
      if (!child) {
        child = { name: part, path: parts.slice(0, i + 1).join("/"), type, children: [] };
        node.children.push(child);
      }
      node = child;
    });
  }

  sortNodes(root.children);
  return root.children;
}

function sortNodes(nodes: TreeNode[]) {
  nodes.sort((a, b) => (a.type === b.type ? a.name.localeCompare(b.name) : a.type === "dir" ? -1 : 1));
  nodes.forEach((n) => sortNodes(n.children));
}
