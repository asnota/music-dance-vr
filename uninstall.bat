@echo off
setlocal enabledelayedexpansion

REM ============================================================
REM  EDGE Model - Uninstall / Cleanup Script
REM ============================================================

echo.
echo ============================================================
echo  EDGE Model - Uninstall / Cleanup
echo ============================================================
echo.
echo This script will help you remove components installed by setup.bat
echo.
echo Choose what you want to remove:
echo.
echo   [1] Deactivate environment only (safe, removes nothing)
echo   [2] Remove virtual environment (edge-env3_8) only
echo   [3] Remove Jukebox repository only
echo   [4] Remove EDGE repository only (KEEPS your checkpoint and music!)
echo   [5] Remove EDGE repository INCLUDING checkpoint and custom_music
echo   [6] FULL cleanup (venv + Jukebox + EDGE, keeps checkpoints/music)
echo   [7] NUCLEAR cleanup (removes EVERYTHING including checkpoints/music)
echo   [8] Uninstall UV from system
echo   [0] Exit without changes
echo.
set /p CHOICE="Enter your choice (0-8): "

if "%CHOICE%"=="0" goto :end
if "%CHOICE%"=="1" goto :deactivate_only
if "%CHOICE%"=="2" goto :remove_venv
if "%CHOICE%"=="3" goto :remove_jukebox
if "%CHOICE%"=="4" goto :remove_edge_safe
if "%CHOICE%"=="5" goto :remove_edge_full
if "%CHOICE%"=="6" goto :full_cleanup
if "%CHOICE%"=="7" goto :nuclear_cleanup
if "%CHOICE%"=="8" goto :uninstall_uv

echo Invalid choice.
pause
exit /b 1

REM ============================================================
:deactivate_only
echo.
echo Attempting to deactivate environment...
call edge-env3_8\Scripts\deactivate.bat 2>nul
if defined VIRTUAL_ENV (
    call deactivate 2>nul
)
echo Done. Environment deactivated (if it was active).
goto :end

REM ============================================================
:remove_venv
echo.
echo This will remove the folder: edge-env3_8
set /p CONFIRM="Are you sure? (Y/N): "
if /i not "!CONFIRM!"=="Y" goto :end

call :deactivate_silent

if exist edge-env3_8 (
    echo Removing edge-env3_8...
    rmdir /s /q edge-env3_8
    if errorlevel 1 (
        echo [ERROR] Failed to remove edge-env3_8. 
        echo It may be in use. Close all terminals using it and try again.
        pause
        exit /b 1
    )
    echo Removed edge-env3_8.
) else (
    echo edge-env3_8 does not exist.
)
goto :end

REM ============================================================
:remove_jukebox
echo.
echo This will remove the folder: jukebox
set /p CONFIRM="Are you sure? (Y/N): "
if /i not "!CONFIRM!"=="Y" goto :end

if exist jukebox (
    echo Removing jukebox...
    rmdir /s /q jukebox
    echo Removed jukebox.
) else (
    echo jukebox does not exist.
)
goto :end

REM ============================================================
:remove_edge_safe
echo.
echo This will remove the EDGE folder BUT preserve:
echo   - EDGE\checkpoint\  (your model checkpoint)
echo   - EDGE\custom_music\  (your input audio files)
echo   - EDGE\SMPL-to-FBX\fbx_out\  (generated FBX outputs)
echo.
set /p CONFIRM="Continue? (Y/N): "
if /i not "!CONFIRM!"=="Y" goto :end

call :backup_user_data

if exist EDGE (
    echo Removing EDGE...
    rmdir /s /q EDGE
    if errorlevel 1 (
        echo [ERROR] Failed to remove EDGE.
        pause
        exit /b 1
    )
    echo Removed EDGE.
) else (
    echo EDGE does not exist.
)

call :restore_user_data
goto :end

REM ============================================================
:remove_edge_full
echo.
echo [WARNING] This will remove the EDGE folder INCLUDING:
echo   - Your downloaded checkpoint
echo   - Your custom music files
echo   - Any generated FBX outputs
echo.
set /p CONFIRM="Are you ABSOLUTELY sure? (Y/N): "
if /i not "!CONFIRM!"=="Y" goto :end

if exist EDGE (
    echo Removing EDGE (full)...
    rmdir /s /q EDGE
    echo Removed EDGE.
) else (
    echo EDGE does not exist.
)
goto :end

