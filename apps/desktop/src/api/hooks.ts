import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { requestJson, requestText } from "./client";
import type {
  Chapter,
  ChapterTranslationReceipt,
  Project,
  ProjectDraft,
  Segment,
  SegmentTranslationDraft,
  TxtChapterDraft
} from "./types";
import { useChapterCatalogueStore } from "../stores/chapterCatalogue";

const projectsQueryKey = ["projects"] as const;
const projectQueryKey = (projectId: string) => ["project", projectId] as const;
const chapterQueryKey = (chapterId: string) => ["chapter", chapterId] as const;

function chapterHasActiveTranslation(chapter: Chapter | undefined): boolean {
  return (
    chapter?.segments.some(
      (segment) => segment.status === "pending" || segment.status === "translating"
    ) ?? false
  );
}

export function useProjects() {
  return useQuery({
    queryKey: projectsQueryKey,
    queryFn: () => requestJson<Project[]>("/projects")
  });
}

export function useProject(projectId: string | undefined) {
  return useQuery({
    queryKey: projectId === undefined ? ["project"] : projectQueryKey(projectId),
    queryFn: () => requestJson<Project>(`/projects/${projectId}`),
    enabled: projectId !== undefined
  });
}

export function useCreateProject() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (projectDraft: ProjectDraft) =>
      requestJson<Project>("/projects", {
        method: "POST",
        body: projectDraft
      }),
    onSuccess: (createdProject) => {
      queryClient.setQueryData<Project>(projectQueryKey(createdProject.id), createdProject);
      void queryClient.invalidateQueries({ queryKey: projectsQueryKey });
    }
  });
}

export function useImportTxtChapter(projectId: string | undefined) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (chapterDraft: TxtChapterDraft) =>
      requestJson<Chapter>(`/projects/${projectId}/chapters/import-txt`, {
        method: "POST",
        body: chapterDraft
      }),
    onSuccess: (importedChapter) => {
      useChapterCatalogueStore.getState().rememberChapter(importedChapter);
      queryClient.setQueryData<Chapter>(chapterQueryKey(importedChapter.id), importedChapter);
    }
  });
}

export function useChapter(chapterId: string | undefined) {
  return useQuery({
    queryKey: chapterId === undefined ? ["chapter"] : chapterQueryKey(chapterId),
    queryFn: () => requestJson<Chapter>(`/chapters/${chapterId}`),
    enabled: chapterId !== undefined,
    refetchInterval: (query) => (chapterHasActiveTranslation(query.state.data) ? 2000 : false)
  });
}

export function useTranslateChapter() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (chapterId: string) =>
      requestJson<ChapterTranslationReceipt>(`/chapters/${chapterId}/translate`, {
        method: "POST"
      }),
    onSuccess: (translationReceipt) => {
      void queryClient.invalidateQueries({
        queryKey: chapterQueryKey(translationReceipt.chapter_id)
      });
    }
  });
}

type SegmentUpdateRequest = {
  chapterId: string;
  segmentId: string;
  targetText: string | null;
};

export function useUpdateSegment() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (segmentDraft: SegmentUpdateRequest) =>
      requestJson<Segment>(`/segments/${segmentDraft.segmentId}`, {
        method: "PUT",
        body: {
          target_text: segmentDraft.targetText
        } satisfies SegmentTranslationDraft
      }),
    onSuccess: (updatedSegment, segmentDraft) => {
      queryClient.setQueryData<Chapter>(
        chapterQueryKey(segmentDraft.chapterId),
        (cachedChapter) => {
          if (cachedChapter === undefined) {
            return cachedChapter;
          }

          return {
            ...cachedChapter,
            segments: cachedChapter.segments.map((segment) =>
              segment.id === updatedSegment.id ? updatedSegment : segment
            )
          };
        }
      );
    }
  });
}

export function exportChapter(chapterId: string): Promise<string> {
  return requestText(`/chapters/${chapterId}/export?format=txt`);
}
