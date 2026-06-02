"""
tencent_nav.py
--------------
Detection and auto-click helpers for Chinese (Tencent) edition UI overlays.

These popups appear exclusively in com.tencent.tmgp.supercell.clashroyale and
would never be visible when running the global version, so it is safe to run
the checks unconditionally — they will simply return None on a global build.

Buttons handled
---------------
* 确定 (queding)  — OK / Confirm dialog
* 关闭 (guanbi)   — Close / dismiss dialog
* 领取全部 (lingquan) — Collect All rewards
"""

from pyclashbot.detection.image_rec import find_image
from pyclashbot.emulators.base import CHINESE_CLASH_PACKAGE

# Tolerance values tuned for the reference images supplied.
# Queding uses a lower value so older/slightly-different reference images still match.
_TOLERANCE_QUEDING = 0.72
_TOLERANCE_GUANBI = 0.85
_TOLERANCE_LINGQUAN = 0.85


# ---------------------------------------------------------------------------
# Low-level: detect a single button in an already-captured screenshot
# ---------------------------------------------------------------------------

def _find_queding(screenshot):
    """Return (x, y) if 确定 (OK) button is visible, else None."""
    return find_image(screenshot, "tencent_queding", tolerance=_TOLERANCE_QUEDING)


def _find_guanbi(screenshot):
    """Return (x, y) if 关闭 (Close) button is visible, else None."""
    return find_image(screenshot, "tencent_guanbi", tolerance=_TOLERANCE_GUANBI)


def _find_lingquan(screenshot):
    """Return (x, y) if 领取全部 (Collect All) button is visible, else None."""
    return find_image(screenshot, "tencent_lingquan", tolerance=_TOLERANCE_LINGQUAN)


# ---------------------------------------------------------------------------
# High-level: handle all Tencent popups in one call
# ---------------------------------------------------------------------------

def handle_tencent_popups(emulator) -> bool:
    """
    Capture one screenshot and click any visible Tencent-specific UI button.

    Priority order: 领取全部 → 确定 → 关闭
    (Collect rewards before confirming, confirm before closing, so we don't
    accidentally dismiss a rewards dialog without collecting first.)

    Returns True if at least one button was clicked, False otherwise.

    This function is a no-op when called on non-Chinese emulator instances:
    the image-template search simply returns None every time, so there is no
    performance penalty worth worrying about (one extra ADB screencap per loop
    tick when the Chinese toggle is off is the worst case).
    """
    # Fast-path: skip if emulator is not running the Chinese package
    clash_pkg = getattr(emulator, "clash_package", None)
    if clash_pkg != CHINESE_CLASH_PACKAGE:
        return False

    try:
        screenshot = emulator.screenshot()
    except Exception as exc:
        print(f"[tencent_nav] screenshot failed: {exc}")
        return False

    clicked = False

    # 1 — 领取全部 (Collect All) has highest priority
    coord = _find_lingquan(screenshot)
    if coord is not None:
        print(f"[tencent_nav] Clicking 领取全部 (Collect All) at {coord}")
        emulator.click(coord[0], coord[1])
        clicked = True

    # 2 — 确定 (OK / Confirm)
    if not clicked:
        coord = _find_queding(screenshot)
        if coord is not None:
            print(f"[tencent_nav] Clicking 确定 (OK) at {coord}")
            emulator.click(coord[0], coord[1])
            clicked = True

    # 3 — 关闭 (Close / Dismiss)
    if not clicked:
        coord = _find_guanbi(screenshot)
        if coord is not None:
            print(f"[tencent_nav] Clicking 关闭 (Close) at {coord}")
            emulator.click(coord[0], coord[1])
            clicked = True

    return clicked
