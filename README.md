# Huiliu Audit 2026-04-26

This repository contains the local audit artifacts for the `回流/` workspace.

Included:

- `tools/`: audit and normalization scripts created for this audit.
- `analysis_outputs/`: generated reports, schema audit JSON, masked normalized samples, and small pipeline validation outputs.
- `huiliu-data-processor/`: extracted 2026-04-26 processor version supplied after the initial audit.
- `archives/huiliu-data-processor-20260426.zip`: original 2026-04-26 processor zip.

Not included:

- Original source repositories.
- Original raw JSONL data except explicit user-uploaded case assets/release assets.
- Legacy zip archives from the initial workspace.
- Unmasked sample input.

Notes:

- Reports and samples were generated locally without network access during the audit.
- Sample content is best-effort PII masked.
- `normalized_cases_sample.jsonl` is a draft CaseRecord sample, not production training data.
