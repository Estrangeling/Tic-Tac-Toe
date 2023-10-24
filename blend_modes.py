import numba as nb
import numpy as np
from color import (
    RGB_to_HSL,
    RGB_to_HSV,
    HSL_to_RGB,
    HSV_to_RGB,
    IMG_to_LCh_D65,
    LCh_D65_to_IMG,
    IMG_to_LCh_D50,
    LCh_D50_to_IMG,
)


@nb.njit(cache=True, fastmath=True, parallel=True)
def blend_lighten(base: np.ndarray, top: np.ndarray) -> np.ndarray:
    return np.maximum(base, top)


@nb.njit(cache=True, fastmath=True, parallel=True)
def blend_screen(base: np.ndarray, top: np.ndarray) -> np.ndarray:
    return base + top - base * top


@nb.njit(cache=True, fastmath=True, parallel=True)
def blend_color_dodge(base: np.ndarray, top: np.ndarray) -> np.ndarray:
    height, width = base.shape[:2]
    result = np.ones_like(base)
    for y in nb.prange(height):
        for x in nb.prange(width):
            for i in (0, 1, 2):
                t = top[y, x, i]
                if t != 1:
                    result[y, x, i] = min(1, base[y, x, i] / (1 - t))

    return result


@nb.njit(cache=True, fastmath=True, parallel=True)
def blend_linear_dodge(base: np.ndarray, top: np.ndarray) -> np.ndarray:
    return np.minimum(1, base + top)


@nb.njit(cache=True, fastmath=True, parallel=True)
def blend_darken(base: np.ndarray, top: np.ndarray) -> np.ndarray:
    return np.minimum(base, top)


@nb.njit(cache=True, fastmath=True, parallel=True)
def blend_multiply(base: np.ndarray, top: np.ndarray) -> np.ndarray:
    return base * top


@nb.njit(cache=True, fastmath=True, parallel=True)
def blend_color_burn(base: np.ndarray, top: np.ndarray) -> np.ndarray:
    height, width = base.shape[:2]
    result = np.zeros_like(base)
    for y in nb.prange(height):
        for x in nb.prange(width):
            for i in (0, 1, 2):
                t = top[y, x, i]
                if t != 0:
                    result[y, x, i] = max(0, 1 - (1 - base[y, x, i]) / t)

    return result


@nb.njit(cache=True, fastmath=True, parallel=True)
def blend_linear_burn(base: np.ndarray, top: np.ndarray) -> np.ndarray:
    return np.maximum(0, base + top - 1.0)


@nb.njit(cache=True, fastmath=True, parallel=True)
def blend_overlay(base: np.ndarray, top: np.ndarray) -> np.ndarray:
    height, width = base.shape[:2]
    result = np.empty_like(base)
    for y in nb.prange(height):
        for x in nb.prange(width):
            for i in (0, 1, 2):
                b = base[y, x, i]
                t = top[y, x, i]
                result[y, x, i] = (
                    2 * b * t if b < 0.5 else 2 * b + 2 * t - 2 * b * t - 1
                )

    return result


@nb.njit(cache=True, fastmath=True, parallel=True)
def blend_soft_light(base: np.ndarray, top: np.ndarray) -> np.ndarray:
    return (1 - 2 * top) * base**2 + 2 * base * top


@nb.njit
def blend_hard_light(base: np.ndarray, top: np.ndarray) -> np.ndarray:
    return blend_overlay(top, base)


@nb.njit(cache=True, fastmath=True)
def vivid_light(b: float, t: float) -> float:
    if t < 0.5:
        return max(0, 1 - (1 - b) / (2 * t)) if t else 0
    else:
        return min(1, b / (2 - 2 * t)) if t != 1 else 1


@nb.njit(cache=True, fastmath=True, parallel=True)
def blend_vivid_light(base: np.ndarray, top: np.ndarray) -> np.ndarray:
    height, width = base.shape[:2]
    result = np.zeros_like(base)
    for y in nb.prange(height):
        for x in nb.prange(width):
            for i in (0, 1, 2):
                result[y, x, i] = vivid_light(base[y, x, i], top[y, x, i])

    return result


@nb.njit(cache=True, fastmath=True, parallel=True)
def blend_linear_light(base: np.ndarray, top: np.ndarray) -> np.ndarray:
    return np.clip(base + 2 * top - 1, 0.0, 1.0)


