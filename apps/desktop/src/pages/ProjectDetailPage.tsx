import { useState } from "react";
import { Link, useParams } from "react-router-dom";
import { useImportTxtChapter, useProject } from "../api/hooks";
import { pickTextFile } from "../lib/files";
import { useChapterCatalogueStore } from "../stores/chapterCatalogue";

function buildChapterTitle(fileName: string): string {
  const titleWithoutExtension = fileName.replace(/\.txt$/i, "").trim();
  return titleWithoutExtension.length > 0 ? titleWithoutExtension : fileName;
}

export function ProjectDetailPage() {
  const { projectId } = useParams();
  const projectQuery = useProject(projectId);
  const importTxtChapter = useImportTxtChapter(projectId);
  const [isPickingTextFile, setIsPickingTextFile] = useState(false);
  const [importMessage, setImportMessage] = useState<string | null>(null);
  const chapterEntries = useChapterCatalogueStore((snapshot) =>
    projectId === undefined ? [] : snapshot.chaptersByProject[projectId] ?? []
  );

  async function importSelectedTextFile() {
    if (projectId === undefined || importTxtChapter.isPending) {
      return;
    }

    setImportMessage(null);
    setIsPickingTextFile(true);

    try {
      const pickedTextFile = await pickTextFile();
      if (pickedTextFile === null) {
        return;
      }

      importTxtChapter.mutate(
        {
          title: buildChapterTitle(pickedTextFile.name),
          content: pickedTextFile.content
        },
        {
          onSuccess: (importedChapter) => {
            setImportMessage(`${importedChapter.title} · ${importedChapter.segments.length} 段`);
          }
        }
      );
    } catch (caughtValue) {
      setImportMessage(caughtValue instanceof Error ? caughtValue.message : "TXT 导入失败");
    } finally {
      setIsPickingTextFile(false);
    }
  }

  const projectMessage = projectQuery.error instanceof Error ? projectQuery.error.message : null;
  const importFailureMessage =
    importTxtChapter.error instanceof Error ? importTxtChapter.error.message : null;

  if (projectQuery.isLoading) {
    return <div className="rounded-lg border border-stone-200 bg-white p-4 text-sm">加载中</div>;
  }

  if (projectMessage || projectQuery.data === undefined) {
    return (
      <div className="rounded-lg border border-stone-200 bg-white p-4 text-sm text-red-700">
        {projectMessage ?? "项目不存在"}
      </div>
    );
  }

  const project = projectQuery.data;

  return (
    <div className="space-y-5">
      <div className="flex flex-wrap items-start justify-between gap-4 rounded-lg border border-stone-200 bg-white p-4 shadow-sm">
        <div className="min-w-0">
          <Link to="/" className="text-sm text-ink-500 hover:text-ink-900">
            项目
          </Link>
          <h1 className="mt-1 truncate text-xl font-semibold">{project.name}</h1>
          <div className="mt-2 text-sm text-ink-500">
            {project.source_lang} → {project.target_lang}
          </div>
        </div>
        <button
          className="h-10 rounded-md bg-ink-900 px-4 text-sm font-medium text-white transition hover:bg-black disabled:cursor-not-allowed disabled:bg-stone-400"
          type="button"
          onClick={importSelectedTextFile}
          disabled={isPickingTextFile || importTxtChapter.isPending}
        >
          导入TXT
        </button>
      </div>

      {(importMessage || importFailureMessage) && (
        <div
          className={`rounded-lg border px-4 py-3 text-sm ${
            importFailureMessage
              ? "border-red-200 bg-red-50 text-red-700"
              : "border-emerald-200 bg-emerald-50 text-emerald-800"
          }`}
        >
          {importFailureMessage ?? importMessage}
        </div>
      )}

      <section className="rounded-lg border border-stone-200 bg-white shadow-sm">
        <div className="flex items-center justify-between border-b border-stone-200 px-4 py-3">
          <h2 className="text-lg font-semibold">章节</h2>
          <span className="text-sm text-ink-500">{chapterEntries.length}</span>
        </div>
        {chapterEntries.length === 0 ? (
          <div className="p-4 text-sm text-ink-500">暂无章节</div>
        ) : (
          <div className="divide-y divide-stone-100">
            {chapterEntries.map((chapter) => (
              <Link
                key={chapter.id}
                to={`/chapters/${chapter.id}`}
                className="block px-4 py-4 transition hover:bg-stone-50"
              >
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <div className="min-w-0">
                    <div className="truncate text-sm font-semibold">{chapter.title}</div>
                    <div className="mt-1 text-xs text-ink-500">
                      {chapter.source_format.toUpperCase()} · {chapter.segment_count} 段
                    </div>
                  </div>
                  <div className="text-xs text-ink-500">#{chapter.order_index + 1}</div>
                </div>
              </Link>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
