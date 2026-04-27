# Current Turn Patch Report

## Patch
- Added replay-only dual intent mapping: `怎么还没配送 / 怎么还没送 / 怎么还没送到 / 还没配送 / 还没送到 / 不是还没送到吗` -> `eta_question + delivery_urge`.
- Kept v22 close/ack/transfer gates unchanged.
- Kept weak confirmation blocking unchanged: weak confirm plus question/progress/reject terms is not pure confirmation.

## Impact On v22 Fulfillment Delivery Oracle Rows
- scanned_fd_oracle_rows: `186`
- changed_rows: `2`
- close_ack_transfer_rows_newly_triggered: `0`

## Phrase Hits
- `怎么还没送`: `2`
- `怎么还没送到`: `2`
- `还没送到`: `2`
- `怎么还没配送`: `2`
- `还没配送`: `2`

## Intent Count Delta
- `delivery_urge`: `57` -> `59`

## Changed Examples
- `cf3e06fc48d0b33eeb84b7fab9224b0f90d0533d` `怎么还没配送`: `['eta_question']` -> `['delivery_urge', 'eta_question']` gold=`智能跟单` oracle=`加急调度` rule=`FD-02`
- `cf3e06fc48d0b33eeb84b7fab9224b0f90d0533d` `怎么还没配送`: `['eta_question']` -> `['delivery_urge', 'eta_question']` gold=`智能跟单` oracle=`加急调度` rule=`FD-02`
