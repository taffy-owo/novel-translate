import { Link, Outlet } from "react-router-dom";

export function AppLayout() {
  return (
    <div className="min-h-screen bg-stone-100 text-ink-900">
      <header className="border-b border-stone-200 bg-white">
        <div className="mx-auto flex w-full max-w-7xl items-center justify-between px-5 py-4">
          <Link to="/" className="text-base font-semibold">
            novel-translate
          </Link>
          <div className="text-sm text-ink-500">桌面工作台</div>
        </div>
      </header>
      <main className="mx-auto w-full max-w-7xl px-5 py-5">
        <Outlet />
      </main>
    </div>
  );
}
