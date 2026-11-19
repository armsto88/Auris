#!/usr/bin/env python3
"""Trace geometry for the Auris rev A board on JLCPCB's JLC04161H-7628 4-layer stack-up.

Two independent estimates for each line, which should agree to a few ohms:
  * closed-form: Wadell's grounded coplanar waveguide, Hammerstad-Jensen microstrip with Wheeler's
    thickness correction, and the IPC-2141 edge-coupled approximation for the differential pair;
    no solder mask;
  * a 2-D finite-difference field solver for the actual cross-section, including JLC's solder mask
    (1.2 mil over bare laminate, 0.6 mil over copper, er 3.8) and copper thickness.

Stack-up (jlcpcb.com/impedance, read 2026-11-19): L1 35 um / 7628 prepreg 0.2104 mm er 4.4 / L2 15.2 um /
core 1.065 mm er 4.6 / L3 15.2 um / 7628 prepreg 0.2104 mm er 4.4 / L4 35 um. L1 and L4 signals reference
L2 and L3 through one 0.2104 mm prepreg. Confirm the final widths with JLC's own impedance calculator before
ordering; the solver is a cross-check, not a replacement.

Usage: python3 hardware/layout/impedance.py           (prints the table used in hardware/layout/README.md)
"""
import math

import numpy as np
from scipy.optimize import brentq
from scipy.sparse import coo_matrix
from scipy.sparse.linalg import spsolve
from scipy.special import ellipk
from scipy.ndimage import binary_dilation

H = 0.2104          # L1-L2 prepreg, mm
ER = 4.4            # 7628 prepreg
T = 0.035           # finished outer copper, mm
MASK_LAM = 0.0305   # 1.2 mil solder mask over laminate
MASK_CU = 0.0152    # 0.6 mil over copper
ER_MASK = 3.8
ETA0 = 376.730313
C0 = 299792458.0
EPS0 = 8.8541878128e-12


# ---------- closed forms (no solder mask) ----------
def _kk(k):
    """K(k)/K(k') with modulus k."""
    return ellipk(k * k) / ellipk(1 - k * k)


def cpwg_closed(w, g, h=H, er=ER):
    """Grounded CPW (Wadell 3.4.3), zero-thickness conductors, infinite side grounds."""
    k = w / (w + 2 * g)
    k3 = math.tanh(math.pi * w / (4 * h)) / math.tanh(math.pi * (w + 2 * g) / (4 * h))
    a, b = _kk(k), _kk(k3)
    eeff = (1 + er * b / a) / (1 + b / a)
    return 60 * math.pi / math.sqrt(eeff) / (a + b)


def microstrip_closed(w, h=H, er=ER, t=T):
    """Hammerstad-Jensen with Wheeler's thickness correction."""
    u = w / h
    du1 = t / (math.pi * h) * math.log(1 + 4 * math.e / (t / h * (1 / math.tanh(math.sqrt(6.517 * u))) ** 2))
    dur = 0.5 * (1 + 1 / math.cosh(math.sqrt(er - 1))) * du1
    u1, ur = u + du1, u + dur

    def z_air(x):
        f = 6 + (2 * math.pi - 6) * math.exp(-((30.666 / x) ** 0.7528))
        return ETA0 / (2 * math.pi) * math.log(f / x + math.sqrt(1 + (2 / x) ** 2))

    def eeff(x):
        a = 1 + math.log((x ** 4 + (x / 52) ** 2) / (x ** 4 + 0.432)) / 49 + math.log(1 + (x / 18.1) ** 3) / 18.7
        b = 0.564 * ((er - 0.9) / (er + 3)) ** 0.053
        return (er + 1) / 2 + (er - 1) / 2 * (1 + 10 / x) ** (-a * b)

    e = eeff(ur) * (z_air(u1) / z_air(ur)) ** 2
    return z_air(ur) / math.sqrt(e)


