from rules.continuous_beam import solve_three_moment
r = solve_three_moment([6,6],[{"type":"udl","w":20},{"type":"udl","w":20}],["pinned","pinned","pinned"])
d = r["diagrams"][0]
print("Span 1 key points:")
for i in range(0, len(d["x"]), 5):
    print(f"  x={d['x'][i]:6.2f}  V={d['shear'][i]:8.2f}  M={d['moment'][i]:8.2f}")
print(f"\nM at support B (x=6): {d['moment'][-1]:.2f} (expected -90)")
print(f"V at x=0: {d['shear'][0]:.2f} (expected R_A = 45)")
