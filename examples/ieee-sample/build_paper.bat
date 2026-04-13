@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
pushd "%SCRIPT_DIR%"

call :resolve_tex_tool pdflatex PDFLATEX
if errorlevel 1 exit /b 1

call :resolve_tex_tool bibtex BIBTEX
if errorlevel 1 exit /b 1

if not exist build mkdir build
if not exist build_tmp mkdir build_tmp

del /q build_tmp\main.aux build_tmp\main.bbl build_tmp\main.blg build_tmp\main.log build_tmp\main.out build_tmp\main.toc build_tmp\main.pdf build_tmp\main.synctex.gz 2>nul

"%PDFLATEX%" -interaction=nonstopmode -synctex=0 -file-line-error -output-directory=build_tmp main.tex
if errorlevel 1 exit /b %errorlevel%

findstr /R /C:"\\cite{" /C:"\\nocite{" main.tex >nul
if %errorlevel%==0 (
    "%BIBTEX%" build_tmp\main
    if errorlevel 1 exit /b %errorlevel%
)

"%PDFLATEX%" -interaction=nonstopmode -synctex=0 -file-line-error -output-directory=build_tmp main.tex
if errorlevel 1 exit /b %errorlevel%

"%PDFLATEX%" -interaction=nonstopmode -synctex=0 -file-line-error -output-directory=build_tmp main.tex
if errorlevel 1 exit /b %errorlevel%

copy /y build_tmp\main.pdf build\main.pdf >nul
copy /y build_tmp\main.pdf build\main_preview.pdf >nul
copy /y build_tmp\main.log build\main.log >nul
copy /y build_tmp\main.aux build\main.aux >nul
copy /y build_tmp\main.bbl build\main.bbl >nul 2>nul
copy /y build_tmp\main.blg build\main.blg >nul 2>nul

popd
exit /b 0

:resolve_tex_tool
set "TOOL_NAME=%~1"
set "OUTPUT_VAR=%~2"

for %%I in (%TOOL_NAME%) do set "CANDIDATE=%%~$PATH:I"
if defined CANDIDATE (
    set "%OUTPUT_VAR%=%CANDIDATE%"
    exit /b 0
)

set "MIKTEX_LOCAL=%LOCALAPPDATA%\Programs\MiKTeX\miktex\bin\x64\%TOOL_NAME%.exe"
if exist "%MIKTEX_LOCAL%" (
    set "%OUTPUT_VAR%=%MIKTEX_LOCAL%"
    exit /b 0
)

set "MIKTEX_PROGRAM=%ProgramFiles%\MiKTeX\miktex\bin\x64\%TOOL_NAME%.exe"
if exist "%MIKTEX_PROGRAM%" (
    set "%OUTPUT_VAR%=%MIKTEX_PROGRAM%"
    exit /b 0
)

set "MIKTEX_PROGRAM_X86=%ProgramFiles(x86)%\MiKTeX\miktex\bin\x64\%TOOL_NAME%.exe"
if exist "%MIKTEX_PROGRAM_X86%" (
    set "%OUTPUT_VAR%=%MIKTEX_PROGRAM_X86%"
    exit /b 0
)

echo Could not find %TOOL_NAME%. Please install MiKTeX or TeX Live and make sure %TOOL_NAME% is available.
exit /b 1
