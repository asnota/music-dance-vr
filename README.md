# Music-to-Dance Generation for Creating an Immersive Music-Driven VR Experience

> **XR Metaverse Conference 2026 — Tallinn, Estonia**

This repository hosts a **Windows + [uv](https://github.com/astral-sh/uv)** adaptation of the [EDGE](https://github.com/Stanford-TML/EDGE) music-to-dance inference pipeline. It was developed as part of a VR application built for our paper to be presented at the **XR Metaverse Conference 2026** in Tallinn (June 16-19), titled *"Music-to-Dance Generation for Creating an Immersive Music-Driven VR Experience."*

## About the Project

The paper explores the maturity of music-to-dance generative models for artistic applications in immersive VR environments. We evaluate three representative models — **Bailando**, **EDGE**, and **LODGE** — by analysing the trade-off between motion quality and practical deployability in **Unreal Engine 5 (UE5)**. Outputs are assessed using automated metrics capturing distributional similarity, rhythm fidelity, diversity, and physical plausibility.

We find that, within current toolchain, **only EDGE supports a straightforward SMPL → FBX export and retargeting workflow into UE5**. To contextualise the practical outcome for immersive media, we also demonstrate a VR-ready case study that uses a marine scene and **Niagara particle effects** to mask residual animation limitations, accompanied by an original piano piece "Whale's hunt".

**Keywords:** music-to-dance generation; multimodal generative AI; music XR; VR.

## About This Repository

This repository provides a **fresh, from-scratch Windows adaptation** of the EDGE inference pipeline using the modern [uv](https://github.com/astral-sh/uv) package manager rather than conda.

An earlier Windows adaptation of EDGE (built with **conda**) was developed by **Yuhong Yuan** and is available here:  
👉 [Music-to-Dance-Models-Windows-Compatible-Deployment](https://github.com/yhongowo/Music-to-Dance-Models-Windows-Compatible-Deployment)

The present adaptation does **not** derive from that work — it has been re-engineered independently around `uv` for faster, reproducible, and dependency-isolated installs on Windows.

### Source Modifications

To ensure compatibility with the Windows + uv stack, the following EDGE source files have been modified:

| File | Purpose |
|------|---------|
| `Model.py` | Model definition adjustments |
| `Diffusion.py` | Diffusion process compatibility fixes |
| `Quaternion.py` | Rotation/quaternion math compatibility |
| `Vis.py` | Visualisation pipeline adaptations |

All other EDGE components remain untouched and are pulled from the [official Stanford-TML/EDGE repository](https://github.com/Stanford-TML/EDGE).

## What This Repository Provides

- 🪟 **Windows-native installation** instructions (no WSL, no conda required)
- ⚡ **`uv`-based environment management** for fast, reproducible installs
- 🔧 **Automated `setup.bat`** to install the full ML stack
- 🎵 **Automated `run_inference.bat`** to generate dance motions and export to `.fbx`
- 🧹 **`uninstall.bat`** for safe cleanup
- 🎮 **UE5 import guide** for integrating motion + audio into an immersive VR scene

---

## Citation

If you use this Windows adaptation or refer to the accompanying case study, please cite our paper (BibTeX will be provided after publication at XR Metaverse 2026).

---

> Below are the installation instructions.

---

## Quick Start with the Automated Setup Script

### Prerequisites
1. **Python 3.8.10** installed and added to PATH  
   → [Download here](https://www.python.org/downloads/release/python-3810/)
2. **Git** installed and available in PATH  
   → [Download here](https://git-scm.com/download/win)
3. **Microsoft MPI** (for mpi4py)  
   → [Download here](https://www.microsoft.com/en-us/download/details.aspx?id=57467)
4. **Blender 5.1** installed (for the FBX conversion step)

### How to Run the Setup Script

1. **Clone or download this repository:**
   ```cmd
   git clone https://github.com/asnota/music-dance-vr.git
   cd music-dance-vr
   ```

2. **Open Command Prompt as Administrator** in the repository folder.

3. **Run the setup script:**
   ```cmd
   setup.bat
   ```

4. **If UV was just installed**, the script will exit and prompt you to restart it.  
   Open a **new** Command Prompt window and run `setup.bat` again.

5. After completion:
   - Download the EDGE checkpoint from the [official repo](https://drive.google.com/file/d/1BAR712cVEqB8GR37fcEihRV_xOC-fZrZ/view?usp=share_link) and place it in:
     ```
     EDGE\checkpoint\checkpoint.pt
     ```
   - Drop your `.wav` files into:
     ```
     EDGE\custom_music\
     ```

### How to Run Inference

Once setup is finished, the checkpoint and music audio file are in place:

```cmd
run_inference.bat
```

The generated `.fbx` files will appear in `EDGE\SMPL-to-FBX\fbx_out\`.

> **Important:** If your Blender install path differs from `C:\Program Files\Blender Foundation\Blender 5.1\blender.exe`, edit `run_inference.bat` to match your installed version.

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `python is not recognized` | Reinstall Python 3.8.10 and check "Add Python to PATH" |
| `uv is not recognized` after install | Open a **new** Command Prompt window |
| `mpi4py` install fails | Install [Microsoft MPI](https://www.microsoft.com/en-us/download/details.aspx?id=57467) |
| Blender command fails | Update the Blender path inside `run_inference.bat` |
---

## Instructions to Run the Script outside of the `run_inference.bat`

### 1. Activate the Environment
From the git folder, run:
```cmd
edge-env3_8\Scripts\activate
```

### 2. Enter the EDGE Directory
```cmd
set CUDA_VISIBLE_DEVICES="" && cd EDGE
```

### 3. Generate Motion
Place your `.wav` files inside the `custom_music` folder (located in the EDGE root folder) and run:
```cmd
python test.py --music_dir custom_music/ --feature_type jukebox --checkpoint checkpoint/checkpoint.pt --save_motions && cd SMPL-to-FBX && for %I in (motions\*.pkl) do "C:\Program Files\Blender Foundation\Blender 5.1\blender.exe" --background --python blender_script.py -- --input "%I" --template ybot.fbx --output "fbx_out\%~nI.fbx" && cd ..
```


## Unreal Engine 5 integration
### 1. Copy generated files to Unreal Engine
Find your generated `.fbx` file and copy it (along with the original `.wav` file you used for generation) into the Unreal Engine `raw` folder.

### 2. Import into Unreal Engine 5
1. Open UE5 and the **Content Drawer**, then press **Import**.
2. Select your `.fbx` file.
3. In the import window, go to the **Skeletal Meshes** tab, then under **Skeleton**, choose `S_Dancer` from the drop-down menu.
4. Also import the audio file.

### 3. Configure the Dancer Blueprint
1. Navigate to the **Custom** folder in the Content Drawer.
2. Go to **BluePrints** and open `BP_Dancer`.
3. Replace the default music and animation references with your new files.
4. Press **Save** and **Compile**.

### 4. Run the Simulation
In the scene editor, click **Simulate** and watch your dancer move to your custom music!

---

## License
Refer to the original [EDGE repository](https://github.com/Stanford-TML/EDGE) for licensing information.
