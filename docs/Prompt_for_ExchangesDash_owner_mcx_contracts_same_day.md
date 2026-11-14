# Request for the ExchangesDash / Octo-MCX owner: MCX contracts on the same evening

*From Tusk (Abhishek Biyani) · 10 Nov 2026*

## Why we're asking

The brokers engine publishes each day's ADR only through the last day on which every exchange input is complete. Our target is to have day D published by **06:00 IST on D+1**. NSE and BSE make it in time. MCX contracts don't, so every broker's ADR stays one trading day behind.

In `dashboard/data/mcx_dashboard_data.json`, a day's row appears on its own evening, but `total_contracts` stays `null` until the next run:

| Commit (IST) | Last row | Its `total_contracts` | Day filled in by this commit |
|---|---|---|---|
| 5 Nov 01:29 | 4 Nov | null | 3 Nov |
| 6 Nov 01:43 | 5 Nov | null | 4 Nov |
| 7 Nov 01:09 | 6 Nov | null | 5 Nov |
| 9 Nov 10:27 | 6 Nov | 16,323,010 | 6 Nov (Friday's count, filled Monday) |
| 10 Nov 04:09 | 9 Nov | null | — |

Your own comment in `scripts/mcx_pipeline.py` (`main()`, "A day's contracts reach mcx_commodity_daily a run after its revenue") describes the same lag. Thank you for the fix that republishes changed days. That fix covers the Friday case, but the one-run lag is still there.

## What we'd like

1. **Octo-MCX (`mcx_commodity_daily`):** load `contracts` for day D in the same run that loads D's revenue. Both come from the day's MCX bhavcopy, which MCX posts that evening. If contracts have to come from a later file, add a run after it posts, before 05:00 IST.
2. **ExchangesDash:** make sure one of your Vercel-triggered slots runs after (1) and before **05:00 IST**, so that `total_contracts` for D is in `mcx_dashboard_data.json` by then. Your 06:00 IST slot is just too late for us.
3. Leave the field name and units as they are (`total_contracts`, raw count per day, all commodities). Nothing changes on our side.

We only read your public JSON. Nothing in your repos or Supabase projects is written by us.

## How we'll know it worked

Our `freshness` check runs at 06:15 IST. It names `mcx:contracts` as the cause whenever MCX contracts are the reason a broker is behind. Once (1) and (2) are in place, that line should disappear.
