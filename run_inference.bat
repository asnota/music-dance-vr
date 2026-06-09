@echo off
setlocal

REM ============================================================
REM  EDGE - Run Inference Script
REM ============================================================

echo Activating environment...
call edge-env3_8\Scripts\activate
if errorlevel 1 (
    echo [ERROR] Could not activate environment. Did you run setup.bat first?
    pause
    exit /b 1
)

set CUDA_VISIBLE_DEVICES=
cd EDGE

echo.
echo Running EDGE inference...
python test.py --music_dir custom_music/ --feature_type jukebox --checkpoint checkpoint/checkpoint.pt --save_motions
if errorlevel 1 (
    echo [ERROR] Inference failed.
    cd ..
    pause
    exit /b 1
)

echo.
echo Converting motions to FBX with Blender...
cd SMPL-to-FBX
for %%I in (motions\*.pkl) do (
    "C:\Program Files\Blender Foundation\Blender 5.1\blender.exe" --background --python blender_script.py -- --input "%%I" --template ybot.fbx --output "fbx_out\%%~nI.fbx"
)
cd ..\..

echo.
echo ============================================================
echo  Done! Generated FBX files are in EDGE\SMPL-to-FBX\fbx_out\
echo ============================================================
pause