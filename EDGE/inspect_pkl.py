import pickle
import numpy as np
import sys
import os

pkl_path = sys.argv[1] if len(sys.argv) > 1 else "SMPL-to-FBX/motions"

if os.path.isdir(pkl_path):
    files = [f for f in os.listdir(pkl_path) if f.endswith(".pkl")]
    pkl_path = os.path.join(pkl_path, files[0])
    print(f"Inspecting: {pkl_path}")

with open(pkl_path, "rb") as f:
    data = pickle.load(f)

print("\n=== KEYS ===")
print(list(data.keys()))

print("\n=== smpl_poses ===")
poses = data["smpl_poses"]
print(f"shape: {poses.shape}")
print(f"dtype: {poses.dtype}")
print(f"min/max: {poses.min():.4f} / {poses.max():.4f}")
print(f"mean abs: {np.abs(poses).mean():.4f}")
print(f"std per joint axis (first 9): {poses.std(axis=0)[:9]}")
print(f"\nFrame 0 (first 9 values - pelvis + L_hip + R_hip rotvecs):")
print(poses[0, :9])
print(f"\nFrame {len(poses)//2}:")
print(poses[len(poses)//2, :9])
print(f"\nFrame -1:")
print(poses[-1, :9])

# Variance check - if poses don't vary, joints don't move
variance_per_joint = poses.reshape(-1, 24, 3).std(axis=0).sum(axis=-1)
print(f"\n=== Variance per joint (24 joints) ===")
for i, v in enumerate(variance_per_joint):
    bar = "█" * int(v * 50)
    print(f"  Joint {i:2d}: {v:.4f}  {bar}")

print(f"\n=== smpl_trans ===")
trans = data["smpl_trans"]
print(f"shape: {trans.shape}")
print(f"range X: [{trans[:, 0].min():.3f}, {trans[:, 0].max():.3f}]")
print(f"range Y: [{trans[:, 1].min():.3f}, {trans[:, 1].max():.3f}]")
print(f"range Z: [{trans[:, 2].min():.3f}, {trans[:, 2].max():.3f}]")