def diff_closed(w, s, h=H, er=ER, t=T):
    """IPC-2141 edge-coupled microstrip approximation."""
    return 2 * microstrip_closed(w, h, er, t) * (1 - 0.48 * math.exp(-0.96 * s / h))


# ---------- 2-D field solver ----------
def _solve(cells_v, er_map, d):
    """Solve div(er grad V) = 0 on a node grid; cells_v: node array with NaN for free nodes, else fixed volts.
    er_map holds the relative permittivity of each cell (ny-1, nx-1). Returns field energy per unit length / eps0."""
    ny, nx = cells_v.shape
    free = np.isnan(cells_v)
    idx = -np.ones(cells_v.shape, dtype=np.int64)
    idx[free] = np.arange(free.sum())
    # permittivity on the four links of each node: average of the two cells beside the link
    erp = np.pad(er_map, 1, mode="edge")  # (ny+1, nx+1): cell (j,i) of erp ~ cell (j-1,i-1) of er_map
    rows, cols, vals = [], [], []
    rhs = np.zeros(free.sum())
    jj, ii = np.nonzero(free)
    diag = np.zeros(len(jj))
    for dj, di, ca, cb in ((0, 1, (0, 1), (1, 1)), (0, -1, (0, 0), (1, 0)), (1, 0, (1, 0), (1, 1)), (-1, 0, (0, 0), (0, 1))):
        e = 0.5 * (erp[jj + ca[0], ii + ca[1]] + erp[jj + cb[0], ii + cb[1]])
        nj, ni = jj + dj, ii + di
        ok = (nj >= 0) & (nj < ny) & (ni >= 0) & (ni < nx)
        e = np.where(ok, e, 0.0)  # outer box edge: Neumann
        diag += e
        njc, nic = np.clip(nj, 0, ny - 1), np.clip(ni, 0, nx - 1)
        nb_free = ok & free[njc, nic]
        rows.append(idx[jj, ii][nb_free]); cols.append(idx[njc, nic][nb_free]); vals.append(-e[nb_free])
        fixed = ok & ~free[njc, nic]
        np.add.at(rhs, idx[jj, ii][fixed], e[fixed] * cells_v[njc, nic][fixed])
    rows.append(idx[jj, ii]); cols.append(idx[jj, ii]); vals.append(diag)
    A = coo_matrix((np.concatenate(vals), (np.concatenate(rows), np.concatenate(cols))), shape=(len(jj), len(jj))).tocsr()
    V = cells_v.copy()
    V[free] = spsolve(A, rhs)
    # energy: sum over cells of er * |grad V|^2 * area / 2 (gradient from the cell's four corner nodes)
    gx = 0.5 * ((V[:-1, 1:] - V[:-1, :-1]) + (V[1:, 1:] - V[1:, :-1])) / d
    gy = 0.5 * ((V[1:, :-1] - V[:-1, :-1]) + (V[1:, 1:] - V[:-1, 1:])) / d
    return 0.5 * np.sum(er_map * (gx ** 2 + gy ** 2)) * d * d


