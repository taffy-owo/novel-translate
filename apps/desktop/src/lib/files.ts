import { open } from "@tauri-apps/plugin-dialog";
import { invoke } from "@tauri-apps/api/core";

export type PickedTextFile = {
  name: string;
  content: string;
};

const txtFileFilters = [
  {
    name: "TXT",
    extensions: ["txt"]
  }
];

function readFileName(filePath: string): string {
  return filePath.split(/[\\/]/).at(-1) ?? "chapter.txt";
}

export async function pickTextFile(): Promise<PickedTextFile | null> {
  const selectedPath = await open({
    multiple: false,
    filters: txtFileFilters
  });

  if (selectedPath === null || Array.isArray(selectedPath)) {
    return null;
  }

  // The native dialog returns an absolute path; the Rust `read_text_file` command reads it
  // without the fs-plugin scope restriction that would otherwise reject arbitrary paths.
  const content = await invoke<string>("read_text_file", { path: selectedPath });
  return { name: readFileName(selectedPath), content };
}
