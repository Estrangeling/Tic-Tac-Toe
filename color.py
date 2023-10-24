import numba as nb
import numpy as np
from math import atan2, cos, sin, pi
from typing import Callable, Tuple

D65_Xw = 0.9504559270516716
D65_Zw = 1.0890577507598784
D50_Xw = 0.96420288
D50_Zw = 0.82490540

D65_Xr = 0.4123835774573348
D65_Xg = 0.35758636076837935
D65_Xb = 0.18048598882595746
D65_Yr = 0.21264225112116675
D65_Yg = 0.7151677022795175
D65_Yb = 0.07219004659931565
D65_Zr = 0.019324834131038457
D65_Zg = 0.11918543851645445
D65_Zb = 0.9505474781123853

D65_Rx = 3.2410639132702483
D65_Ry = -1.5374434989773638
D65_Rz = -0.49863738352233855
D65_Gx = -0.9692888172936756
D65_Gy = 1.875993314670902
D65_Gz = 0.04157078604801982
D65_Bx = 0.05564381729909414
D65_By = -0.20396692403457678
D65_Bz = 1.0569503107394616

D50_Xr = 0.43603484825656935
D50_Xg = 0.3851166943865836
D50_Xb = 0.14305133735684697
D50_Yr = 0.22248792538138254
D50_Yg = 0.7169037981483454
D50_Yb = 0.06060827647027179
D50_Zr = 0.013915901710730823
D50_Zg = 0.09706054515938503
D50_Zb = 0.7139289531298839

D50_Rx = 3.1342757757453534
D50_Ry = -1.6172769674977776
D50_Rz = -0.4907238602027905
D50_Gx = -0.9787936355010586
D50_Gy = 1.9161606866577585
D50_Gz = 0.033452266912100515
D50_Bx = 0.07197630801411643
D50_By = -0.2289831961913926
D50_Bz = 1.4057168648822214

LAB_F0 = 216 / 24389
LAB_F1 = 841 / 108
LAB_F2 = 4 / 29
LAB_F3 = LAB_F0 ** (1 / 3)
LAB_F4 = 1 / LAB_F1
LAB_F5 = 1 / 2.4
LAB_F6 = 0.04045 / 12.92
RtD = 180 / pi
DtR = pi / 180


@nb.njit(cache=True, fastmath=True)
def extrema(a: float, b: float, c: float) -> Tuple[float]:
    i = 2
    if b > c:
        b, c = c, b
        i = 1

    if a > b:
        a, b = b, a

    if b > c:
        b, c = c, b
        i = 0

    return i, a, c


@nb.njit(cache=True, fastmath=True)
def hue(r: float, g: float, b: float, d: float, i: float) -> float:
    if i == 2:
        h = 2 / 3 + (r - g) / (6 * d)
    elif i:
        h = 1 / 3 + (b - r) / (6 * d)
    else:
        h = (g - b) / (6 * d)

    return h % 1


@nb.njit(cache=True, fastmath=True)
def HSL_pixel(r: float, g: float, b: float) -> Tuple[float]:
    i, x, z = extrema(r, g, b)
    s = x + z
    d = z - x
    avg = s / 2

    return (hue(r, g, b, d, i), d / (1 - abs(s - 1)), avg) if d else (0, 0, avg)


@nb.njit(cache=True, fastmath=True)
def HSV_pixel(r: float, g: float, b: float) -> Tuple[float]:
    i, x, z = extrema(r, g, b)
    d = z - x
    return (hue(r, g, b, d, i), d / z, z) if d else (0, 0, z)


@nb.njit(cache=True, parallel=True)
def convert(img: np.ndarray, mode: Callable) -> np.ndarray:
    height, width = img.shape[:2]
    out = np.empty_like(img)
    for y in nb.prange(height):
        for x in nb.prange(width):
            a, b, c = img[y, x]
            out[y, x] = mode(a, b, c)

    return out


@nb.njit
def RGB_to_HSL(img: np.ndarray) -> np.ndarray:
    return convert(img, HSL_pixel)


@nb.njit
def RGB_to_HSV(img: np.ndarray) -> np.ndarray:
    return convert(img, HSV_pixel)


@nb.njit(cache=True, fastmath=True)
def HSL_helper(h: float, n: float) -> float:
    k = (n + 12 * h) % 12
    return max(-1, min(k - 3, 9 - k, 1))


@nb.njit(cache=True, fastmath=True)
def RGB_from_HSL_pixel(h: float, s: float, l: float):
    a = s * min(l, 1 - l)
    return l - a * HSL_helper(h, 0), l - a * HSL_helper(h, 8), l - a * HSL_helper(h, 4)


@nb.njit(cache=True, fastmath=True)
def HSV_helper(h: float, n: float) -> float:
    k = (n + 6 * h) % 6
    return max(0, min(k, 4 - k, 1))


@nb.njit(cache=True, fastmath=True)
def RGB_from_HSV_pixel(h: float, s: float, v: float):
    a = v * s
    return v - a * HSV_helper(h, 5), v - a * HSV_helper(h, 3), v - a * HSV_helper(h, 1)


@nb.njit(cache=True)
def HSL_short(h: float, s: float, l: float) -> Tuple[float]:
    return RGB_from_HSL_pixel(h, s, l) if s else (l, l, l)


@nb.njit(cache=True)
def HSV_short(h: float, s: float, v: float) -> Tuple[float]:
    return RGB_from_HSV_pixel(h, s, v) if s else (v, v, v)


