import argparse
import json

HEADER = """HIERARCHY
ROOT root
{{
    OFFSET 0 0 0
    CHANNELS 6 Xposition Yposition Zposition Zrotation Xrotation Yrotation
    End Site
    {{
        OFFSET 0 0 0
    }}
}}
MOTION
Frames: {frame_count}
Frame Time: 0.0333333
"""

def convert_jsonl_to_bvh(jsonl_path: str, bvh_path: str) -> None:
    """Convert a JSONL file of frames to a simple BVH file.

    Each non-empty line of the input is expected to be a JSON array or object.
    Values are written in the order they appear, separated by spaces.
    """
    frames = []
    with open(jsonl_path, "r", encoding="utf-8") as src:
        for line in src:
            line = line.strip()
            if not line:
                continue
            data = json.loads(line)
            if isinstance(data, dict):
                data = list(data.values())
            frames.append(" ".join(str(v) for v in data))

    with open(bvh_path, "w", encoding="utf-8") as dst:
        dst.write(HEADER.format(frame_count=len(frames)))
        for frame in frames:
            dst.write(frame + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert JSONL motion data to a minimal BVH file."
    )
    parser.add_argument("input", help="Input JSONL file")
    parser.add_argument("output", help="Output BVH file")
    args = parser.parse_args()
    convert_jsonl_to_bvh(args.input, args.output)


if __name__ == "__main__":
    main()
