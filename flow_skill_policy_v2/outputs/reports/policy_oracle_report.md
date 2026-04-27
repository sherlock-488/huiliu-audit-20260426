# Policy Oracle Report

- fulfillment_delivery_oracle_cases: `121`
- receipt_quality_oracle_cases: `120`
- needs_trainer_review: `159`

## Gold / Oracle Relation
- `same`: `102`
- `different`: `60`
- `oracle_no_gold_action`: `51`
- `gold_no_oracle_action`: `26`
- `canonical_same`: `2`

## Conflict Rules
- `RQ-09`: `24`
- `FD-05A`: `19`
- `RQ-07`: `19`
- `FD-03`: `18`
- `RQ-01`: `15`
- `RQ-02`: `14`
- `RQ-11`: `13`
- `FD-10`: `8`
- `FD-OTHER`: `6`
- `FD-08`: `5`
- `FD-02`: `4`
- `FD-04`: `3`
- `FD-12`: `3`
- `FD-05B`: `2`
- `RQ-03`: `2`
- `FD-11`: `1`
- `FD-06`: `1`
- `FD-01`: `1`
- `FD-07`: `1`

- fulfillment_delivery gold=无 but oracle=系统催单/加急调度: `17`
- receipt_quality gold=退款 but oracle 前置 guard: `0`
- receipt_quality gold=无 but oracle action: `21`

这些冲突不是自动判 gold 错，而是进入训练师校准包。
