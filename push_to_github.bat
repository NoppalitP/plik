@echo off
echo ========================================================
echo   Plik - One-Click Push to GitHub (NoppalitP/plik)
echo ========================================================
echo.
cd /d D:\plik
echo Pushing branch 'main' and tags 'v1.0.0' to GitHub...
git push -u origin main --tags
echo.
if %ERRORLEVEL% EQU 0 (
    echo [SUCCESS] Pushed to https://github.com/NoppalitP/plik successfully!
    echo GitHub Actions CI/CD will now automatically build and publish release v1.0.0.
) else (
    echo [ERROR] Failed to push. Make sure you have created the repository:
    echo https://github.com/new with name 'plik' under account 'NoppalitP'.
)
echo.
pause
