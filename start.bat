@echo off
setlocal
cd /d "%~dp0"

echo ===========================================================
echo   novel-translate  one-click launcher
echo   Prerequisite: Docker Desktop is running; uv / pnpm installed.
echo ===========================================================
echo.

echo [1/4] Starting postgres / redis / minio ...
docker compose up -d postgres redis minio
if errorlevel 1 (
  echo.
  echo [ERROR] Could not start docker services. Open Docker Desktop first, then retry.
  pause
  exit /b 1
)

echo [2/4] Applying database migration ...
pushd backend
call uv run alembic upgrade head
popd

echo [3/4] Starting backend API and worker (each opens its own window) ...
start "novel-translate API" cmd /k "cd /d %~dp0backend&&uv run uvicorn novel_translate.api.main:app --host 127.0.0.1 --port 8000"
rem Worker calls the model gateway through the local proxy. Adjust/remove these two
rem set lines if your proxy differs or you use a direct (no-proxy) model endpoint.
start "novel-translate Worker" cmd /k "cd /d %~dp0backend&&set HTTPS_PROXY=http://127.0.0.1:7897&&set ALL_PROXY=socks5://127.0.0.1:7897&&uv run arq novel_translate.worker.main.WorkerSettings"

echo [4/4] Starting desktop app (FIRST run compiles Rust; the window may take 1-2 min) ...
echo.
pnpm --filter desktop tauri dev

endlocal
