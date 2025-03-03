# dummy_bms.py
from bleak.backends.characteristic import BleakGATTCharacteristic
from bleak.backends.device import BLEDevice
from bleak.uuids import normalize_uuid_str

from custom_components.bms_ble.const import (
    ATTR_BATTERY_CHARGING,
    ATTR_CURRENT,
    ATTR_POWER,
    ATTR_TEMPERATURE,
    ATTR_VOLTAGE,
)

from .basebms import BaseBMS, BMSsample

class BMS(BaseBMS):
    """Dummy battery class implementation."""

    def __init__(self, ble_device: BLEDevice, reconnect: bool = False) -> None:
        """Initialize BMS."""
        super().__init__(__name__, ble_device, reconnect)
        self._buffer = bytearray()
        self._last_response = None

    @staticmethod
    def matcher_dict_list() -> list[dict]:
        """Provide BluetoothMatcher definition."""
        return [{"local_name": "dummy", "connectable": True}]

    @staticmethod
    def device_info() -> dict[str, str]:
        """Return device information for the battery management system."""
        return {"manufacturer": "Dummy Manufacturer", "model": "dummy model"}

    @staticmethod
    def uuid_services() -> list[str]:
        """Return list of 128-bit UUIDs of services required by BMS."""
        return [normalize_uuid_str("0000ffe0-0000-1000-8000-00805f9b34fb")]

    @staticmethod
    def uuid_rx() -> str:
        """Return 16-bit UUID of characteristic that provides notification/read property."""
        return "0000ffe1-0000-1000-8000-00805f9b34fb"

    @staticmethod
    def uuid_tx() -> str:
        """Return 16-bit UUID of characteristic that provides write property."""
        return "0000ffe1-0000-1000-8000-00805f9b34fb"

    @staticmethod
    def _calc_values() -> set[str]:
        return {
            ATTR_POWER,
            ATTR_BATTERY_CHARGING,
        }

    def _notification_handler(self, sender: BleakGATTCharacteristic, data: bytearray) -> None:
        """Handle the RX characteristics notify event (new data arrives)."""
        if data.startswith(b'\x7E\xA1'):
            self._buffer.clear()
        self._buffer += data
        if self._buffer.endswith(b'\x55'):
            self._last_response = self._buffer
            self._buffer.clear()
            self._data_event.set()

    async def _async_update(self) -> BMSsample:
        """Update battery status information."""
        self._log.debug("replace with command to UUID %s", BMS.uuid_tx())
        await self._send(b"<some_command>")
        await self._data_event.wait()
        data = self._last_response

        # Parse data
        voltage = int.from_bytes(data[1:3], byteorder='little') * 0.01
        current = int.from_bytes(data[3:5], byteorder='little', signed=True) * 0.1
        temperature = int.from_bytes(data[5:7], byteorder='little') * 0.1

        return {
            ATTR_VOLTAGE: voltage,
            ATTR_CURRENT: current,
            ATTR_TEMPERATURE: temperature,
        }
