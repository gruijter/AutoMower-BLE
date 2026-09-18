# combined-fixes → upstream status

Last checked: 2026-09-17 (against `upstream/main` = `4bf4b00`).

| PR | Fix | Status |
|----|-----|--------|
| [#151](https://github.com/alistair23/AutoMower-BLE/pull/151) | parse_response crash on empty response | **Merged** (`75e10fe`) |
| [#158](https://github.com/alistair23/AutoMower-BLE/pull/158) | AuthenticationFailed pairing diagnostics (by kelvan) | **Partially merged** (`4bf4b00`) |
| [#161](https://github.com/alistair23/AutoMower-BLE/pull/161) | swapped eco mode / frost sensor mapping + SetFrostSensorEnabledLegacy | Open — **the only functional blocker**, and partly disputed (see below) |
| [#162](https://github.com/alistair23/AutoMower-BLE/pull/162) | competing ECO/frost fix by AlirezaT, overlaps #161 | Open |
| [#166](https://github.com/alistair23/AutoMower-BLE/pull/166) | rename `GetFrostSensorEnabledLegacy` (4476/6) to `GetLiftSensorLegacy` | Open — cherry-picked into this branch |

## Hardware evidence (2026-09-18, Gardena SILENO Minimo 250)

Settled by read-only probing on real hardware. This is the only hardware evidence
in the #161/#162 discussion; neither PR author claimed any.

| Register | What it actually is | How it was shown |
|---|---|---|
| **5370/1** | **Frost sensor** | Flipped `01`->`00` when frost was toggled off in the GARDENA app |
| **4476/6** | **Lift sensor** | Flipped `00`->`01`->`00` when the mower was physically lifted |
| 4692/6 | Eco mode | Uncontested |
| 5412/1 | Does not exist on this model | `INVALID_ID(7)` |

Conclusions:

- **#161's main correction is confirmed**: ECO = 4692/6,5 and FrostSensor = 5370/1,2.
- **Our `SetFrostSensorEnabledLegacy` at 4476/5 is wrong.** 4476 is lift sensing,
  as AlirezaT claimed. Commit `40ce4ec` should be dropped from #161.
- **#162's `FrostSensorV1` at 5412/1,2 is also wrong**, at least on the Minimo 250 --
  the very model AlirezaT compared against. That group is not implemented there.
- **Upstream's existing `GetFrostSensorEnabledLegacy` at 4476/6 is misnamed** and
  predates our branch. It is a lift-sensor read. Worth a separate upstream issue.

Action: drop `40ce4ec` from #161, leaving the confirmed and uncontested main
correction, which is then directly mergeable. Separately, remove the
`SetFrostSensorEnabledLegacy` fallback from `GardenaMower-BLE-MQTT` -- on models
where `GetFrostSensorEnabled` fails (e.g. the Husqvarna 305) the bridge currently
writes to 4476/5, adjacent to a confirmed lift sensor, on every `FROST_SENSOR`
command.

## #161 is partly disputed by #162

[Comment of 2026-09-13](https://github.com/alistair23/AutoMower-BLE/pull/161#issuecomment-5655674896)
from AlirezaT, who opened the competing #162:

- **Confirms** our main correction: ECO = 4692/6,5 and FrostSensor = 5370/1,2,
  verified against the GARDENA Bluetooth 9.2.0 app and a Minimo app/HA comparison.
- **Rejects** our `SetFrostSensorEnabledLegacy` at 4476/5. They map legacy frost
  (`FrostSensorV1`) to **5412/1 (read) and 5412/2 (write)**, and say 4476/5 and
  4476/6 are **lift-sensor reads**, so 4476/5 should not become a frost setter.
- They offer to consolidate into whichever PR the maintainer prefers, and do not
  claim hardware validation of the legacy module.

Checked against this repo:

- Major **5412 does not exist in protocol.json at all**, so #162 adds a new
  command group rather than remapping one.
- `GetFrostSensorEnabledLegacy` at 4476/6 **already exists in `upstream/main`**
  and predates our branch. If AlirezaT is right, the mislabel is upstream's
  pre-existing bug; our commit `40ce4ec` added a *setter* to an already-wrong
  pair rather than introducing the error.

### Why we cannot just drop commit `40ce4ec`

`GardenaMower-BLE-MQTT/mower_mqtt.py` actively **writes** via
`SetFrostSensorEnabledLegacy` on both branches of the `FROST_SENSOR` handler
(lines ~1426 and ~1440), as a fallback around `SetFrostSensorEnabled`.

Worse for our hardware: `GetFrostSensorEnabled` is in that bridge's
`UNSUPPORTED_COMMANDS_WHITELIST`, so on the 305 the **first** branch fires and
every `FROST_SENSOR` command writes to 4476/5 *before* trying 5370/2. If 4476 is
lift sensing, that is a write to the wrong register on every frost command.

Action: settle 4476 vs 5412 before relying on the legacy path. Cheapest resolution
is to ask the maintainer to consolidate #161 and #162, adopting #162's 5412
mapping for the legacy pair and keeping #161's credited main correction.

## What is still in `combined-fixes`

`git diff upstream/main combined-fixes` touches 4 files:

1. `automower_ble/protocol.json` + `tests/test_requests.py` — the #161 frost/eco
   remap and `SetFrostSensorEnabledLegacy`. Functional; blocks dropping the branch.
   The remap is uncontested; the 4476/5 legacy setter is disputed (see above).
2. `automower_ble/protocol.py` — the #158 leftover. Upstream took the base
   `AuthenticationFailed` warning, but not our `pairing_requires_confirmation`
   flag and its two follow-up `logger.error` calls. Log-only, no behaviour change.
3. `COMBINED_FIXES_STATUS.md` — this file, local-only, never goes upstream.

`main` needs no rebase: it is 0 ahead / 2 behind `upstream/main`, a clean fast-forward.

## Steps to drop the branch

1. Get #161 and #166 merged (#161 no longer carries the legacy setter).
2. Decide on the #158 remainder — either push it upstream or drop those log lines
   locally. If dropped, #161 is the sole blocker.
3. **Wait for a PyPI release.** PyPI `automower-ble` 0.2.9 was uploaded
   2026-06-20, but #151 (`75e10fe`, 2026-07-07) and #158 (`4bf4b00`, 2026-07-16)
   landed after it. Upstream `main` is ahead of the last release, so switching to
   the plain PyPI package today would silently lose the #151 fix we depend on.
   Upstream must cut a release containing #161 first.
4. Switch `GardenaMower-BLE-MQTT/requirements.txt` from
   `git+https://github.com/gruijter/AutoMower-BLE.git@combined-fixes` to the plain
   `automower-ble` PyPI package, pinned to that release.
5. Delete `combined-fixes`.

Superseded, no action needed: #152, #153 (closed — covered by #148).
