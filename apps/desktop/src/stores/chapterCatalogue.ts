import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { Chapter } from "../api/types";

export type ChapterCatalogueEntry = {
  id: string;
  project_id: string;
  title: string;
  order_index: number;
  source_format: string;
  created_at: string;
  segment_count: number;
};

type ChapterCatalogueState = {
  chaptersByProject: Record<string, ChapterCatalogueEntry[]>;
  rememberChapter: (chapter: Chapter) => void;
};

function createChapterCatalogueEntry(chapter: Chapter): ChapterCatalogueEntry {
  return {
    id: chapter.id,
    project_id: chapter.project_id,
    title: chapter.title,
    order_index: chapter.order_index,
    source_format: chapter.source_format,
    created_at: chapter.created_at,
    segment_count: chapter.segments.length
  };
}

export const useChapterCatalogueStore = create<ChapterCatalogueState>()(
  persist(
    (set) => ({
      chaptersByProject: {},
      rememberChapter: (chapter) =>
        set((snapshot) => {
          const chapterEntry = createChapterCatalogueEntry(chapter);
          const projectChapters = snapshot.chaptersByProject[chapter.project_id] ?? [];
          const remainingChapters = projectChapters.filter(
            (storedChapter) => storedChapter.id !== chapter.id
          );
          const orderedChapters = [...remainingChapters, chapterEntry].sort(
            (leftChapter, rightChapter) =>
              leftChapter.order_index - rightChapter.order_index ||
              leftChapter.created_at.localeCompare(rightChapter.created_at)
          );

          return {
            chaptersByProject: {
              ...snapshot.chaptersByProject,
              [chapter.project_id]: orderedChapters
            }
          };
        })
    }),
    {
      name: "novel-translate-chapter-catalogue"
    }
  )
);
