"""
SMPL pkl → FBX using Blender's bpy.
Run with: blender --background --python blender_script.py -- --input motion.pkl --template ybot.fbx --output out.fbx
"""

import bpy
import sys
import os
import pickle
import argparse
import numpy as np
from mathutils import Quaternion, Vector, Matrix


SMPL_JOINTS = [
    "m_avg_Pelvis", "m_avg_L_Hip", "m_avg_R_Hip", "m_avg_Spine1",
    "m_avg_L_Knee", "m_avg_R_Knee", "m_avg_Spine2", "m_avg_L_Ankle",
    "m_avg_R_Ankle", "m_avg_Spine3", "m_avg_L_Foot", "m_avg_R_Foot",
    "m_avg_Neck", "m_avg_L_Collar", "m_avg_R_Collar", "m_avg_Head",
    "m_avg_L_Shoulder", "m_avg_R_Shoulder", "m_avg_L_Elbow", "m_avg_R_Elbow",
    "m_avg_L_Wrist", "m_avg_R_Wrist", "m_avg_L_Hand", "m_avg_R_Hand",
]


def axis_angle_to_quat(rotvec):
    """rotvec (3,) numpy -> mathutils.Quaternion"""
    angle = float(np.linalg.norm(rotvec))
    if angle < 1e-8:
        return Quaternion((1.0, 0.0, 0.0, 0.0))
    axis = Vector(rotvec / angle)
    return Quaternion(axis, angle)


def parse_args():
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1:]
    else:
        argv = []
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to pkl motion file")
    parser.add_argument("--template", required=True, help="Path to template FBX (ybot.fbx)")
    parser.add_argument("--output", required=True, help="Output FBX path")
    parser.add_argument("--fps", type=int, default=30)
    return parser.parse_args(argv)


def main():
    args = parse_args()
    print(f"\n=== SMPL → FBX (Blender) ===")
    print(f"  Input:    {args.input}")
    print(f"  Template: {args.template}")
    print(f"  Output:   {args.output}")
    print(f"  FPS:      {args.fps}\n")

    # ---- Load motion ----
    with open(args.input, "rb") as f:
        data = pickle.load(f)
    smpl_poses = np.asarray(data["smpl_poses"], dtype=np.float64)  # (T, 72)
    smpl_trans = np.asarray(data["smpl_trans"], dtype=np.float64)  # (T, 3)
    num_frames = smpl_poses.shape[0]
    print(f"Motion loaded: {num_frames} frames, poses {smpl_poses.shape}, trans {smpl_trans.shape}")

    # ---- Clean Blender scene ----
    bpy.ops.wm.read_factory_settings(use_empty=True)

    # ---- Import template FBX ----
    print(f"\nImporting template: {args.template}")
    bpy.ops.import_scene.fbx(filepath=args.template)

    # ---- Find armature ----
    armature = None
    for obj in bpy.data.objects:
        if obj.type == 'ARMATURE':
            armature = obj
            break
    if armature is None:
        raise RuntimeError("No armature found in template FBX!")
    print(f"Armature: {armature.name}")
    print(f"Bones: {len(armature.data.bones)}")

    # Print bone names for sanity check
    bone_names = {b.name for b in armature.data.bones}
    missing = [j for j in SMPL_JOINTS if j not in bone_names]
    found = [j for j in SMPL_JOINTS if j in bone_names]
    print(f"SMPL joints found in template: {len(found)}/{len(SMPL_JOINTS)}")
    if missing:
        print(f"WARNING - missing joints: {missing}")
        print(f"Available bones in template: {sorted(bone_names)[:30]}")
        if len(found) == 0:
            raise RuntimeError("No SMPL joints found in template - wrong skeleton!")

    # ---- Set scene properties ----
    bpy.context.scene.render.fps = args.fps
    bpy.context.scene.frame_start = 0
    bpy.context.scene.frame_end = num_frames - 1

    # ---- Enter Pose Mode ----
    bpy.context.view_layer.objects.active = armature
    bpy.ops.object.mode_set(mode='POSE')

    # Ensure every bone uses quaternion rotation
    for pb in armature.pose.bones:
        pb.rotation_mode = 'QUATERNION'

    # ---- Animate every frame ----
    print(f"\nWriting {num_frames} frames...")

    # The SMPL/FBX -90deg X rotation correction for root (Y-up)
    root_correction = Quaternion(Vector((1.0, 0.0, 0.0)), -np.pi / 2)  # identity by default
    # If your template is already Y-up oriented, no extra rotation is needed.
    # Uncomment below if your mannequin imports lying down:
    # root_correction = Quaternion(Vector((1, 0, 0)), -np.pi / 2)

    for frame in range(num_frames):
        bpy.context.scene.frame_set(frame)

        # --- Joint rotations ---
        for joint_idx, joint_name in enumerate(SMPL_JOINTS):
            if joint_name not in armature.pose.bones:
                continue
            pose_bone = armature.pose.bones[joint_name]
            rotvec = smpl_poses[frame, joint_idx * 3: joint_idx * 3 + 3]
            q = axis_angle_to_quat(rotvec)

            if joint_name == "m_avg_Pelvis":
                q = root_correction @ q

            pose_bone.rotation_quaternion = q
            pose_bone.keyframe_insert(data_path="rotation_quaternion", frame=frame)

        # --- Root translation ---
        if "m_avg_Pelvis" in armature.pose.bones:
            pelvis = armature.pose.bones["m_avg_Pelvis"]
            t = smpl_trans[frame]
            t_world = root_correction @ Vector(t)
            pelvis.location = t_world
            pelvis.keyframe_insert(data_path="location", frame=frame)

        if frame % 100 == 0:
            print(f"  Frame {frame}/{num_frames}")

    bpy.ops.object.mode_set(mode='OBJECT')
    print("Animation written.")

    # ---- Export FBX ----
    os.makedirs(os.path.dirname(os.path.abspath(args.output)) or ".", exist_ok=True)
    print(f"\nExporting to: {args.output}")
    bpy.ops.export_scene.fbx(
        filepath=args.output,
        use_selection=False,
        add_leaf_bones=False,
        bake_anim=True,
        bake_anim_use_all_bones=True,
        bake_anim_use_nla_strips=False,
        bake_anim_use_all_actions=False,
        bake_anim_force_startend_keying=True,
        bake_anim_step=1.0,
        bake_anim_simplify_factor=0.0,
        path_mode='COPY',
        embed_textures=False,
        axis_forward='-Z',
        axis_up='Y',
    )
    print(f"\n=== DONE: {args.output} ===\n")


if __name__ == "__main__":
    main()