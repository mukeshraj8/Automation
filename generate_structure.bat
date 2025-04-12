@echo off
setlocal EnableDelayedExpansion

REM === Set your source directory here ===
set "SOURCE_DIR=D:\Automation\JobAgentBotV2"

REM === Output recreation batch script ===
set "OUTPUT_SCRIPT=recreate_structure.bat"
echo @echo off > "%OUTPUT_SCRIPT%"
echo REM === Auto-generated script to recreate folder structure and placeholder files === >> "%OUTPUT_SCRIPT%"
echo. >> "%OUTPUT_SCRIPT%"

REM === Generate folder creation commands, excluding specific folders ===
for /d /r "%SOURCE_DIR%" %%D in (*) do (
    set "FOLDER=%%~fD"
    set "REL_FOLDER=!FOLDER:%SOURCE_DIR%=!"
    
    echo !REL_FOLDER! | findstr /I /C:"\venv" /C:"\__pycache__" >nul
    if errorlevel 1 (
        if NOT "!REL_FOLDER!"=="" (
            echo mkdir "JobAgentBotV2!REL_FOLDER!" >> "%OUTPUT_SCRIPT%"
        )
    )
)

REM === Generate file creation commands, excluding certain files and folders ===
for /R "%SOURCE_DIR%" %%F in (*) do (
    set "FILE=%%~fF"
    set "REL_PATH=!FILE:%SOURCE_DIR%=!"
    set "EXT=%%~xF"

    REM === Check for excluded folders and extensions ===
    echo !REL_PATH! | findstr /I /C:"\venv" /C:"\__pycache__" >nul
    if errorlevel 1 (
        if /I not "!EXT!"==".log" if /I not "!EXT!"==".csv" if /I not "!EXT!"==".pyc" if /I not "!EXT!"==".pyo" if /I not "!EXT!"==".swp" if /I not "!EXT!"==".tmp" (
            echo type nul ^> "JobAgentBotV2!REL_PATH!" >> "%OUTPUT_SCRIPT%"
        )
    )
)

echo. >> "%OUTPUT_SCRIPT%"
echo echo Structure recreated successfully. >> "%OUTPUT_SCRIPT%"
echo pause >> "%OUTPUT_SCRIPT%"

echo === ✅ Script generated: %OUTPUT_SCRIPT% ===
