# Three-Moment Theorem Implementation Plan

## Files to Create/Modify

1. **CREATE** `rules/continuous_beam.py` — Three-Moment solver
2. **MODIFY** `nlp/prompt_parser.py` — Parse multiple spans & supports
3. **MODIFY** `rules/beam_design.py` — Route continuous to new solver
4. **MODIFY** `api/main.py` — Handle multi-span responses
5. **MODIFY** `api/static/script.js` — Display multi-span results & diagrams

## Phase 1: Solver Module
- Build coefficient matrix for N spans
- Handle fixed/pinned/roller boundary conditions
- Compute support moments, reactions, SFD, BMD per span
- Support UDL and point loads per span

## Phase 2: Parser
- Extract multiple spans: "spans 6m, 5m, 4m"
- Extract per-span loads or uniform load across all spans
- Extract support types for each support

## Phase 3: Integration
- Route continuous beams through new solver
- Return per-span diagram data
- Frontend renders multi-span beam with intermediate supports