@nb.njit(cache=True, fastmath=True, parallel=True)
def blend_pin_light(base: np.ndarray, top: np.ndarray) -> np.ndarray:
    height, width = base.shape[:2]
    result = np.zeros_like(base)
    for y in nb.prange(height):
        for x in nb.prange(width):
            for i in (0, 1, 2):
                b = base[y, x, i]
                t = top[y, x, i]
                result[y, x, i] = min(b, 2 * t) if t < 0.5 else max(b, 2 * t - 1)

    return result


@nb.njit(cache=True, fastmath=True, parallel=True)
def blend_reflect(base: np.ndarray, top: np.ndarray) -> np.ndarray:
    height, width = base.shape[:2]
    result = np.ones_like(base)
    for y in nb.prange(height):
        for x in nb.prange(width):
            for i in (0, 1, 2):
                t = top[y, x, i]
                if t != 1:
                    result[y, x, i] = min(1, base[y, x, i] ** 2 / (1 - t))

    return result


@nb.njit(cache=True, fastmath=True, parallel=True)
def blend_difference(base: np.ndarray, top: np.ndarray) -> np.ndarray:
    return np.abs(base - top)


@nb.njit(cache=True, fastmath=True, parallel=True)
def blend_exclusion(base: np.ndarray, top: np.ndarray) -> np.ndarray:
    return base + top - 2 * base * top


@nb.njit(cache=True, fastmath=True, parallel=True)
def blend_subtract(base: np.ndarray, top: np.ndarray) -> np.ndarray:
    return np.maximum(0, base - top)


@nb.njit(cache=True, fastmath=True, parallel=True)
def blend_grain_extract(base: np.ndarray, top: np.ndarray) -> np.ndarray:
    return np.clip(base + top - 0.5, 0, 1)


@nb.njit(cache=True, fastmath=True, parallel=True)
def blend_grain_merge(base: np.ndarray, top: np.ndarray) -> np.ndarray:
    return np.clip(base - top + 0.5, 0, 1)


@nb.njit(cache=True, fastmath=True, parallel=True)
def blend_divide(base: np.ndarray, top: np.ndarray) -> np.ndarray:
    height, width = base.shape[:2]
    result = np.ones_like(base)
    for y in nb.prange(height):
        for x in nb.prange(width):
            for i in (0, 1, 2):
                t = top[y, x, i]
                if t != 0:
                    result[y, x, i] = min(1, base[y, x, i] / t)

    return result


@nb.njit
def blend_HSV_Color(base: np.ndarray, top: np.ndarray) -> np.ndarray:
    hsv = RGB_to_HSV(base)
    hsv[..., 0:2] = RGB_to_HSV(top)[..., 0:2]
    return HSV_to_RGB(hsv)


@nb.njit
def blend_HSL_Color(base: np.ndarray, top: np.ndarray) -> np.ndarray:
    hsl = RGB_to_HSL(base)
    hsl[..., 0:2] = RGB_to_HSL(top)[..., 0:2]
    return HSL_to_RGB(hsl)


@nb.njit
def blend_color_lux(base: np.ndarray, top: np.ndarray) -> np.ndarray:
    hsv = RGB_to_HSV(base)
    hsv[..., 0:2] = RGB_to_HSV(top)[..., 0:2]
    return HSL_to_RGB(hsv)


@nb.njit
def blend_color_nox(base: np.ndarray, top: np.ndarray) -> np.ndarray:
    hsl = RGB_to_HSL(base)
    hsl[..., 0:2] = RGB_to_HSL(top)[..., 0:2]
    return HSV_to_RGB(hsl)


@nb.njit
def blend_color_LCh_D65(base: np.ndarray, top: np.ndarray) -> np.ndarray:
    lch = IMG_to_LCh_D65(base)
    lch[..., 1:3] = IMG_to_LCh_D65(top)[..., 1:3]
    return LCh_D65_to_IMG(lch)


@nb.njit
def blend_color_LCh_D50(base: np.ndarray, top: np.ndarray) -> np.ndarray:
    lch = IMG_to_LCh_D50(base)
    lch[..., 1:3] = IMG_to_LCh_D50(top)[..., 1:3]
    return LCh_D50_to_IMG(lch)
