# ADR-002 (2026-10-22 revision): Real-time clock selection

Status: Accepted (concept revision — pending schematic and bench verification)
Date: 2026-10-22
Owner/reviewers: Auris hardware owner; engineering review pending
Supersedes: initial RV-3129-C3 Option A concept selection recorded 2026-07-28

## Context and measurable requirements

- The RTC lives on the always-on wake rail (`docs/04-HARDWARE-V1.md` §2): it must keep time, fire calendar-aligned wake alarms, and drive the level-held open-drain INT line into the power latch **while the switched 3.3 V core is off**.
- Two distinct wake tasks exist simultaneously: (a) a dynamic one-shot "next job at 03:42 UTC" alarm rewritten by the MCU each power-down, and (b) a standing wall-clock-aligned periodic wake (e.g. daily sync window) that must not require MCU re-anchoring.
- Device is solar-charged outdoors: −40 to +85 °C operation; absolute always-on current is a minor contributor (solar margin) rather than a design driver.
- Part must be procurable at LCSC in healthy stock for prototype and ~100-unit builds.

## Options considered with costs/risks

| Option | Stock (LCSC, 2026-10-22) | Wake capability | Notes / risks |
|---|---|---|---|
| **DS3231MZ+TRL** (SOIC-8, MEMS) | **11,498** in stock, $3.54 / $2.28@1k (`C107410`) | **Two time-of-day alarms** (A1 one-shot with seconds match; A2 masked-rate for standing UTC windows). A1F/A2F identify wake reason. | ±5 ppm, −40…+85 °C. `INTCN=1` required for alarm mode (POR default is 1; write explicitly anyway). Mature ecosystem (RTClib, Linux mainline driver, team familiarity with DS3231). |
| RV-3129-C3 Option A (previous selection) | 738 in stock, $3.34 / $2.88@1k (`C5366552`) | One calendar alarm + countdown timer. Timer is **relative** time: auto-reload drifts off UTC alignment and needs MCU re-anchoring; the single alarm cannot hold a one-shot and a standing window at once. | ±6 ppm, lower VBACKUP current (0.8 µA typ) and 1.3 V minimum — advantages irrelevant to a solar topology. Paged registers, no-repeated-START I²C, custom driver required. |
| DS3231SN#T&R (crystal, SOIC-16) | 912 in stock, $9.77 (`C9866`) | Same two-alarm model as DS3231MZ. | ±3.5 ppm accuracy, but ~2.7× the cost; accuracy gain unnecessary for a device that re-syncs time over LTE. |

## Decision and rationale

Select **DS3231MZ+TRL (`C107410`)** as the V1 RTC concept. The two independent alarm channels map directly onto the two required wake tasks (dynamic one-shot + standing UTC window) without firmware workarounds; the RV-3129 would force software to multiplex a single alarm. With solar charging, the RV-3129's lower backup current is not a differentiator, while the DS3231 family's maturity, second alarm, temperature rating and stock depth are concrete gains. RV-3129-C3 remains the recorded fallback for hypothetical future nanoamp-critical variants (e.g. coin-cell-only logger SKU) where its 0.8 µA timekeeping and 1.3 V VBACKUP floor would matter.

**Wake model on this part:** Alarm 1 = dynamic one-shot job alarm (MCU rewrites each power-down). Alarm 2 = standing periodic sync window (e.g. A2M2/A2M3 masked → minute+hour match, wall-clock aligned, never needs touching). Shared INT/SQW pin, active-low; A1F/A2F flags in the status register distinguish which task fired; flags cleared only after `PWR_HOLD` asserted (existing rule unchanged).

## Tests / supplier datasheet revisions

- DS3231M datasheet (Rev 3, 5/19), DS3231 datasheet (Rev 10, 3/15), Analog Devices.
- LCSC stock/price observations 2026-10-22; re-verify before prototype build (prices/stock are not frozen).
- **VBAT INT caveat (must bench-verify):** the datasheet states that when `BBSQW=0` and VCC falls below VPF, the INT/SQW pin **goes high-impedance** — i.e. alarm INT is *not specified* to assert while the part runs on VBAT with VCC dead. In the Auris topology the RTC's VCC comes from the always-on LDO (never switched off), so VBAT-only operation occurs only at total battery exhaustion (no energy left to record — moot). Nevertheless, verify on the bench: (a) alarm INT assertion with main 3.3 V off but always-on rail healthy, (b) INT/SQW pin state during battery brownout near VPF, (c) whether a 2.3–5.5 V always-on rail plus decoupled VBAT (0.1–1.0 µF, datasheet §Backup Power-Supply) satisfies both pins.
- Bench gate remains `G1 Power prototype` (`docs/12-TEST-AND-VALIDATION.md`): alarm INT across power states, wake timing, brownout, latch race tests — now covering A1/A2 individually and together.

## Consequences and rollback plan

- I²C address is **0x68** (7-bit); alone on the system bus since the MAX17048 was dropped (ADR-027); the PCM1863 (0x4A) has its own bus. Open-drain INT requires pull-up to the always-on rail.
- Configuration duties: `INTCN=1` (alarm mode) at every boot; `BBSQW=0`; verify INT/SQW never carries a square wave while the latch is armed.
- The `RST` pin includes a pushbutton debounce circuit (PBDB ≈ 250 ms) — candidate free debounce for the field service button; still requires its own wake-path test (do not assume).
- RTC backup rail decision (ADR-010, always-on LDO) unchanged: DS3231MZ VBAT range 2.3–5.5 V — confirm LDO output fits.
- Rollback: return to RV-3129-C3 Option A if bench testing exposes an unfixable INT-on-VBAT/latch incompatibility, or if DS3231MZ supply collapses; firmware abstraction should keep the RTC interface behind one driver module to make this swap cheap.