@nb.njit
def HSL_to_RGB(hsl: np.ndarray) -> np.ndarray:
    return convert(hsl, HSL_short)


@nb.njit
def HSV_to_RGB(hsv: np.ndarray) -> np.ndarray:
    return convert(hsv, HSV_short)


@nb.njit(cache=True, fastmath=True)
def gamma_expand(c: float) -> float:
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


@nb.njit(cache=True, fastmath=True)
def LABF(f: float) -> float:
    return f ** (1 / 3) if f >= LAB_F0 else LAB_F1 * f + LAB_F2


@nb.njit(cache=True, fastmath=True)
def LABINVF(f: float) -> float:
    return f**3 if f >= LAB_F3 else LAB_F4 * (f - LAB_F2)


@nb.njit(cache=True, fastmath=True)
def gamma_contract(n: float) -> float:
    n = n * 12.92 if n <= LAB_F6 else (1.055 * n**LAB_F5) - 0.055
    return 0.0 if n < 0 else (1.0 if n > 1 else n)


@nb.njit(cache=True, fastmath=True)
def RGB_to_LCh_D65(r: float, g: float, b: float) -> Tuple[float]:
    b = gamma_expand(b)
    g = gamma_expand(g)
    r = gamma_expand(r)
    x = LABF((D65_Xr * r + D65_Xg * g + D65_Xb * b) / D65_Xw)
    y = LABF(D65_Yr * r + D65_Yg * g + D65_Yb * b)
    z = LABF((D65_Zr * r + D65_Zg * g + D65_Zb * b) / D65_Zw)
    m = 500 * (x - y)
    n = 200 * (y - z)
    return 116 * y - 16, (m * m + n * n) ** 0.5, (atan2(n, m) * RtD) % 360


@nb.njit(cache=True, fastmath=True)
def LCh_D65_to_RGB(l: float, c: float, h: float) -> Tuple[float]:
    h *= DtR
    l = (l + 16) / 116
    x = D65_Xw * LABINVF(l + c * cos(h) / 500)
    y = LABINVF(l)
    z = D65_Zw * LABINVF(l - c * sin(h) / 200)
    r = D65_Rx * x + D65_Ry * y + D65_Rz * z
    g = D65_Gx * x + D65_Gy * y + D65_Gz * z
    b = D65_Bx * x + D65_By * y + D65_Bz * z
    m = min(r, g, b)
    if m < 0:
        r -= m
        g -= m
        b -= m

    return gamma_contract(r), gamma_contract(g), gamma_contract(b)


@nb.njit(cache=True, fastmath=True)
def RGB_to_LCh_D50(r: float, g: float, b: float) -> Tuple[float]:
    b = gamma_expand(b)
    g = gamma_expand(g)
    r = gamma_expand(r)
    x = LABF((D50_Xr * r + D50_Xg * g + D50_Xb * b) / D50_Xw)
    y = LABF(D50_Yr * r + D50_Yg * g + D50_Yb * b)
    z = LABF((D50_Zr * r + D50_Zg * g + D50_Zb * b) / D50_Zw)
    m = 500 * (x - y)
    n = 200 * (y - z)
    return 116 * y - 16, (m * m + n * n) ** 0.5, (atan2(n, m) * RtD) % 360


@nb.njit(cache=True, fastmath=True)
def LCh_D50_to_RGB(l: float, c: float, h: float) -> Tuple[float]:
    h *= DtR
    l = (l + 16) / 116
    x = D50_Xw * LABINVF(l + c * cos(h) / 500)
    y = LABINVF(l)
    z = D50_Zw * LABINVF(l - c * sin(h) / 200)
    r = D50_Rx * x + D50_Ry * y + D50_Rz * z
    g = D50_Gx * x + D50_Gy * y + D50_Gz * z
    b = D50_Bx * x + D50_By * y + D50_Bz * z
    m = min(r, g, b)
    if m < 0:
        r -= m
        g -= m
        b -= m

    return gamma_contract(r), gamma_contract(g), gamma_contract(b)


@nb.njit(cache=True, parallel=True)
def loop_LCh(img: np.ndarray, mode: Callable) -> np.ndarray:
    height, width = img.shape[:2]
    out = np.empty_like(img)
    for y in nb.prange(height):
        for x in nb.prange(width):
            a, b, c = img[y, x]
            out[y, x] = mode(a, b, c)

    return out


@nb.njit
def IMG_to_LCh_D65(img: np.ndarray) -> np.ndarray:
    return loop_LCh(img, RGB_to_LCh_D65)


@nb.njit
def LCh_D65_to_IMG(lch: np.ndarray) -> np.ndarray:
    return loop_LCh(lch, LCh_D65_to_RGB)


@nb.njit
def IMG_to_LCh_D50(img: np.ndarray) -> np.ndarray:
    return loop_LCh(img, RGB_to_LCh_D50)


@nb.njit
def LCh_D50_to_IMG(lch: np.ndarray) -> np.ndarray:
    return loop_LCh(lch, LCh_D50_to_RGB)


SEXTET = (
    "255.{:03d}.000",
    "{:03d}.255.000",
    "000.255.{:03d}",
    "000.{:03d}.255",
    "{:03d}.000.255",
    "255.000.{:03d}",
)
SIX = (0, 510, 510, 1020, 1020, 1530)


def spectrum_position(n: int) -> str:
    n %= 1530
    i = n // 255
    return SEXTET[i].format(abs(n - SIX[i]))
