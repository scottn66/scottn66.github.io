# Site quality checks

The workflow is `.github/workflows/site-quality.yml`. Two checks beyond the WCAG ratchet live here.

## Byte budget

`check-byte-budget.py` reads every tracked file. Anything over **1 MiB** (1,048,576 bytes) fails unless its path is in `byte-budget-allowlist.txt`. That list is the set already over the budget on main, so main stays green. A file that is added or edited up past 1 MiB is not on the list and fails. Each allowlisted path has a cap (the size on main, rounded up to the next 256 KiB). Growing past the cap fails. Deleting a listed file does not; the script warns about the stale row.

`robot-arm-sim/img/crawler_race.mp4` is about 1.04 MB and under this 1 MiB line, so it is not allowlisted.

```
python3 .github/site-quality/check-byte-budget.py --self-test
python3 .github/site-quality/check-byte-budget.py
```

## Links

`lychee.toml` checks every HTML file. A missing local file or image fails. An external **404** or **410** fails. External **403**, **429**, and **timeouts** do not: `accept` includes 403 and 429, and `accept_timeouts` is set. A timeout does not hide a 404, a 410, or a missing file in the same run. `check-link-policy.py` proves that against a local server (lychee 0.24.2 on `PATH`).

```
python3 .github/site-quality/check-link-policy.py
```

## Solar source hosts

`lychee.toml` still excludes `nrel.gov`, `eia.gov`, `emp.lbl.gov`, and `openei.org` (not `apps.openei.org`). Those hosts stall or block checkers, and waiting on them in every pull request does not produce a reliable status. `check-solar-sources.py` requests each of those URLs cited under `solar/` and fails only on **404** or **410**. Timeouts, connection errors, 403, 429, and other non-404 statuses are warnings.

The `solar-sources` job runs the self-test on every pull request and push. The live requests run on the weekly schedule (Monday 15:17 UTC) and on `workflow_dispatch`.

```
python3 .github/site-quality/check-solar-sources.py --self-test
python3 .github/site-quality/check-solar-sources.py
```
