# SPDX-FileCopyrightText: 2025 Ritesh
# SPDX-License-Identifier: MIT

import pathlib
import sys
import types

# 1) Ensure project root (where adafruit_ili9341.py lives) is importable
ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# 2) Stub 'busdisplay' so the driver can import BusDisplay without hardware deps
busdisplay_stub = types.ModuleType("busdisplay")


def _to_bytes(obj):
    if obj is None:
        return b""
    if isinstance(obj, (bytes, bytearray, memoryview)):
        return bytes(obj)
    if isinstance(obj, (list, tuple)):
        try:
            return bytes(obj)
        except Exception:
            return b""
    return b""


def _pick_bytes_from_args_kwargs(args, kwargs):
    # Prefer explicit kwarg value that looks bytes-like
    for v in kwargs.values():
        b = _to_bytes(v)
        if b:
            return b
    # Common names: init_sequence, init, sequence
    for key in ("init_sequence", "init", "sequence"):
        if key in kwargs:
            b = _to_bytes(kwargs[key])
            if b:
                return b
    # Otherwise, search positional args after the bus (args[0] usually 'bus')
    best = b""
    for v in args[1:]:
        b = _to_bytes(v)
        if len(b) > len(best):
            best = b
    return best


class BusDisplay:
    # Accept any signature; extract a bytes-like init sequence robustly
    def __init__(self, *args, **kwargs):
        init_seq = _pick_bytes_from_args_kwargs(args, kwargs)
        self.init_sequence = init_seq
        self._busdisplay_debug = {
            "arg_types": [type(a).__name__ for a in args],
            "kw_keys": list(kwargs.keys()),
            "init_seq_len": len(init_seq),
        }


busdisplay_stub.BusDisplay = BusDisplay
sys.modules["busdisplay"] = busdisplay_stub

import adafruit_ili9341 as ili


def _last_madctl(seq: bytes) -> int:
    """
    Return the last MADCTL data byte written in the init sequence.

    Init sequence encoding per Adafruit style:
      [CMD][LEN|0x80 if delay][<LEN data bytes>][<1 delay byte if delay flag set>]
    """
    cmd = ili._MADCTL
    i = 0
    last = None
    L = len(seq)
    while i < L:
        if i >= L:
            break
        c = seq[i]
        i += 1
        if i >= L:
            break
        length_byte = seq[i]
        i += 1

        delay_flag = (length_byte & 0x80) != 0
        n = length_byte & 0x7F  # actual data length

        # If this is MADCTL, expect exactly 1 data byte
        if c == cmd:
            assert n == 1, f"Expected MADCTL length 1, got {n}"
            assert i + n <= L, "MADCTL payload truncated"
            last = seq[i]  # the one data byte
        # advance over data
        i += n
        # consume delay byte if present
        if delay_flag:
            i += 1
    assert last is not None, f"No MADCTL write found. seq={seq.hex(' ')}"
    return last


def test_color_order_defaults_rgb():
    d = ili.ILI9341(bus=object())
    assert len(getattr(d, "init_sequence", b"")) > 0, (
        f"Driver did not pass an init sequence to BusDisplay. "
        f"debug={getattr(d, '_busdisplay_debug', {})}"
    )
    madctl = _last_madctl(d.init_sequence)
    # Default is RGB => BGR bit NOT set
    assert (madctl & ili._MADCTL_BGR) == 0


def test_color_order_bgr_sets_bit():
    d = ili.ILI9341(bus=object(), color_order="BGR")
    assert len(getattr(d, "init_sequence", b"")) > 0, (
        f"Driver did not pass an init sequence to BusDisplay. "
        f"debug={getattr(d, '_busdisplay_debug', {})}"
    )
    madctl = _last_madctl(d.init_sequence)
    # BGR => BGR bit set
    assert (madctl & ili._MADCTL_BGR) == ili._MADCTL_BGR


def test_legacy_bgr_true_sets_bit():
    d = ili.ILI9341(bus=object(), bgr=True)
    assert len(getattr(d, "init_sequence", b"")) > 0, (
        f"Driver did not pass an init sequence to BusDisplay. "
        f"debug={getattr(d, '_busdisplay_debug', {})}"
    )
    madctl = _last_madctl(d.init_sequence)
    # legacy bgr=True still sets the bit
    assert (madctl & ili._MADCTL_BGR) == ili._MADCTL_BGR


def _has_invon(seq: bytes) -> bool:
    # Scan TLV-style sequence; check command 0x21 is present
    i, L = 0, len(seq)
    while i + 2 <= L:
        cmd = seq[i]
        i += 1
        lb = seq[i]
        i += 1
        delay = (lb & 0x80) != 0
        n = lb & 0x7F
        i += n
        if delay:
            i += 1
        if cmd == 0x21:
            return True
    return False


def test_invert_true_appends_invon():
    d = ili.ILI9341(bus=object(), invert=True)
    assert _has_invon(d.init_sequence)
