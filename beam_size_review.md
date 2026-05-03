Let me update the `estimate_beam_size` function in `rules/beam_design.py` with the standard size progression you described.

Viewed beam_design.py:230-270
Viewed beam_design.py:310-332
Edited beam_design.py

Now I need to update `main.py` to pass `beam_type` to `estimate_beam_size`:

Viewed main.py:55-75
Edited main.py

Now let me restart the server and test:

Ran command: `venv\Scripts\python.exe -m uvicorn api.main:app --host 127.0.0.1 --port 8000`

Server is running. Let me test the beam sizes for different scenarios:

Created test_beam_sizes.py
Ran command: `venv\Scripts\python.exe test_beam_sizes.py`

The test script used system Python instead of venv Python. Let me wait for the server to be ready and retry:

Server is ready. Now let me test:

Ran command: `venv\Scripts\python.exe test_beam_sizes.py`

All tests pass with the correct standard sizes. Here's what the results show:

| Scenario | Width | Depth | Deflection | Why |
|---|---|---|---|---|
| Simply Supported 6m | **230mm** | **300mm** | ✅ SAFE | 6000/20 = 300mm min → 300mm matches |
| Cantilever 4m | **300mm** | **600mm** | ✅ SAFE | 4000/7 = 571mm min → snaps up to 600mm |
| Continuous 8m | **230mm** | **450mm** | ✅ SAFE | 8000/26 = 308mm min → snaps up to 450mm |
| Simply Supported 3m | **230mm** | **300mm** | ✅ SAFE | 3000/20 = 150mm min → starts at 300mm (minimum) |

### Summary of changes:
- **`rules/beam_design.py`** — `estimate_beam_size()` now uses your standard progressions:
  - **Widths**: 230 → 300 → 450 → 600 → 750 → 900 → 1050 → 1200mm
  - **Depths**: 300 → 450 → 600 → 750 → 900 → 1050 → 1200 → 1350 → 1500mm
- It picks the **smallest standard depth** that satisfies the span/depth deflection ratio for the beam type
- Width is selected as the **smallest standard width ≥ half the depth** (minimum 230mm)
- The function now accepts `beam_type` so cantilevers (L/7) get larger beams than simply supported (L/20)