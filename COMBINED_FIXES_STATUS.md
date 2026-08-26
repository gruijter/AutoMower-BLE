# combined-fixes → upstream status

`combined-fixes` can be dropped once these 3 PRs are merged into `alistair23/AutoMower-BLE:main`:

| PR | Fix | Status |
|----|-----|--------|
| [#151](https://github.com/alistair23/AutoMower-BLE/pull/151) | parse_response crash on empty response | Open |
| [#161](https://github.com/alistair23/AutoMower-BLE/pull/161) | swapped eco mode / frost sensor mapping + SetFrostSensorEnabledLegacy | Open |
| [#158](https://github.com/alistair23/AutoMower-BLE/pull/158) | AuthenticationFailed pairing diagnostics (by kelvan) | Draft |

Once all 3 are merged: switch `GardenaMower-BLE-MQTT/requirements.txt` from
`git+https://github.com/gruijter/AutoMower-BLE.git@combined-fixes` to the plain
`automower-ble` PyPI package, and delete `combined-fixes`.

Superseded, no action needed: #152, #153 (closed — covered by #148).
