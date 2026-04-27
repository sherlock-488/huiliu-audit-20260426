# xx_all_scene vs case_2026-04-20 overlap report

## Files
- xx: `/Users/sherlock/Desktop/01_项目代码/回流/xx_all_scene_service_v2_0408_signals_sort_process_multiple_chuli.jsonl`
- case_0420: `/Users/sherlock/Desktop/01_项目代码/回流/case_2026-04-20.txt`

## Method
- `xx` 使用 JSONL 字段 `sessionId/input/target`。
- `case_0420` 使用 TSV 字段 `session_id/model_name/input_prompt/output`，跳过表头/非 4 列/第 3 列不以 `User` 开头的行。
- `input` 统一把字面量 `\n` 还原为换行后再 hash。
- `target/output` 去掉 ```json fence，尽量按 JSON canonical form hash；不能 parse 时按原始字符串 hash。
- 样本级重叠以 `normalized(input) + normalized(target/output)` 的 SHA1 为准。

## Counts
- xx parse_ok rows: `13524` / total `13524`
- case valid data rows: `95188` / total `95547`; skipped/header/bad `359`
- common sessions: `0`
- common normalized inputs: `0`
- common normalized targets only: `1002`
- common normalized input+target pairs: `0`

## Row Overlap
- xx rows with common session: `0` / `13524` (0.00%)
- case rows with common session: `0` / `95188` (0.00%)
- xx rows with exact input+target pair in case: `0` / `13524` (0.00%)
- case rows with exact input+target pair in xx: `0` / `95188` (0.00%)

## Conclusion
- 未发现样本级重叠：按 `input+target/output` 精确规范化 hash，交集为 0。
- 未发现 session_id/sessionId 级重叠。

## Matched Session Examples

## Matched Pair Examples
- None
