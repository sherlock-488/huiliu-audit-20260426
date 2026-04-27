# README_FOR_GPT - replay_run_effect_v1

## Context
- latest pushed commit before this bundle: `6bd492214592407a816bdfd68cfefaee5bd0db08`
- Scope: fulfillment_delivery only.
- Formal effect groups: baseline vs skill.
- Upper-bound group: gold-guided, with gold/oracle labels intentionally inserted into prompt.

## Completed
- Built three main replay inputs: baseline / skill / gold-guided, each 121 rows.
- Built challenge calibration inputs: baseline / skill / gold-guided, each 45 rows.
- Baseline and skill prompt leakage check: 0 rows.
- Gold-guided prompt label block: 121 rows by design.
- Added robust output parser supporting JSON, markdown fences, wrapper output, and Python-literal fallback.
- Added dry-run model runner and evaluator. No model outputs are present, so no metrics were fabricated.

## GPT Review Focus
1. Whether gold-guided prompt should use skill prompt as base, as implemented.
2. Whether baseline/skill prompt leakage detection is sufficient.
3. Whether output_parser.py is robust enough for expected model formats.
4. Whether evaluate_fd_effect.py metrics are enough for ResponseSolution / DialogueAgreeSolution effect judgment.
