import torch
import numpy as np
from scipy.spatial.transform import Rotation as R

def quat_slerp(q0, q1, fraction):
    """
    Element-wise spherical linear interpolation between two quaternion tensors.
    q0, q1: (..., 4) tensors of quaternions
    fraction: scalar or tensor broadcastable to q0
    Returns: (..., 4) tensor
    """
    # Make sure everything is a tensor on the same device/dtype
    if not isinstance(q0, torch.Tensor):
        q0 = torch.tensor(q0)
    if not isinstance(q1, torch.Tensor):
        q1 = torch.tensor(q1, dtype=q0.dtype, device=q0.device)
    if not isinstance(fraction, torch.Tensor):
        fraction = torch.tensor(fraction, dtype=q0.dtype, device=q0.device)
    else:
        fraction = fraction.to(q0.device).to(q0.dtype)

    # Reshape fraction to broadcast with q0
    # If fraction is (T,) and q0 is (B, T, J, 4), expand to (1, T, 1, 1)
    while fraction.dim() < q0.dim():
        if fraction.dim() == 1 and q0.dim() >= 2 and q0.shape[1] == fraction.shape[0]:
            fraction = fraction.unsqueeze(0).unsqueeze(-1).unsqueeze(-1)
            if fraction.dim() > q0.dim():
                fraction = fraction.squeeze(-1)
            break
        else:
            fraction = fraction.unsqueeze(-1)

    # Make sure shape matches via broadcasting
    fraction = fraction.expand(*q0.shape[:-1], 1) if fraction.shape[-1] != 1 else fraction

    # Dot product
    dot = (q0 * q1).sum(dim=-1, keepdim=True)

    # If dot < 0, flip q1 to take shorter path
    q1 = torch.where(dot < 0, -q1, q1)
    dot = dot.abs().clamp(-1.0, 1.0)

    # Where dot is close to 1, use LERP (avoid division by ~0)
    DOT_THRESHOLD = 0.9995

    omega = torch.acos(dot)
    sin_omega = torch.sin(omega)
    # Safe division
    sin_omega_safe = torch.where(sin_omega.abs() < 1e-6,
                                  torch.ones_like(sin_omega),
                                  sin_omega)

    s0 = torch.sin((1.0 - fraction) * omega) / sin_omega_safe
    s1 = torch.sin(fraction * omega) / sin_omega_safe

    slerp_result = s0 * q0 + s1 * q1

    # LERP fallback
    lerp = (1.0 - fraction) * q0 + fraction * q1
    lerp = lerp / lerp.norm(dim=-1, keepdim=True).clamp(min=1e-8)

    return torch.where(dot > DOT_THRESHOLD, lerp, slerp_result)

def quaternion_to_matrix(quaternions):
    """
    Convert quaternion (..., 4) -> rotation matrix (..., 3, 3)
    Quaternion format: xyzw
    """
    orig_shape = quaternions.shape[:-1]

    q = quaternions.reshape(-1, 4).detach().cpu().numpy()

    mats = R.from_quat(q).as_matrix()

    mats = torch.tensor(
        mats,
        dtype=quaternions.dtype,
        device=quaternions.device,
    )

    return mats.reshape(*orig_shape, 3, 3)


def matrix_to_quaternion(matrix):
    """
    Convert rotation matrix (..., 3, 3) -> quaternion (..., 4)
    Quaternion format: xyzw
    """
    orig_shape = matrix.shape[:-2]

    mats = matrix.reshape(-1, 3, 3).detach().cpu().numpy()

    q = R.from_matrix(mats).as_quat()

    q = torch.tensor(
        q,
        dtype=matrix.dtype,
        device=matrix.device,
    )

    return q.reshape(*orig_shape, 4)


def axis_angle_to_matrix(axis_angle):
    """
    axis-angle (..., 3) -> rotation matrix (..., 3, 3)
    """
    orig_shape = axis_angle.shape[:-1]

    aa = axis_angle.reshape(-1, 3).detach().cpu().numpy()

    mats = R.from_rotvec(aa).as_matrix()

    mats = torch.tensor(
        mats,
        dtype=axis_angle.dtype,
        device=axis_angle.device,
    )

    return mats.reshape(*orig_shape, 3, 3)


def matrix_to_axis_angle(matrix):
    """
    rotation matrix (..., 3, 3) -> axis-angle (..., 3)
    """
    orig_shape = matrix.shape[:-2]

    mats = matrix.reshape(-1, 3, 3).detach().cpu().numpy()

    aa = R.from_matrix(mats).as_rotvec()

    aa = torch.tensor(
        aa,
        dtype=matrix.dtype,
        device=matrix.device,
    )

    return aa.reshape(*orig_shape, 3)


def matrix_to_rotation_6d(matrix):
    """
    rotation matrix (..., 3, 3) -> 6D rotation (..., 6)
    """
    return matrix[..., :2, :].reshape(*matrix.shape[:-2], 6)


def rotation_6d_to_matrix(d6):
    """
    6D rotation (..., 6) -> rotation matrix (..., 3, 3)
    """
    a1 = d6[..., 0:3]
    a2 = d6[..., 3:6]

    b1 = torch.nn.functional.normalize(a1, dim=-1)

    b2 = a2 - (b1 * a2).sum(-1, keepdim=True) * b1
    b2 = torch.nn.functional.normalize(b2, dim=-1)

    b3 = torch.cross(b1, b2, dim=-1)

    return torch.stack((b1, b2, b3), dim=-2)


def ax_to_6v(axis_angle):
    """
    axis-angle (..., 3) -> rotation 6D (..., 6)
    """
    return matrix_to_rotation_6d(
        axis_angle_to_matrix(axis_angle)
    )


def ax_from_6v(rot_6d):
    """
    rotation 6D (..., 6) -> axis-angle (..., 3)
    """
    return matrix_to_axis_angle(
        rotation_6d_to_matrix(rot_6d)
    )