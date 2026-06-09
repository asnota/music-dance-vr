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
### 1. Copy generated files to Unreal Engine project
Find your generated `.fbx` file and copy it (along with the original `.wav` file you used for generation) into the VRTemplate's `raw` folder.

### 2. Import into Unreal Engine 5
1. Double-click the VRTemplate.uproject inside VRTemplate folder to open the project
2. From the **Content Drawer** press **Import**.
3. Select your `.fbx` file.
4. In the import window, go to the **Skeletal Meshes** tab, then under **Skeleton**, choose `S_Dancer` from the drop-down menu.
5. Also import the audio file.

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
