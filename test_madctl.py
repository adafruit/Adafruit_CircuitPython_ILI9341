# SPDX-FileCopyrightText: 2025 Ritesh
#
# SPDX-License-Identifier: MIT

import pytest

from adafruit_ili9341 import ILI9341


class DummyBus:
    """A fake bus to avoid hardware dependency."""

    def __init__(self):
        self.commands = []

    def send(self, *args, **kwargs):
        self.commands.append((args, kwargs))


def extract_madctl_bytes(init_seq: bytes) -> bytes | None:
    """
    Helper to find MADCTL command (0x36) in the init sequence.
    Returns 2 bytes: [0x36, value] or None if not present.
    """
    for i in range(len(init_seq) - 2):
        if init_seq[i] == 0x36:
            return init_seq[i : i + 3]
    return None


def test_default_rgb_encoding():
    bus = DummyBus()
    disp = ILI9341(bus)
    madctl = extract_madctl_bytes(disp.init_sequence)
    assert madctl == b"\x36\x01\x38"  # Default RGB


def test_bgr_encoding():
    bus = DummyBus()
    disp = ILI9341(bus, bgr=True)
    madctl = extract_madctl_bytes(disp.init_sequence)
    assert madctl == b"\x36\x01\x30"  # BGR mode


def test_custom_madctl():
    bus = DummyBus()
    disp = ILI9341(bus, madctl=0b01011000)
    madctl = extract_madctl_bytes(disp.init_sequence)
    assert madctl == bytes([0x36, 0x01, 0b01011000])  # Custom override
