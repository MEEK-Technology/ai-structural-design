"""
Test the Three-Moment solver with known problems.
"""
from rules.continuous_beam import solve_three_moment, merge_diagrams

print("=" * 60)
print("TEST 1: 2-span continuous beam, all pinned, UDL 20 kN/m")
print("Spans: 6m + 6m")
print("=" * 60)

result = solve_three_moment(
    spans=[6, 6],
    loads=[
        {"type": "udl", "w": 20},
        {"type": "udl", "w": 20},
    ],
    support_types=["pinned", "pinned", "pinned"]
)

print(f"Support moments: {result['moments']}")
print(f"Reactions: {result['reactions']}")
print(f"Max moment: {result['max_moment']} kNm")
print(f"Max shear: {result['max_shear']} kN")

# Expected for symmetric 2-span UDL:
# M_B (interior) = -wL²/8 = -20*36/8 = -90... no
# For 2-span: M_B = -wL²/8 (by Three-Moment)
# Three-Moment: 0 + 2*M_B*(6+6) + 0 = -(20*216/4 + 20*216/4)
# 24*M_B = -(1080 + 1080) = -2160
# M_B = -90 kNm
print("\nExpected: M_B = -90 kNm")
print(f"Got:      M_B = {result['moments'][1]} kNm")

print()
print("=" * 60)
print("TEST 2: 3-span continuous beam, all pinned, UDL 15 kN/m")
print("Spans: 8m + 6m + 8m (symmetric)")
print("=" * 60)

result2 = solve_three_moment(
    spans=[8, 6, 8],
    loads=[
        {"type": "udl", "w": 15},
        {"type": "udl", "w": 15},
        {"type": "udl", "w": 15},
    ],
    support_types=["pinned", "pinned", "pinned", "pinned"]
)

print(f"Support moments: {result2['moments']}")
print(f"Reactions: {result2['reactions']}")
print(f"Max moment: {result2['max_moment']} kNm")
print(f"Max shear: {result2['max_shear']} kN")

print()
print("=" * 60)
print("TEST 3: 2-span, fixed LEFT, pinned rest, UDL 20 kN/m")
print("Spans: 6m + 4m")
print("=" * 60)

result3 = solve_three_moment(
    spans=[6, 4],
    loads=[
        {"type": "udl", "w": 20},
        {"type": "udl", "w": 20},
    ],
    support_types=["fixed", "pinned", "pinned"]
)

print(f"Support moments: {result3['moments']}")
print(f"Reactions: {result3['reactions']}")
print(f"Max moment: {result3['max_moment']} kNm")
print(f"Max shear: {result3['max_shear']} kN")

print()
print("=" * 60)
print("TEST 4: 2-span with point load on span 2")
print("Spans: 6m + 6m, UDL 10kN/m on span 1, Point 30kN at 3m on span 2")
print("=" * 60)

result4 = solve_three_moment(
    spans=[6, 6],
    loads=[
        {"type": "udl", "w": 10},
        {"type": "point_load", "P": 30, "a": 3},
    ],
    support_types=["pinned", "pinned", "pinned"]
)

print(f"Support moments: {result4['moments']}")
print(f"Reactions: {result4['reactions']}")
print(f"Max moment: {result4['max_moment']} kNm")
print(f"Max shear: {result4['max_shear']} kN")

# Merged diagrams
x, v, m, w = merge_diagrams(result4['diagrams'])
print(f"\nDiagram points: {len(x)}")
print(f"x range: {x[0]} to {x[-1]}m")
print(f"V range: {min(v)} to {max(v)} kN")
print(f"M range: {min(m)} to {max(m)} kNm")
