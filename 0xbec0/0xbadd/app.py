import asyncio
import time
import app
import machine
import struct

from system.espnow import espnow_service

BEACON_MAGIC = 0x52474442
HEADER_FORMAT = "<IIHB"
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)

MORSE_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
MORSE_CODES = (
    ".- -... -.-. -.. . ..-. --. .... .. .--- -.- .-.. -- -. --- .--. --.- "
    ".-. ... - ..- ...- .-- -..- -.-- --.. "
    "----- .---- ..--- ...-- ....- ..... -.... --... ---.. ----."
).split()
L = 0.5 # Long
S = 0.25 # Short


def encode_word(word):
    return [MORSE_CODES[MORSE_CHARS.index(c)] for c in word if c in MORSE_CHARS]


class BeaconMessage:
    def __init__(self, seq, mv, chan, msg):
        self.sequence, self.battery_mv = seq, mv
        self.channel, self.message = chan, msg

    @property
    def battery_volts(self):
        return self.battery_mv / 1000 if self.battery_mv else None


class BadgerDetectorApp(app.App):
    RSSI_MAX = -50
    RSSI_MIN = -90
    GAMMA = 3.5
    MAGIC_BYTES = b"BDGR"

    def __init__(self, config=None):
        self.hexpansion_config = config
        self.eye_left = machine.PWM(config.pin[2])
        self.eye_right = machine.PWM(config.pin[3])
        self.brightness = 0
        self._last_msg = time.ticks_ms()
        self._last_beacon = None
        self._lock = asyncio.Lock()
        self._pending = False
        self._event = None

        espnow_service.subscribe(
            handler=self._on_message,
            app=self,
            predicate=lambda e: e.msg.startswith(self.MAGIC_BYTES),
        )

    def _on_message(self, event):
        if not (self._pending or self._lock.locked()):
            self._pending = True
            self._event = event

    async def _display_message(self, event):
        try:
            async with self._lock:
                self._last_msg = time.ticks_ms()
                pct = (event.rssi - self.RSSI_MIN) / (self.RSSI_MAX - self.RSSI_MIN)
                self.brightness = int(min(1, max(0, pct)) ** self.GAMMA * 1023)
                self._last_beacon = beacon = self._unpack_beacon(event.msg)
                print("Badger:", beacon.message)
                await self.morse_pulses(beacon.message)
        finally:
            self.eye_left.duty(0)
            self.eye_right.duty(0)
            self._pending = False

    async def background_task(self):
        while True:
            event = self._event
            if event is None:
                await asyncio.sleep(0.05)
                continue
            self._event = None
            await self._display_message(event)

    def _unpack_beacon(self, payload):
        if len(payload) < HEADER_SIZE:
            raise ValueError("Beacon payload is too short")

        magic, seq, mv, chan = struct.unpack(HEADER_FORMAT, payload[:HEADER_SIZE])
        if magic != BEACON_MAGIC:
            raise ValueError("Not a Badger Beacon message")

        message = payload[HEADER_SIZE:]
        try:
            message = message.decode()
        except UnicodeError:
            pass  # keep raw bytes

        return BeaconMessage(seq, mv, chan, message)

    async def flash(self, brightness, duration):
        self.eye_left.duty(brightness)
        self.eye_right.duty(brightness)
        await asyncio.sleep(duration)

    async def morse_pulses(self, message):
        words = [encode_word(w) for w in message.upper().split()]
        for i, codes in enumerate(words):
            for j, code in enumerate(codes):
                for k, symbol in enumerate(code):
                    await self.flash(self.brightness, S if symbol == "." else L)
                    if k < len(code) - 1:
                        await self.flash(0, S)
                if j < len(codes) - 1:
                    await self.flash(0, L)
            if codes and i < len(words) - 1:
                await self.flash(0, L)


__app_export__ = BadgerDetectorApp
