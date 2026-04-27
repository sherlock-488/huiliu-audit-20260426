# Output Parser Report

## Summary
- test_cases: `6`
- passed: `6`

## Cases
| case | expected_error | actual_error | ResponseSolution | DialogueAgreeSolution | pass |
|---|---:|---:|---|---|---:|
| `pure_json` | `False` | `False` | `系统催单` | `无` | `True` |
| `code_fence_json` | `False` | `False` | `无` | `无` | `True` |
| `prefix_text_json` | `False` | `False` | `加急调度` | `无` | `True` |
| `non_json_text` | `True` | `True` | `无` | `无` | `True` |
| `missing_fields` | `False` | `False` | `无` | `无` | `True` |
| `composite_solution` | `False` | `False` | `系统催单;智能跟单` | `无` | `True` |
