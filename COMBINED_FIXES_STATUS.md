# combined-fixes → upstream status

Last checked: 2026-09-24.

## Blocker

[#163](https://github.com/alistair23/AutoMower-BLE/pull/163) adds `GetLiftSensorStatus` (4476/6). Awaiting maintainer re-review.

## To drop the branch

1. #163 merged; close #166.
2. #158 leftover log lines in `protocol.py`: upstream them or drop.
3. PyPI release after #163 (current: 0.2.9, too old).
4. Bridge: rename `GetLiftSensorLegacy` → `GetLiftSensorStatus`; pin `requirements.txt` and `Dockerfile` to that release.
5. Delete `combined-fixes` and `backup-combined-fixes-pre-drop`.
