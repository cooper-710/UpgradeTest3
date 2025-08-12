import json
from typing import Dict, List, Any, Optional

# Define a minimal skeleton suitable for Blender BVH files.  The hierarchy
# here is intentionally tiny so that unit tests can exercise the conversion
# logic without requiring a full body rig.  The structure can easily be
# extended by supplying a different ``hierarchy`` argument to ``jsonl_to_bvh``.
DEFAULT_HIERARCHY = {
    "name": "Hips",
    "offset": [0, 0, 0],
    "children": [
        {
            "name": "Chest",
            "offset": [0, 0, 0],
            "children": [],
        }
    ],
}


def _build_hierarchy_lines(node: Dict[str, Any], indent: int = 0) -> List[str]:
    """Recursively build BVH hierarchy lines from a node description."""
    lines: List[str] = []
    ind = " " * indent
    name = node["name"]

    if indent == 0:
        lines.append("HIERARCHY")
        lines.append(f"ROOT {name}")
    else:
        lines.append(f"{ind}JOINT {name}")

    lines.append(f"{ind}{'{'}")
    offset = node.get("offset", [0, 0, 0])
    lines.append(f"{ind}    OFFSET {offset[0]} {offset[1]} {offset[2]}")

    if indent == 0:
        lines.append(
            f"{ind}    CHANNELS 6 Xposition Yposition Zposition Zrotation Xrotation Yrotation"
        )
    else:
        lines.append(f"{ind}    CHANNELS 3 Zrotation Xrotation Yrotation")

    children = node.get("children", [])
    if children:
        for child in children:
            lines.extend(_build_hierarchy_lines(child, indent + 4))
    else:
        lines.append(f"{ind}    End Site")
        lines.append(f"{ind}    {{")
        lines.append(f"{ind}        OFFSET 0 0 0")
        lines.append(f"{ind}    }}")

    lines.append(f"{ind}}}")
    return lines


def _joint_traversal(node: Dict[str, Any], order: Optional[List[str]] = None) -> List[str]:
    """Collect joints in depth‑first order for motion channel mapping."""
    if order is None:
        order = []
    order.append(node["name"])
    for child in node.get("children", []):
        _joint_traversal(child, order)
    return order


def jsonl_to_bvh(
    jsonl: str,
    frame_time: float = 1 / 60.0,
    hierarchy: Optional[Dict[str, Any]] = None,
) -> str:
    """Convert a JSONL stream of joint transforms into a BVH string.

    Parameters
    ----------
    jsonl:
        A string containing one JSON object per line describing a frame.  Each
        object must map joint names to dictionaries with optional ``pos`` and
        ``rot`` keys.  The ``pos`` value is ``[x, y, z]`` and is only used for
        the root joint.  The ``rot`` value is ``[z, x, y]`` representing
        rotations in degrees following Blender's ZXY ordering.
    frame_time:
        Time step between frames.
    hierarchy:
        Optional hierarchy description.  When omitted, ``DEFAULT_HIERARCHY`` is
        used.
    """

    hierarchy = hierarchy or DEFAULT_HIERARCHY

    # Parse frames from JSONL.
    frames: List[Dict[str, Any]] = []
    for line in jsonl.strip().splitlines():
        if line.strip():
            frames.append(json.loads(line))

    if not frames:
        raise ValueError("No frames found in JSONL data")

    # Build header and determine joint order for channel mapping.
    header_lines = _build_hierarchy_lines(hierarchy)
    header = "\n".join(header_lines) + "\n"

    joint_order = _joint_traversal(hierarchy)

    # Build motion section.
    motion_lines: List[str] = []
    for frame in frames:
        values: List[float] = []
        for idx, joint in enumerate(joint_order):
            data = frame.get(joint, {})
            if idx == 0:  # root has translation channels
                pos = data.get("pos", [0, 0, 0])
                values.extend(pos)
            rot = data.get("rot", [0, 0, 0])
            values.extend(rot)
        motion_lines.append(" ".join(str(v) for v in values))

    motion = (
        "MOTION\n"
        f"Frames: {len(frames)}\n"
        f"Frame Time: {frame_time}\n"
        + "\n".join(motion_lines)
        + "\n"
    )

    return header + motion
