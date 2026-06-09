@echo off
setlocal enabledelayedexpansion

REM ============================================================
REM  EDGE Model - Automated Setup Script
REM  Requires: Python 3.8.10 installed and available in PATH
REM ============================================================

echo.
echo ============================================================
echo  EDGE Model - Automated Setup
echo ============================================================
echo.

REM ---------- Check Python ----------
echo [1/8] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Please install Python 3.8.10 from:
    echo https://www.python.org/downloads/release/python-3810/
    pause
    exit /b 1
)

for /f "tokens=2" %%v in ('python --version 2^>^&1') do set PYVER=%%v
echo Found Python !PYVER!
echo.

REM ---------- Check / Install UV ----------
echo [2/8] Checking UV installation...
where uv >nul 2>&1
if errorlevel 1 (
    echo UV not found. Installing UV...
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    if errorlevel 1 (
        echo [ERROR] Failed to install UV.
        pause
        exit /b 1
    )
    echo.
    echo [WARNING] UV was just installed. You may need to restart this script
    echo so the new PATH variables take effect.
    pause
    exit /b 0
) else (
    echo UV is already installed.
)
echo.

REM ---------- Create venv ----------
echo [3/8] Creating UV virtual environment with Python 3.8...
if exist edge-env3_8 (
    echo Environment edge-env3_8 already exists, skipping creation.
) else (
    uv venv --python 3.8 edge-env3_8
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
)
echo.

REM ---------- Activate venv ----------
echo [4/8] Activating environment...
call edge-env3_8\Scripts\activate
if errorlevel 1 (
    echo [ERROR] Failed to activate environment.
    pause
    exit /b 1
)
echo.

REM ---------- Install core ML stack ----------
echo [5/8] Installing core ML dependencies...

echo  - Upgrading pip, setuptools, wheel...
uv pip install --upgrade pip setuptools==65.5.0 wheel
if errorlevel 1 goto :install_error

echo  - Installing core scientific libraries...
uv pip install numpy==1.21.6 scipy==1.7.3 tqdm==4.45.0 soundfile==0.10.3.post1 librosa==0.7.2 mpi4py==3.1.4 wandb==0.13.11 matplotlib==3.7.5 einops==0.7.0 p-tqdm==1.4.0
if errorlevel 1 goto :install_error

echo  - Installing llvmlite and numba (no isolation)...
uv pip install llvmlite==0.31.0 numba==0.48.0 --no-build-isolation
if errorlevel 1 goto :install_error
echo.

REM ---------- Jukebox ----------
echo [6/8] Installing Jukebox...
if exist jukebox (
    echo Jukebox repo already cloned, skipping clone.
) else (
    git clone https://github.com/openai/jukebox.git
    if errorlevel 1 goto :install_error
)
cd jukebox
uv pip install -e . --no-build-isolation
if errorlevel 1 (
    cd ..
    goto :install_error
)
python -c "import jukebox; print('Jukebox import OK')"
if errorlevel 1 (
    cd ..
    goto :install_error
)
cd ..
echo.

REM ---------- PyTorch ----------
echo [7/8] Installing PyTorch (CUDA 11.6)...
uv pip install torch==1.12.1+cu116 torchvision==0.13.1+cu116 torchaudio==0.12.1 --index-url https://download.pytorch.org/whl/cu116
if errorlevel 1 goto :install_error

echo  - Installing jukemirlib...
uv pip install git+https://github.com/rodrigo-castellon/jukemirlib.git
if errorlevel 1 goto :install_error
echo.

REM ---------- Clone EDGE ----------
echo [8/8] Cloning EDGE repository...
if exist EDGE (
    echo EDGE repo already exists, skipping clone.
) else (
    git clone https://github.com/Stanford-TML/EDGE.git
    if errorlevel 1 goto :install_error
)

REM ---------- Create checkpoint folder ----------
if not exist EDGE\checkpoint (
    mkdir EDGE\checkpoint
    echo Created folder: EDGE\checkpoint
)

REM ---------- Create custom_music folder ----------
if not exist EDGE\custom_music (
    mkdir EDGE\custom_music
    echo Created folder: EDGE\custom_music
)

echo.
echo ============================================================
echo  Setup completed successfully!
echo ============================================================
echo.
echo NEXT STEPS:
echo  1. Download the EDGE checkpoint and place it in:
echo       EDGE\checkpoint\checkpoint.pt
echo     Download link: https://drive.google.com/file/d/1BAR712cVEqB8GR37fcEihRV_xOC-fZrZ/view?usp=share_link
echo.
echo  2. Place your .wav files inside:
echo       EDGE\custom_music\
echo.
echo  3. Run inference using run_inference.bat (or follow README).
echo.
pause
exit /b 0

:install_error
echo.
echo ============================================================
echo  [ERROR] Installation failed at one of the steps above.
echo  Please review the messages and try again.
echo ============================================================
pause
exit /b 1