REM ============================================================
:full_cleanup
echo.
echo This will remove:
echo   - edge-env3_8 (virtual environment)
echo   - jukebox (repo)
echo   - EDGE (repo, but PRESERVES checkpoint, custom_music, fbx_out)
echo.
set /p CONFIRM="Continue? (Y/N): "
if /i not "!CONFIRM!"=="Y" goto :end

call :deactivate_silent
call :backup_user_data

if exist edge-env3_8 (
    echo Removing edge-env3_8...
    rmdir /s /q edge-env3_8
)
if exist jukebox (
    echo Removing jukebox...
    rmdir /s /q jukebox
)
if exist EDGE (
    echo Removing EDGE...
    rmdir /s /q EDGE
)

call :restore_user_data

echo.
echo Full cleanup complete. Your user data has been preserved in:
echo   _backup_checkpoint\
echo   _backup_custom_music\
echo   _backup_fbx_out\
goto :end

REM ============================================================
:nuclear_cleanup
echo.
echo [WARNING] NUCLEAR CLEANUP will remove ALL of the following:
echo   - edge-env3_8
echo   - jukebox
echo   - EDGE (including checkpoint, custom_music, and FBX outputs)
echo.
echo This action CANNOT be undone!
echo.
set /p CONFIRM="Type DELETE to confirm: "
if not "!CONFIRM!"=="DELETE" (
    echo Confirmation failed. Aborting.
    goto :end
)

call :deactivate_silent

if exist edge-env3_8 (
    echo Removing edge-env3_8...
    rmdir /s /q edge-env3_8
)
if exist jukebox (
    echo Removing jukebox...
    rmdir /s /q jukebox
)
if exist EDGE (
    echo Removing EDGE...
    rmdir /s /q EDGE
)

echo.
echo Nuclear cleanup complete. Everything has been removed.
goto :end

REM ============================================================
:uninstall_uv
echo.
echo This will uninstall UV from your system.
echo UV is installed per-user at: %USERPROFILE%\.local\bin\uv.exe
echo.
set /p CONFIRM="Continue? (Y/N): "
if /i not "!CONFIRM!"=="Y" goto :end

if exist "%USERPROFILE%\.local\bin\uv.exe" (
    del /q "%USERPROFILE%\.local\bin\uv.exe"
    echo Removed uv.exe.
) else (
    echo uv.exe not found at default location.
)

if exist "%USERPROFILE%\.local\bin\uvx.exe" (
    del /q "%USERPROFILE%\.local\bin\uvx.exe"
    echo Removed uvx.exe.
)

if exist "%USERPROFILE%\.cache\uv" (
    echo Removing UV cache...
    rmdir /s /q "%USERPROFILE%\.cache\uv"
    echo Removed UV cache.
)

echo.
echo UV has been uninstalled.
echo You may also want to remove %USERPROFILE%\.local\bin from your PATH.
goto :end

REM ============================================================
REM  Helper subroutines
REM ============================================================

:deactivate_silent
if defined VIRTUAL_ENV (
    call deactivate 2>nul
)
exit /b 0

:backup_user_data
echo Backing up user data...
if exist EDGE\checkpoint (
    if not exist _backup_checkpoint (
        move /y EDGE\checkpoint _backup_checkpoint >nul
        echo  - Backed up checkpoint to _backup_checkpoint\
    )
)
if exist EDGE\custom_music (
    if not exist _backup_custom_music (
        move /y EDGE\custom_music _backup_custom_music >nul
        echo  - Backed up custom_music to _backup_custom_music\
    )
)
if exist EDGE\SMPL-to-FBX\fbx_out (
    if not exist _backup_fbx_out (
        move /y EDGE\SMPL-to-FBX\fbx_out _backup_fbx_out >nul
        echo  - Backed up fbx_out to _backup_fbx_out\
    )
)
exit /b 0

:restore_user_data
echo Restoring user data...
if exist _backup_checkpoint (
    if not exist EDGE mkdir EDGE
    move /y _backup_checkpoint EDGE\checkpoint >nul 2>&1
    echo  - Restored checkpoint
)
if exist _backup_custom_music (
    if not exist EDGE mkdir EDGE
    move /y _backup_custom_music EDGE\custom_music >nul 2>&1
    echo  - Restored custom_music
)
if exist _backup_fbx_out (
    if not exist EDGE\SMPL-to-FBX mkdir EDGE\SMPL-to-FBX
    move /y _backup_fbx_out EDGE\SMPL-to-FBX\fbx_out >nul 2>&1
    echo  - Restored fbx_out
)
exit /b 0

REM ============================================================
:end
echo.
echo ============================================================
echo  Cleanup script finished.
echo ============================================================
pause
exit /b 0