import type { FormEvent } from "react";
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useCreateProject, useProjects } from "../api/hooks";
import type { Project } from "../api/types";

const dateFormatter = new Intl.DateTimeFormat("zh-CN", {
  dateStyle: "medium",
  timeStyle: "short"
});

function formatProjectTime(project: Project): string {
  return dateFormatter.format(new Date(project.created_at));
}

export function ProjectListPage() {
  const navigate = useNavigate();
  const projectsQuery = useProjects();
  const createProject = useCreateProject();
  const [projectName, setProjectName] = useState("");
  const [sourceLang, setSourceLang] = useState("ja");
  const [targetLang, setTargetLang] = useState("zh-CN");

  function submitProjectForm(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const trimmedProjectName = projectName.trim();
    const trimmedSourceLang = sourceLang.trim();
    const trimmedTargetLang = targetLang.trim();

    if (trimmedProjectName.length === 0 || trimmedSourceLang.length === 0 || trimmedTargetLang.length === 0) {
      return;
    }

    createProject.mutate(
      {
        name: trimmedProjectName,
        source_lang: trimmedSourceLang,
        target_lang: trimmedTargetLang,
        provider_config: null
      },
      {
        onSuccess: (createdProject) => {
          setProjectName("");
          navigate(`/projects/${createdProject.id}`);
        }
      }
    );
  }

  const projectEntries = projectsQuery.data ?? [];
  const projectsMessage = projectsQuery.error instanceof Error ? projectsQuery.error.message : null;
  const creationMessage =
    createProject.error instanceof Error ? createProject.error.message : null;

  return (
    <div className="grid gap-5 lg:grid-cols-[360px_minmax(0,1fr)]">
      <section className="rounded-lg border border-stone-200 bg-white p-4 shadow-sm">
        <h1 className="text-lg font-semibold">新建项目</h1>
        <form className="mt-4 space-y-4" onSubmit={submitProjectForm}>
          <label className="block">
            <span className="text-sm font-medium text-ink-700">项目名称</span>
            <input
              className="mt-1 h-10 w-full rounded-md border border-stone-300 bg-white px-3 text-sm outline-none transition focus:border-stone-500 focus:ring-2 focus:ring-stone-200"
              value={projectName}
              onChange={(event) => setProjectName(event.target.value)}
              required
            />
          </label>
          <div className="grid grid-cols-2 gap-3">
            <label className="block">
              <span className="text-sm font-medium text-ink-700">源语言</span>
              <input
                className="mt-1 h-10 w-full rounded-md border border-stone-300 bg-white px-3 text-sm outline-none transition focus:border-stone-500 focus:ring-2 focus:ring-stone-200"
                value={sourceLang}
                onChange={(event) => setSourceLang(event.target.value)}
                required
              />
            </label>
            <label className="block">
              <span className="text-sm font-medium text-ink-700">目标语言</span>
              <input
                className="mt-1 h-10 w-full rounded-md border border-stone-300 bg-white px-3 text-sm outline-none transition focus:border-stone-500 focus:ring-2 focus:ring-stone-200"
                value={targetLang}
                onChange={(event) => setTargetLang(event.target.value)}
                required
              />
            </label>
          </div>
          <button
            className="h-10 w-full rounded-md bg-ink-900 px-4 text-sm font-medium text-white transition hover:bg-black disabled:cursor-not-allowed disabled:bg-stone-400"
            type="submit"
            disabled={createProject.isPending}
          >
            新建
          </button>
          {creationMessage && <p className="text-sm text-red-700">{creationMessage}</p>}
        </form>
      </section>

      <section className="min-w-0 rounded-lg border border-stone-200 bg-white shadow-sm">
        <div className="flex items-center justify-between border-b border-stone-200 px-4 py-3">
          <h2 className="text-lg font-semibold">项目</h2>
          <span className="text-sm text-ink-500">{projectEntries.length}</span>
        </div>
        {projectsQuery.isLoading ? (
          <div className="p-4 text-sm text-ink-500">加载中</div>
        ) : projectsMessage ? (
          <div className="p-4 text-sm text-red-700">{projectsMessage}</div>
        ) : projectEntries.length === 0 ? (
          <div className="p-4 text-sm text-ink-500">暂无项目</div>
        ) : (
          <div className="divide-y divide-stone-100">
            {projectEntries.map((project) => (
              <Link
                key={project.id}
                to={`/projects/${project.id}`}
                className="block px-4 py-4 transition hover:bg-stone-50"
              >
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <div className="min-w-0">
                    <div className="truncate text-sm font-semibold">{project.name}</div>
                    <div className="mt-1 text-xs text-ink-500">
                      {project.source_lang} → {project.target_lang}
                    </div>
                  </div>
                  <div className="text-xs text-ink-500">{formatProjectTime(project)}</div>
                </div>
              </Link>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
