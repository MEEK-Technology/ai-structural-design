Edited index.html
Edited index.html
Viewed index.html:1-21

Yes! The system **already supports mixed supports** — it depends entirely on what you specify in the prompt. Let me verify the parser handles this correctly and give you example prompts.

Ran command: `venv\Scripts\python.exe -c "from nlp.prompt_parser import extract_parameters, apply_defaults; import json; prompts = ['A 3-span continuous beam with spans 8m, 6m, 4m, UDL 20kN/m, fixed at start, supports: fixed, pinned, roller, pinned', 'A 2-span continuous beam with spans 6m, 5m, UDL 15kN/m, fixed at start and fixed at end', 'A 3-span continuous beam with spans 8m, 6m, 8m and UDL of 20kN/m']; [print(f'Prompt: {p}\n  Result: beam_type={apply_defaults(extract_parameters(p))[\"beam_type\"]}, spans={apply_defaults(extract_parameters(p))[\"spans\"]}, supports={apply_defaults(extract_parameters(p))[\"supports\"]}\n') for p in prompts]"`

Inline Python is too complex. Let me write a test file:

Edited test_supports.py
Ran command: `venv\Scripts\python.exe test_supports.py`

All working. Now let me verify each combination actually solves correctly with the Three-Moment solver:

Edited test_supports.py
Ran command: `venv\Scripts\python.exe test_supports.py`

Unicode issue on Windows. Let me fix the check mark:

Edited test_supports.py
Ran command: `venv\Scripts\python.exe test_supports.py`

**All 4 combinations pass equilibrium checks** (ΣR = Total Load). The solver handles every combination correctly.

Now here are the example prompts you can use:

---

### Example Prompts to Test All Support Types

**1. All Pinned (default):**
```
A 3-span continuous beam with spans 8m, 6m, 8m and UDL of 20kN/m
```
→ Supports: `Pinned → Pinned → Pinned → Pinned`

**2. Fixed at one end:**
```
A 2-span continuous beam with spans 6m, 4m, UDL 25kN/m, fixed at start
```
→ Supports: `Fixed → Pinned → Pinned`

**3. Fixed at both ends:**
```
A 2-span continuous beam with spans 6m, 5m, UDL 15kN/m, fixed at start and fixed at end
```
→ Supports: `Fixed → Pinned → Fixed`

**4. Mixed supports (the showcase prompt):**
```
A 3-span continuous beam with spans 8m, 6m, 4m, UDL 20kN/m, supports: fixed, pinned, roller, pinned
```
→ Supports: `Fixed → Pinned → Roller → Pinned`

---

### How it works:

| What you type | What happens |
|---|---|
| No supports mentioned | All supports default to **pinned** |
| `"fixed at start"` | First support → **fixed**, rest → pinned |
| `"fixed at end"` | Last support → **fixed**, rest → pinned |
| `"fixed at start and fixed at end"` | Both ends → **fixed**, interior → pinned |
| `"supports: fixed, pinned, roller, pinned"` | **Explicit per-support** — you control each one |

The Three-Moment solver treats **pinned and roller identically** (both have M = 0 at that support), but the beam diagram shows them with different symbols so the engineering context is preserved.
