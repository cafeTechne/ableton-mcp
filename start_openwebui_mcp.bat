@echo off
echo ========================================
echo   Ableton MCP + OpenWebUI Starter
echo ========================================
echo.

echo [1/2] Starting MCP Server on port 8000...
start "MCP Server" cmd /k "cd /d %~dp0 && python MCP_Server/server.py --transport sse --port 8000"
timeout /t 3 /nobreak > nul

echo [2/2] Starting MCPO Proxy on port 8001...
start "MCPO Proxy" cmd /k "cd /d %~dp0 && python start_mcpo.py"

echo.
echo ========================================
echo   Both servers started!
echo ========================================
echo.
echo In OpenWebUI:
echo   1. Go to: Workspace ^> Tools ^> Add Tool (+)
echo   2. Add URL: http://host.docker.internal:8001/openapi.json
echo.
echo Test in browser: http://localhost:8001/docs
echo.
pause
