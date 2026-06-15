import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { createBrowserRouter, RouterProvider } from "react-router-dom";
import "./index.css";
import { AppLayout } from "./pages/AppLayout";
import { ChapterWorkspacePage } from "./pages/ChapterWorkspacePage";
import { GlossaryPage } from "./pages/GlossaryPage";
import { ProjectDetailPage } from "./pages/ProjectDetailPage";
import { ProjectListPage } from "./pages/ProjectListPage";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      staleTime: 1000
    }
  }
});

const router = createBrowserRouter([
  {
    path: "/",
    element: <AppLayout />,
    children: [
      {
        index: true,
        element: <ProjectListPage />
      },
      {
        path: "projects/:projectId",
        element: <ProjectDetailPage />
      },
      {
        path: "chapters/:chapterId",
        element: <ChapterWorkspacePage />
      },
      {
        path: "projects/:projectId/glossary",
        element: <GlossaryPage />
      }
    ]
  }
]);

const rootElement = document.getElementById("root");

if (rootElement === null) {
  throw new Error("Root element #root is missing");
}

createRoot(rootElement).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <RouterProvider router={router} />
    </QueryClientProvider>
  </StrictMode>
);
