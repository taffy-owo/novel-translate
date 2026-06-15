@echo off
cd /d "%~dp0"
echo Stopping docker services (postgres / redis / minio) ...
docker compose stop
echo.
echo Also close the "novel-translate API", "novel-translate Worker" and the
echo desktop (tauri) windows to fully stop everything.
pause
