import { useState } from "react";
import { Link, useParams } from "react-router-dom";
import {
  useApproveTerm,
  useCreateTerm,
  useExtractTerms,
  useGlossary,
  useUpdateTerm
} from "../api/hooks";
import type { GlossaryTerm, TermConstraint, TermStatus } from "../api/types";

const statusLabels: Record<TermStatus, string> = {
  draft: "草稿",
  approved: "已审批",
  deprecated: "已弃用"
};
const constraintLabels: Record<TermConstraint, string> = { hard: "硬约束", soft: "软约束" };

function TermRow({ projectId, term }: { projectId: string; term: GlossaryTerm }) {
  const updateTerm = useUpdateTerm(projectId);
  const approveTerm = useApproveTerm(projectId);
  const [target, setTarget] = useState(term.target);
  const dirty = target !== term.target;

  return (
    <tr className="border-b border-stone-100 last:border-b-0">
      <td className="px-3 py-2 align-middle text-sm text-ink-900">{term.source}</td>
      <td className="px-3 py-2 align-middle">
        <input
          className="w-full rounded-md border border-stone-300 bg-stone-50 px-2 py-1 text-sm outline-none transition focus:border-stone-500 focus:bg-white"
          value={target}
          placeholder="填写译名"
          onChange={(event) => setTarget(event.target.value)}
        />
      </td>
      <td className="px-3 py-2 align-middle text-xs text-ink-500">
        {constraintLabels[term.constraint_kind]}
      </td>
      <td className="px-3 py-2 align-middle text-xs text-ink-700">{statusLabels[term.status]}</td>
      <td className="px-3 py-2 align-middle">
        <div className="flex gap-2">
          <button
            type="button"
            className="h-8 rounded-md border border-stone-300 bg-white px-2 text-xs transition hover:bg-stone-50 disabled:cursor-not-allowed disabled:text-ink-500"
            disabled={!dirty || updateTerm.isPending}
            onClick={() => updateTerm.mutate({ termId: term.id, target })}
          >
            保存
          </button>
          <button
            type="button"
            className="h-8 rounded-md border border-stone-300 bg-white px-2 text-xs transition hover:bg-stone-50 disabled:cursor-not-allowed disabled:text-ink-500"
            disabled={term.status === "approved" || target.trim() === "" || approveTerm.isPending}
            onClick={() => approveTerm.mutate(term.id)}
          >
            审批
          </button>
        </div>
      </td>
    </tr>
  );
}

export function GlossaryPage() {
  const { projectId } = useParams();
  const glossaryQuery = useGlossary(projectId);
  const createTerm = useCreateTerm(projectId);
  const extractTerms = useExtractTerms(projectId);
  const [source, setSource] = useState("");
  const [target, setTarget] = useState("");
  const [constraint, setConstraint] = useState<TermConstraint>("soft");
  const [message, setMessage] = useState<string | null>(null);

  function addTerm() {
    if (source.trim() === "" || target.trim() === "" || createTerm.isPending) {
      return;
    }
    createTerm.mutate(
      { source: source.trim(), target: target.trim(), constraint_kind: constraint },
      {
        onSuccess: () => {
          setSource("");
          setTarget("");
          setMessage("已添加术语");
        }
      }
    );
  }

  function extractCandidates() {
    setMessage(null);
    extractTerms.mutate(undefined, {
      onSuccess: (created) => setMessage(`抽取到 ${created.length} 个候选术语，请补全译名后审批`)
    });
  }

  const terms = glossaryQuery.data ?? [];
  const loadError = glossaryQuery.error instanceof Error ? glossaryQuery.error.message : null;
  const createError = createTerm.error instanceof Error ? createTerm.error.message : null;

  return (
    <div className="space-y-5">
      <div className="flex flex-wrap items-start justify-between gap-4 rounded-lg border border-stone-200 bg-white p-4 shadow-sm">
        <div className="min-w-0">
          {projectId !== undefined && (
            <Link to={`/projects/${projectId}`} className="text-sm text-ink-500 hover:text-ink-900">
              项目
            </Link>
          )}
          <h1 className="mt-1 text-xl font-semibold">术语表</h1>
          <div className="mt-1 text-sm text-ink-500">
            已审批且出现在段落中的术语会注入翻译，约束模型用词一致。
          </div>
        </div>
        <button
          type="button"
          className="h-10 rounded-md border border-stone-300 bg-white px-4 text-sm font-medium transition hover:bg-stone-50 disabled:cursor-not-allowed disabled:text-ink-500"
          disabled={extractTerms.isPending}
          onClick={extractCandidates}
        >
          从原文抽取候选
        </button>
      </div>

      {(message || loadError || createError) && (
        <div
          className={`rounded-lg border px-4 py-3 text-sm ${
            loadError || createError
              ? "border-red-200 bg-red-50 text-red-700"
              : "border-emerald-200 bg-emerald-50 text-emerald-800"
          }`}
        >
          {loadError ?? createError ?? message}
        </div>
      )}

      <div className="rounded-lg border border-stone-200 bg-white p-4 shadow-sm">
        <div className="flex flex-wrap items-end gap-3">
          <label className="flex flex-col gap-1 text-xs text-ink-500">
            原文词
            <input
              className="h-9 w-44 rounded-md border border-stone-300 px-2 text-sm outline-none focus:border-stone-500"
              value={source}
              onChange={(event) => setSource(event.target.value)}
            />
          </label>
          <label className="flex flex-col gap-1 text-xs text-ink-500">
            译名
            <input
              className="h-9 w-44 rounded-md border border-stone-300 px-2 text-sm outline-none focus:border-stone-500"
              value={target}
              onChange={(event) => setTarget(event.target.value)}
            />
          </label>
          <label className="flex flex-col gap-1 text-xs text-ink-500">
            约束
            <select
              className="h-9 rounded-md border border-stone-300 px-2 text-sm outline-none focus:border-stone-500"
              value={constraint}
              onChange={(event) => setConstraint(event.target.value as TermConstraint)}
            >
              <option value="soft">软约束</option>
              <option value="hard">硬约束</option>
            </select>
          </label>
          <button
            type="button"
            className="h-9 rounded-md bg-ink-900 px-4 text-sm font-medium text-white transition hover:bg-black disabled:cursor-not-allowed disabled:bg-stone-400"
            disabled={createTerm.isPending}
            onClick={addTerm}
          >
            添加
          </button>
        </div>
      </div>

      <section className="overflow-hidden rounded-lg border border-stone-200 bg-white shadow-sm">
        <table className="w-full table-auto">
          <thead>
            <tr className="border-b border-stone-200 bg-stone-50 text-left text-xs font-semibold text-ink-700">
              <th className="px-3 py-2">原文</th>
              <th className="px-3 py-2">译名</th>
              <th className="px-3 py-2">约束</th>
              <th className="px-3 py-2">状态</th>
              <th className="px-3 py-2">操作</th>
            </tr>
          </thead>
          <tbody>
            {terms.length === 0 ? (
              <tr>
                <td colSpan={5} className="px-3 py-4 text-sm text-ink-500">
                  暂无术语，可手动添加或从原文抽取候选
                </td>
              </tr>
            ) : (
              terms.map((term) => (
                <TermRow key={term.id} projectId={projectId ?? ""} term={term} />
              ))
            )}
          </tbody>
        </table>
      </section>
    </div>
  );
}
