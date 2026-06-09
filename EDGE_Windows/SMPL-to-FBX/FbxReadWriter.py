import os
import sys
from typing import Dict

import numpy as np
from scipy.spatial.transform import Rotation as R
from SmplObject import SmplObjects

try:
    from fbx import *
    from FbxCommon import *
except ImportError:
    print("Error: module FbxCommon failed to import.\n")
    raise


class FbxReadWrite(object):
    def __init__(self, fbx_source_path, fps=30):
        lSdkManager, lScene = InitializeSdkObjects()
        self.lSdkManager = lSdkManager
        self.lScene = lScene
        self.fps = fps

        lResult = LoadScene(self.lSdkManager, self.lScene, fbx_source_path)
        if not lResult:
            raise Exception("An error occured while loading the scene :(")

    def _write_curve(self, lCurve, data: np.ndarray):
        lTime = FbxTime()
        time_mode = self._get_time_mode()
        lTime.SetGlobalTimeMode(time_mode)
        data = np.squeeze(np.asarray(data, dtype=np.float32))

        lCurve.KeyModifyBegin()
        for i in range(data.shape[0]):
            lTime.SetFrame(i, time_mode)
            lKeyIndex = lCurve.KeyAdd(lTime)[0]
            lCurve.KeySetValue(lKeyIndex, float(data[i]))
            lCurve.KeySetInterpolation(lKeyIndex, FbxAnimCurveDef.eInterpolationCubic)
        lCurve.KeyModifyEnd()

    def _find_node_recursive(self, node, name):
        """Robust recursive search by name."""
        if node.GetName() == name:
            return node
        for i in range(node.GetChildCount()):
            found = self._find_node_recursive(node.GetChild(i), name)
            if found is not None:
                return found
        return None

    def _prepare_bone_for_animation(self, node):
        """
        Critical: Reset PreRotation/PostRotation and force EulerXYZ rotation order.
        Without this, LclRotation keys may have no visible effect.
        """
        # Force rotation order to XYZ (matches our euler conversion)
        node.SetRotationOrder(FbxNode.EPivotSet.eSourcePivot, FbxEuler.EOrder.eOrderXYZ)
        node.SetRotationOrder(FbxNode.EPivotSet.eDestinationPivot, FbxEuler.EOrder.eOrderXYZ)
        
        # Zero out PreRotation and PostRotation - these are baked offsets that
        # would otherwise add to LclRotation
        node.SetPreRotation(FbxNode.EPivotSet.eSourcePivot, FbxVector4(0, 0, 0))
        node.SetPostRotation(FbxNode.EPivotSet.eSourcePivot, FbxVector4(0, 0, 0))
        
        # Make sure the rotation is active
        node.SetRotationActive(True)

    def addAnimation(self, pkl_filename: str, smpl_params: Dict, verbose: bool = False):
        lScene = self.lScene
        lGlobalSettings = lScene.GetGlobalSettings()
        lGlobalSettings.SetTimeMode(self._get_time_mode())

        self.destroyAllAnimation()

        lAnimStackName = pkl_filename
        lAnimStack = FbxAnimStack.Create(lScene, lAnimStackName)
        lAnimLayer = FbxAnimLayer.Create(lScene, "Base Layer")
        lAnimStack.AddMember(lAnimLayer)
        lRootNode = lScene.GetRootNode()

        names = SmplObjects.joints

        # rotate back to y-up
        rotation = R.from_quat(np.array([-0.7071068, 0, 0, 0.7071068]))

        smpl_poses = smpl_params["smpl_poses"]
        num_frames = smpl_poses.shape[0]
        print(f"\n=== Writing {num_frames} frames for {pkl_filename} ===")

        joints_found = 0
        joints_missing = []
        joints_written = 0

        for idx, name in enumerate(names):
            # Use robust recursive search
            node = self._find_node_recursive(lRootNode, name)
            
            if node is None:
                joints_missing.append(name)
                continue
            
            joints_found += 1
            
            # CRITICAL: Prepare the bone before writing animation
            self._prepare_bone_for_animation(node)

            rotvec = smpl_poses[:, idx * 3 : idx * 3 + 3].astype(np.float64)

            if name == "m_avg_Pelvis":
                rotvec_rotated = np.zeros_like(rotvec)
                for f in range(num_frames):
                    rotated = rotation * R.from_rotvec(rotvec[f])
                    rotvec_rotated[f] = rotated.as_rotvec()
                rotvec = rotvec_rotated

            euler = R.from_rotvec(rotvec).as_euler("xyz", degrees=True)

            # Sanity check the euler values
            if idx < 3 or idx == 12:  # print for pelvis, hips, neck
                print(f"  {name}: euler range X[{euler[:,0].min():.1f},{euler[:,0].max():.1f}] "
                      f"Y[{euler[:,1].min():.1f},{euler[:,1].max():.1f}] "
                      f"Z[{euler[:,2].min():.1f},{euler[:,2].max():.1f}]")

            for axis_idx, axis_name in enumerate(["X", "Y", "Z"]):
                lCurve = node.LclRotation.GetCurve(lAnimLayer, axis_name, True)
                if lCurve is not None:
                    self._write_curve(lCurve, euler[:, axis_idx])
                    joints_written += 1
                else:
                    print(f"  WARNING: GetCurve returned None for {name} {axis_name}")

        print(f"\nJoints found: {joints_found}/{len(names)}")
        print(f"Curves written: {joints_written} (expected {joints_found * 3})")
        if joints_missing:
            print(f"MISSING JOINTS: {joints_missing}")

        # Translation - pelvis only
        smpl_trans = np.asarray(smpl_params["smpl_trans"], dtype=np.float64)
        print(f"\nTranslation range: X[{smpl_trans[:,0].min():.3f},{smpl_trans[:,0].max():.3f}] "
              f"Y[{smpl_trans[:,1].min():.3f},{smpl_trans[:,1].max():.3f}] "
              f"Z[{smpl_trans[:,2].min():.3f},{smpl_trans[:,2].max():.3f}]")

        # Apply rotation per frame
        smpl_trans_rotated = np.array([rotation.apply(t) for t in smpl_trans])

        pelvis = self._find_node_recursive(lRootNode, "m_avg_Pelvis")
        if pelvis is not None:
            for axis_idx, axis_name in enumerate(["X", "Y", "Z"]):
                lCurve = pelvis.LclTranslation.GetCurve(lAnimLayer, axis_name, True)
                if lCurve is not None:
                    self._write_curve(lCurve, smpl_trans_rotated[:, axis_idx])

        print(f"=== Done ===\n")

    def writeFbx(self, write_base: str, filename: str):
        if not os.path.isdir(write_base):
            os.makedirs(write_base, exist_ok=True)
        write_path = os.path.join(write_base, filename.replace(".pkl", ""))
        lResult = SaveScene(self.lSdkManager, self.lScene, write_path)
        if not lResult:
            raise Exception("Failed to write to {}".format(write_path))

    def destroy(self):
        self.lSdkManager.Destroy()

    def destroyAllAnimation(self):
        lScene = self.lScene
        animStackCount = lScene.GetSrcObjectCount(FbxCriteria.ObjectType(FbxAnimStack.ClassId))
        for i in range(animStackCount):
            lAnimStack = lScene.GetSrcObject(FbxCriteria.ObjectType(FbxAnimStack.ClassId), i)
            lScene.RemoveMember(lAnimStack)

    def _get_time_mode(self):
        return {24: FbxTime.eFrames24, 25: FbxTime.eFrames25,
                30: FbxTime.eFrames30, 60: FbxTime.eFrames60}.get(self.fps, FbxTime.eFrames30)
