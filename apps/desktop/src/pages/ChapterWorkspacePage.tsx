import { useEffect, useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";
import {
  exportChapter,
  useChapter,
  useTranslateChapter,
  useUpdateSegment
} from "../api/hooks";
import type { Chapter, Segment, SegmentStatus } from "../api/types";
import { useChapterCatalogueStore } from "../stores/chapterCatalogue";

const statusLabels: Record<SegmentStatus, string> = {
  pending: "待翻译",
  translating: "翻译中",
  done: "已完成",
  error: "失败"
};

function createSegmentCounts(chapter: Chapter | undefined): Record<SegmentStatus, number> {
  const segmentCounts: Record<SegmentStatus, number> = {
    pending: 0,
    translating: 0,
    done: 0,
    error: 0
  };

  chapter?.segments.forEach((segment) => {
    segmentCounts[segment.status] += 1;
  });

  return segmentCounts;
}

function buildTxtFileName(chapterTitle: string): string {
  const safeTitle = chapterTitle.replace(/[\\/:*?"<>|]/g, "_").trim();
  return `${safeTitle.length > 0 ? safeTitle : "chapter"}.txt`;
}

function downloadTextFile(fileName: string, exportedText: string): void {
  const textBlob = new Blob([exportedText], { type: "text/plain;charset=utf-8" });
  const downloadUrl = URL.createObjectURL(textBlob);
  const downloadLink = document.createElement("a");
  downloadLink.href = downloadUrl;
  downloadLink.download = fileName;
  downloadLink.click();
  URL.revokeObjectURL(downloadUrl);
}

function StatusBadge({ status }: { status: SegmentStatus }) {
  const badgeClassName =
    status === "error"
      ? "border-red-200 bg-red-50 text-red-700"
      : status === "done"
        ? "border-emerald-200 bg-emerald-50 text-emerald-800"
        : status === "translating"
          ? "border-sky-200 bg-sky-50 text-sky-800"
          : "border-stone-200 bg-stone-50 text-ink-700";

  return (
    <span className={`rounded-md border px-2 py-1 text-xs font-medium ${badgeClassName}`}>
      {statusLabels[status]}
    </span>
  );
}

function SegmentEditor({ chapterId, segment }: { chapterId: string; segment: Segment }) {
  const updateSegment = useUpdateSegment();
  const [targetDraft, setTargetDraft] = useState(segment.target_text ?? "");

  useEffect(() => {
    setTargetDraft(segment.target_text ?? "");
  }, [segment.id, segment.target_text]);

  const hasPendingEdit = targetDraft !== (segment.target_text ?? "");

  function saveSegmentTranslation() {
    if (!hasPendingEdit || updateSegment.isPending) {
      return;
    }

    updateSegment.mutate({
      chapterId,
      segmentId: segment.id,
      targetText: targetDraft
    });
  }

  const updateMessage = updateSegment.error instanceof Error ? updateSegment.error.message : null;

  return (
    <article className="grid min-h-[180px] grid-cols-1 border-b border-stone-200 bg-white last:border-b-0 lg:grid-cols-2">
      <div className="border-b border-stone-200 p-4 lg:border-b-0 lg:border-r">
        <div className="mb-3 flex items-center justify-between gap-3">
          <span className="text-xs font-medium text-ink-500">第 {segment.order_index + 1} 段</span>
          <StatusBadge status={segment.status} />
        </div>
        <p className="whitespace-pre-wrap text-sm leading-7 text-ink-900">{segment.source_text}</p>
      </div>
      <div className="flex min-h-[180px] flex-col p-4">
        <textarea
          className="min-h-[130px] flex-1 rounded-md border border-stone-300 bg-stone-50 px-3 py-2 text-sm leading-7 outline-none transition focus:border-stone-500 focus:bg-white focus:ring-2 focus:ring-stone-200"
          value={targetDraft}
          onChange={(event) => setTargetDraft(event.target.value)}
        />
        <div className="mt-3 flex min-h-10 flex-wrap items-center justify-between gap-3">
          <div className="text-xs text-red-700">{updateMessage}</div>
          <button
            className="h-9 rounded-md border border-stone-300 bg-white px-3 text-sm font-medium transition hover:bg-stone-50 disabled:cursor-not-allowed disabled:text-ink-500"
            type="button"
            onClick={saveSegmentTranslation}
            disabled={!hasPendingEdit || updateSegment.isPending}
          >
            保存
          </button>
        </div>
      </div>
    </article>
  );
}

export function ChapterWorkspacePage() {
  const { chapterId } = useParams();
  const chapterQuery = useChapter(chapterId);
  const translateChapter = useTranslateChapter();
  const rememberChapter = useChapterCatalogueStore((snapshot) => snapshot.rememberChapter);
  const [exportMessage, setExportMessage] = useState<string | null>(null);
  const [isExportingChapter, setIsExportingChapter] = useState(false);

  useEffect(() => {
    if (chapterQuery.data !== undefined) {
      rememberChapter(chapterQuery.data);
    }
  }, [chapterQuery.data, rememberChapter]);

  const segmentCounts = useMemo(() => createSegmentCounts(chapterQuery.data), [chapterQuery.data]);
  const chapterMessage = chapterQuery.error instanceof Error ? chapterQuery.error.message : null;
  const translationMessage =
    translateChapter.error instanceof Error ? translateChapter.error.message : null;

  async function exportCurrentChapter() {
    if (chapterQuery.data === undefined) {
      return;
    }

    setExportMessage(null);
    setIsExportingChapter(true);

    try {
      const exportedText = await exportChapter(chapterQuery.data.id);
      downloadTextFile(buildTxtFileName(chapterQuery.data.title), exportedText);
      setExportMessage("TXT 已生成");
    } catch (caughtValue) {
      setExportMessage(caughtValue instanceof Error ? caughtValue.message : "导出失败");
    } finally {
      setIsExportingChapter(false);
    }
  }

  if (chapterQuery.isLoading) {
    return <div className="rounded-lg border border-stone-200 bg-white p-4 text-sm">加载中</div>;
  }

  if (chapterMessage || chapterQuery.data === undefined) {
    return (
      <div className="rounded-lg border border-stone-200 bg-white p-4 text-sm text-red-700">
        {chapterMessage ?? "章节不存在"}
      </div>
    );
  }

  const chapter = chapterQuery.data;

  return (
    <div className="space-y-5">
      <div className="flex flex-wrap items-start justify-between gap-4 rounded-lg border border-stone-200 bg-white p-4 shadow-sm">
        <div className="min-w-0">
          <Link
            to={`/projects/${chapter.project_id}`}
            className="text-sm text-ink-500 hover:text-ink-900"
          >
            章节
          </Link>
          <h1 className="mt-1 truncate text-xl font-semibold">{chapter.title}</h1>
          <div className="mt-2 flex flex-wrap gap-2 text-sm">
            {(Object.keys(statusLabels) as SegmentStatus[]).map((status) => (
              <span key={status} className="rounded-md border border-stone-200 px-2 py-1 text-xs">
                {statusLabels[status]} {segmentCounts[status]}
              </span>
            ))}
          </div>
        </div>
        <div className="flex flex-wrap gap-2">
          <button
            className="h-10 rounded-md bg-ink-900 px-4 text-sm font-medium text-white transition hover:bg-black disabled:cursor-not-allowed disabled:bg-stone-400"
            type="button"
            onClick={() => translateChapter.mutate(chapter.id)}
            disabled={translateChapter.isPending}
          >
            翻译本章
          </button>
          <button
            className="h-10 rounded-md border border-stone-300 bg-white px-4 text-sm font-medium transition hover:bg-stone-50 disabled:cursor-not-allowed disabled:text-ink-500"
            type="button"
            onClick={exportCurrentChapter}
            disabled={isExportingChapter}
          >
            导出TXT
          </button>
        </div>
      </div>

      {(translationMessage || exportMessage) && (
        <div
          className={`rounded-lg border px-4 py-3 text-sm ${
            translationMessage
              ? "border-red-200 bg-red-50 text-red-700"
              : "border-emerald-200 bg-emerald-50 text-emerald-800"
          }`}
        >
          {translationMessage ?? exportMessage}
        </div>
      )}

      <section className="overflow-hidden rounded-lg border border-stone-200 bg-white shadow-sm">
        <div className="grid border-b border-stone-200 bg-stone-50 px-4 py-3 text-sm font-semibold text-ink-700 lg:grid-cols-2">
          <div>原文</div>
          <div className="hidden lg:block">译文</div>
        </div>
        {chapter.segments.length === 0 ? (
          <div className="p-4 text-sm text-ink-500">暂无分段</div>
        ) : (
          chapter.segments.map((segment) => (
            <SegmentEditor key={segment.id} chapterId={chapter.id} segment={segment} />
          ))
        )}
      </section>
    </div>
  );
}
