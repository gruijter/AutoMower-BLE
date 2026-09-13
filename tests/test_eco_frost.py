"""Independent ECO and frost packets from the app's command definitions."""

import json
from importlib.resources import files

import pytest

from automower_ble.helpers import crc
from automower_ble.protocol import Command


@pytest.fixture
def protocol():
    return json.loads(files("automower_ble").joinpath("protocol.json").read_text())


@pytest.mark.parametrize(
    ("name", "group", "read_id", "write_id"),
    [
        ("EcoMode", 4692, 6, 5),
        ("FrostSensor", 5370, 1, 2),
        ("FrostSensorLegacy", 5412, 1, 2),
    ],
)
@pytest.mark.parametrize("enabled", [False, True])
def test_independent_setting_packets(protocol, name, group, read_id, write_id, enabled):
    suffix = "EnabledLegacy" if name.endswith("Legacy") else "Enabled"
    stem = name.removesuffix("Legacy")
    read = Command(1197489078, protocol[f"Get{stem}{suffix}"])
    write = Command(1197489078, protocol[f"Set{stem}{suffix}"])
    request = read.generate_request()
    setting = write.generate_request(enabled=enabled)
    # Assert literal group/id and payload, not expectations derived from JSON.
    assert request[12:16] == group.to_bytes(2, "little") + read_id.to_bytes(2, "little")
    assert request[16:18] == b"\x00\x00"
    assert setting[12:16] == group.to_bytes(2, "little") + write_id.to_bytes(
        2, "little"
    )
    assert setting[16:19] == b"\x01\x00" + bytes([enabled])
    assert setting[-2] == crc(setting, 1, len(setting) - 3)

    # Synthetic successful response with an independently specified command ID.
    response = bytearray.fromhex("02fd1200b63b604701db01af00000000000100000003")
    response[12:16] = group.to_bytes(2, "little") + read_id.to_bytes(2, "little")
    response[19] = enabled
    response[-2] = crc(response, 1, len(response) - 3)
    assert read.validate_command_response(response)
    # The upstream decoder represents protocol booleans as integer 0/1.
    assert read.parse_response(response)["response"] == int(enabled)


def test_no_unrelated_frost_or_loop_aliases(protocol):
    assert "GetChargingStationLoopSignalGeneration" not in protocol
    assert "SetChargingStationLoopSignalGeneration" not in protocol
    for name, definition in protocol.items():
        if "Frost" in name:
            assert definition["major"] in (5370, 5412)
            assert definition["major"] != 4476
