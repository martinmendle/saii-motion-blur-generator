# Credits and Third-Party Software

The original code in this repository is licensed under the MIT License (see [`LICENSE`](./LICENSE)),
**except** as noted in this document. The third-party components listed below retain their own
rights and terms, and are **not** covered by this repository's MIT License.

---

## 1. CNC Shield Stepper Control Demo (Superb Tech)

| Field | Details |
|---|---|
| **Author** | Superb Tech |
| **Source** | https://www.youtube.com/superbtech |
| **Used in** | `Movement.ino` (basic STEP/DIR pulse control for the stepper motors) |
| **Declared license** | None |

**What is third-party and what is original:**
- Third-party base: pin configuration and pulse-based movement functions for the CNC Shield.
- Original contributions (MIT): photo grid logic, serpentine movement pattern, position
  counters, serial communication with the acquisition script, and return-to-origin routine.

> Because no license is declared, the author's original code remains under all rights
> reserved. The original modifications are under MIT; the base code is not.

---

## 2. Spinnaker SDK / PySpin (FLIR / Teledyne)

| Field | Details |
|---|---|
| **Rights holder** | FLIR Systems, Inc. / Teledyne FLIR |
| **Source** | https://www.teledynevisionsolutions.com/ (Spinnaker SDK downloads section) |
| **Used in** | `Acquisition.py` (camera control via the PySpin API) |
| **License** | FLIR proprietary license agreement, bundled with the SDK |
| **Redistributed in this repo** | **No.** The SDK and its examples are not included. |

To use this project, you must download and install the Spinnaker SDK (including the PySpin
Python package) yourself, accepting its license. This repository does not include or
redistribute code from the SDK's example programs.

---

## 3. Python dependencies

Installed separately; each retains its own license.

| Package | Use | License |
|---|---|---|
| [pySerial](https://github.com/pyserial/pyserial) | Serial communication with the Arduino | BSD-3-Clause |

---

## Reporting an attribution issue

If you are the rights holder of any code included here and would like the attribution
corrected or the code removed, please open an issue in this repository or contact: martin.mendlewicz@fing.edu.uy.
