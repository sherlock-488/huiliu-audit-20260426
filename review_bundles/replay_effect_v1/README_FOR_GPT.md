# README_FOR_GPT - replay effect v1

## Context
- latest pushed commit before this bundle: `d75b3fe7b080741b147e0b1211aaaf55e8ce8e52`
- Scope: fulfillment_delivery only.
- Formal comparison: baseline vs skill.
- Upper-bound: gold-guided prompt includes gold/oracle labels by design.

## Completed
- Built baseline / skill / gold-guided main inputs: 121 rows each.
- Built challenge baseline / skill / gold-guided inputs: 45 rows each.
- Baseline and skill prompt leakage check: 0 rows.
- Gold-guided prompt has reference-label block: 121 rows, expected.
- Output parser tests: 6 / 6 passed.
- No model outputs are present, so no performance metrics were fabricated.

## Review Focus
1. Whether gold-guided prompt construction is appropriate for upper-bound measurement.
2. Whether baseline/skill prompt leakage detection is sufficient.
3. Whether `evaluate_fd_replay.py` metrics cover ResponseSolution and DialogueAgreeSolution risks.
4. Whether `compare_fd_replay.py` gate logic is suitable for deciding skill effectiveness.
