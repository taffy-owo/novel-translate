export type SegmentStatus = "pending" | "translating" | "done" | "error";

export type Project = {
  id: string;
  name: string;
  source_lang: string;
  target_lang: string;
  provider_config: Record<string, unknown> | null;
  created_at: string;
};

export type ProjectDraft = {
  name: string;
  source_lang: string;
  target_lang: string;
  provider_config?: Record<string, unknown> | null;
};

export type Segment = {
  id: string;
  order_index: number;
  source_text: string;
  target_text: string | null;
  status: SegmentStatus;
  error: string | null;
};

export type Chapter = {
  id: string;
  project_id: string;
  title: string;
  order_index: number;
  source_format: string;
  created_at: string;
  segments: Segment[];
};

export type TxtChapterDraft = {
  title: string;
  content: string;
};

export type ChapterTranslationReceipt = {
  chapter_id: string;
  enqueued: number;
};

export type SegmentTranslationDraft = {
  target_text: string | null;
};
