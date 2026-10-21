@echo off
REM run-bahmni.cmd - Bahmni Startup with Automatic Port Detection (80 vs 8186)
setlocal enabledelayedexpansion

if "%PROXY_PORT%"=="" (
    netstat -ano | findstr /R /C:":80 " >nul 2>&1
    if !errorlevel! equ 0 (
        echo [INFO] Port 80 is occupied by another application. Using port 8186 for Bahmni Proxy.
        set PROXY_PORT=8186
    ) else (
        echo [INFO] Port 80 is free. Using default port 80 (http://localhost/) for Bahmni Proxy.
        set PROXY_PORT=80
    )
) else (
    echo [INFO] PROXY_PORT explicitly set to: %PROXY_PORT%
)

cd /d "%~dp0bahmni-docker\bahmni-standard"
echo [INFO] Starting Bahmni containers (Port: %PROXY_PORT%)...
docker compose up -d %*
endlocal
