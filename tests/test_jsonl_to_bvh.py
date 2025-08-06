import textwrap

from converter.jsonl_to_bvh import jsonl_to_bvh


def test_jsonl_to_bvh_basic():
    jsonl = "\n".join(
        [
            '{"Hips":{"pos":[0,0,0],"rot":[0,0,0]},"Chest":{"rot":[0,0,0]}}',
            '{"Hips":{"pos":[1,2,3],"rot":[10,20,30]},"Chest":{"rot":[40,50,60]}}',
        ]
    )

    expected = textwrap.dedent(
        """
        HIERARCHY
        ROOT Hips
        {
            OFFSET 0 0 0
            CHANNELS 6 Xposition Yposition Zposition Zrotation Xrotation Yrotation
            JOINT Chest
            {
                OFFSET 0 0 0
                CHANNELS 3 Zrotation Xrotation Yrotation
                End Site
                {
                    OFFSET 0 0 0
                }
            }
        }
        MOTION
        Frames: 2
        Frame Time: 0.0333333
        0 0 0 0 0 0 0 0 0
        1 2 3 10 20 30 40 50 60
        """
    ).strip()

    output = jsonl_to_bvh(jsonl, frame_time=0.0333333).strip()
    assert output == expected
