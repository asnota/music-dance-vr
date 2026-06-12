import sys
sys.path.append('.')
from FbxCommon import *
from fbx import *

fbx_path = sys.argv[1]

lSdkManager, lScene = InitializeSdkObjects()
LoadScene(lSdkManager, lScene, fbx_path)

lAnimStack = lScene.GetSrcObject(FbxCriteria.ObjectType(FbxAnimStack.ClassId), 0)
lAnimLayer = lAnimStack.GetSrcObject(FbxCriteria.ObjectType(FbxAnimLayer.ClassId), 0)

def walk(node, depth=0):
    name = node.GetName()
    rx = node.LclRotation.GetCurve(lAnimLayer, "X")
    ry = node.LclRotation.GetCurve(lAnimLayer, "Y")
    rz = node.LclRotation.GetCurve(lAnimLayer, "Z")
    tx = node.LclTranslation.GetCurve(lAnimLayer, "X")
    
    nkeys_r = (rx.KeyGetCount() if rx else 0) + (ry.KeyGetCount() if ry else 0) + (rz.KeyGetCount() if rz else 0)
    nkeys_t = tx.KeyGetCount() if tx else 0
    
    marker = ""
    if nkeys_r > 0: marker += " [ROT]"
    if nkeys_t > 0: marker += " [TRANS]"
    
    print(f"{'  ' * depth}{name}: rot_keys={nkeys_r}, trans_keys={nkeys_t}{marker}")
    
    for i in range(node.GetChildCount()):
        walk(node.GetChild(i), depth + 1)

walk(lScene.GetRootNode())
lSdkManager.Destroy()