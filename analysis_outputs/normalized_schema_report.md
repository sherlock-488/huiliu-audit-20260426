# Normalized CaseRecord Draft Report

- Output: `analysis_outputs/normalized_cases_sample.jsonl`
- Records written: 58
- Max per file: 50
- Max total: 200
- Text fields and `raw` are PII-masked in this sample output.

## Input Files

| File | Normalized | Parse Failed | Notes |
|---|---:|---:|---|
| `xx_all_scene_service_v2_0408_signals_sort_process_multiple_chuli.jsonl` | 50 | 0 | sample_limit=50 |
| `analysis_outputs/pipeline_sample_outputs/annotation_exaggeration.jsonl` | 2 | 0 | sample_limit=50 |
| `analysis_outputs/pipeline_sample_outputs/annotation_profession.jsonl` | 2 | 0 | sample_limit=50 |
| `analysis_outputs/pipeline_sample_outputs/annotation_risk.jsonl` | 2 | 0 | sample_limit=50 |
| `analysis_outputs/pipeline_sample_outputs/fixture_cleaned_data.jsonl` | 2 | 0 | sample_limit=50 |
| `analysis_outputs/pipeline_sample_outputs/root_full_attempt_cleaned.jsonl` | 0 | 0 | sample_limit=50 |
| `analysis_outputs/pipeline_sample_outputs/root_full_attempt_cleaned_intermediate.jsonl` | 0 | 0 | sample_limit=50 |
| `analysis_outputs/pipeline_sample_outputs/root_stage1_intermediate.jsonl` | 0 | 0 | sample_limit=50 |

## Mapping Notes

- `sample_id`: uses explicit `request_id` / `trace_id` / `turn_id` only when present; otherwise SHA1 of source_file, source_line, session_id, user_query, response, and response_solution.
- `turn_index`: only filled from explicit turn/round fields; no inferred order was generated.
- `signals`: direct structured dict fields are retained. Prompt-embedded signal text is not parsed.
- `available_solutions`: direct structured list fields are retained. Prompt-embedded方案列表 is not parsed.
- `label_type`: only normalized when the source already has one of `unknown/good/bad/human_annotated`; otherwise `unknown`.

## Counters

- sample_id sources: `{"sha1": 58}`

### Notes

- sample_id_source: sha1: 58
- signals_note: signals appear in prompt text; not parsed: 56
- available_solutions_note: available solutions appear in prompt text; not parsed: 50
- available_solutions_note: not found: 8
- signals_note: not found: 2

## Output Fields

- `sample_id`: populated in 58/58 records
- `source_file`: populated in 58/58 records
- `source_line`: populated in 58/58 records
- `session_id`: populated in 58/58 records
- `turn_index`: populated in 0/58 records
- `model_name`: populated in 2/58 records
- `scene`: populated in 50/58 records
- `user_query`: populated in 52/58 records
- `dialogue_history`: populated in 52/58 records
- `signals`: populated in 0/58 records
- `available_solutions`: populated in 0/58 records
- `response`: populated in 52/58 records
- `response_solution`: populated in 52/58 records
- `dialogue_agree_solution`: populated in 52/58 records
- `label_type`: populated in 58/58 records
- `raw`: populated in 58/58 records