def field_solver(traces, grounds, d=0.005, mask=True, width=None, air=1.2):
    """traces: list of (x_left, x_right, volts); grounds: list of (x_left, x_right) coplanar grounds on L1.
    The L2 plane is the bottom edge (0 V). Returns (C, C_air) in F/m for the driven conductors' energy."""
    xs = [x for tr in traces for x in tr[:2]] + [x for g in grounds for x in g]
    x0 = min(xs) - 1.0 if width is None else -width / 2
    x1 = max(xs) + 1.0 if width is None else width / 2
    nx = int(round((x1 - x0) / d)) + 1
    ny = int(round((H + T + air) / d)) + 1
    xn = x0 + np.arange(nx) * d
    yn = np.arange(ny) * d
    jh, jt = int(round(H / d)), int(round((H + T) / d))
    V = np.full((ny, nx), np.nan)
    V[0, :] = 0.0                     # L2 plane
    cu = np.zeros((ny, nx), bool)
    for xl, xr, v in traces:
        sel = (xn >= xl - 1e-9) & (xn <= xr + 1e-9)
        V[jh:jt + 1, sel] = v; cu[jh:jt + 1, sel] = True
    for xl, xr in grounds:
        sel = (xn >= xl - 1e-9) & (xn <= xr + 1e-9)
        V[jh:jt + 1, sel] = 0.0; cu[jh:jt + 1, sel] = True
    ycell = (yn[:-1] + yn[1:]) / 2
    er_d = np.ones((ny - 1, nx - 1))
    er_d[ycell < H, :] = ER
    if mask:
        cu_cell = cu[:-1, :-1] & cu[1:, 1:]
        n_cu = max(1, int(round(MASK_CU / d)))
        near_cu = binary_dilation(cu_cell, iterations=n_cu) & ~cu_cell & (ycell[:, None] > H)
        lam = (ycell[:, None] > H) & (ycell[:, None] < H + MASK_LAM) & ~cu_cell
        er_d[near_cu | lam] = ER_MASK
    er_a = np.ones_like(er_d)
    w_d = _solve(V, er_d, d * 1e-3)
    w_a = _solve(V, er_a, d * 1e-3)
    return 2 * w_d * EPS0, 2 * w_a * EPS0


def z_single(w, g=None, gnd_w=1.5, **kw):
    """Single-ended line: CPWG if g is given (grounds gnd_w wide each side), else microstrip."""
    tr = [(-w / 2, w / 2, 1.0)]
    gr = [] if g is None else [(-w / 2 - g - gnd_w, -w / 2 - g), (w / 2 + g, w / 2 + g + gnd_w)]
    c, ca = field_solver(tr, gr, **kw)
    return 1 / (C0 * math.sqrt(c * ca)), c / ca       # (Z0, effective permittivity)


def z_diff(w, s, **kw):
    """Edge-coupled pair, odd mode: each trace's C from the total energy with +1/-1 V."""
    tr = [(-s / 2 - w, -s / 2, 1.0), (s / 2, s / 2 + w, -1.0)]
    c, ca = field_solver(tr, [], **kw)
    c1, ca1 = c / 2, ca / 2       # energy is shared by two lines at |V| = 1
    return 2 / (C0 * math.sqrt(c1 * ca1))


def main():
    print("JLC04161H-7628, L1 over L2: h 0.2104 mm, er 4.4, t 0.035 mm; mask 1.2/0.6 mil er 3.8\n")
    print("50 ohm grounded CPW (ANT_FEED, ANT_MAIN):")
    for g in (0.15, 0.20, 0.25):
        w = brentq(lambda x: cpwg_closed(x, g) - 50, 0.05, 2)
        zf, ee = z_single(w, g)
        w_f = brentq(lambda x: z_single(x, g)[0] - 50, 0.1, 1.0, xtol=0.002)
        print(f"  gap {g:.2f}: closed form w {w:.3f} mm (solver at that w: {zf:.1f} ohm); solver 50 ohm w {w_f:.3f} mm")
    w_ms = brentq(lambda x: microstrip_closed(x) - 50, 0.05, 2)
    print(f"  microstrip, no side ground: closed form w {w_ms:.3f} mm; solver {z_single(w_ms)[0]:.1f} ohm at that w\n")
    print("90 ohm edge-coupled pair (ESP_USB_DP/DN, USB_DP/DN):")
    for w in (0.20, 0.25, 0.30):
        try:
            s_c = f"{brentq(lambda s: diff_closed(w, s) - 90, 0.02, 2):.3f}"
        except ValueError:
            s_c = "none"
        try:
            s_f = f"{brentq(lambda s: z_diff(w, s) - 90, 0.05, 1.0, xtol=0.002):.3f}"
        except ValueError:
            s_f = "none in 0.05-1.0"
        print(f"  w {w:.2f}: closed form s {s_c} mm; solver s {s_f} mm")


if __name__ == "__main__":
    main()
