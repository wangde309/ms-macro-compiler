# ms-macro-compiler
A command-line compiler that converts .ms macro scripts into hardware configuration

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Active-success)

> This is a reverse engineering project targeting the configuration file of a specific mouse macro driver. Through static analysis of the underlying assembly code, we have completely reconstructed the serialization protocol of its configuration files and developed a minimalist domain-specific language called **MacroScript**, which is entirely independent of GUIs and generates low-level macro data purely through code.

## Core Features

    - **Detach from the GUI interface**:No need to open a complex interface; pure code can generate valid macro files.
    - **Self-created grammar**:Say goodbye to tedious 8-byte hexadecimal concatenation and write macros using pseudo-code.
    - **Full support for mouse and keyboard**:Supports left/right/middle mouse button clicks, full keyboard key positions, pure latency, and X/Y axis trajectory movement.
    - **Transparent underlying protocols**:The complete data structure diagram obtained through reverse analysis has been made public.

### Protocol Reverse
| Byte Position | Offset | Parameter Meaning | based on actual data |
| :--- | :--- | :--- | :--- |
| **Byte 0** | `0x00` | Action Type | `1`=Press, `2`=Release, `3`=Mouse Move, `0`=Pure Delay |
| **Byte 1** | `0x01` | Key Code | Keyboard ASCII code (e.g., `A`=65);Mouse: `240` = left button, `241` = right button, `242` = middle button |
| ** Bytes 2-3** | `0x02` | X-axis coordinate | 16-bit integer, with the low 8 bits first and the high 8 bits after |
| ** Bytes 4-5** | `0x04` | Y-axis coordinate | 16-bit integer, low 8 bits first, high 8 bits after |
| ** Bytes 6-7** | `0x06` | Delay | 16-bit integer in milliseconds, low byte first, high byte second |

### File Structure (INI Format)
- ** Header Name: Located at the beginning of the file, encoded in UTF-16-LE, occupying 60 bytes.
- ** Action Sequence: A total of 275 action slots; any remaining slots should be filled with `000`.
- ** Tail Configuration**: Includes features such as LED and DPI, fixed at 340 bytes.

## Self-created language: MacroScript

For human readability, we have developed the `.ms` script syntax. The compiler will automatically convert it into 275 action points.

## 📜MacroASM Syntax Manual

The `.mas` file adopts a minimalist assembly-style format, is case-insensitive, and supports `; Single-line comment.

### 1. Macros and Attributes
| Instruction  | Parameter | Example | Dxplaination |
| :--- | :---  | :--- | :--- |
| ** `MACRO`** | `"Macro Name"` | `MACRO "AK"` | Initiates a new macro block, with the name supporting Chinese characters (maximum 30 characters). |
| **`MODE`**   | `0` or `1` | `MODE 1` | `0` = Trigger cycle (default); `1` = Press and hold until released (toggle mode). |

### 2. Mouse and Keyboard Actions
| Instruction | Parameter | Example | Dxplaination |
| :--- | :--- | :--- | :--- |
| **`MD`** | `L` / `R` / `M` | `MD L` | Mouse button press (Mouse Down), where L=left button, R=right button, M=middle button. |
| ** `MU`** | `L` / `R` / `M` | `MU L` | Mouse Up. |
| ** `KD`** | `Character` | `KD A` | Key Down, such as `KD 1`, `KD A`. |
| ** `KU`** | `Character` | `KU A` | Key Up. |
| ** `MOVE`**| `X Y Delay` | `MOVE 0 2 15` | Mouse movement. X/Y represent the relative displacement coordinates, with the delay unit in milliseconds (ms). |
| ** `SLEEP` | `milliseconds` | `SLEEP 500` | A pure delay command, pausing for the specified milliseconds. |

### 3. Control Flow (Loops)
| Instruction | Parameter | Example | Dxplaination |
| :--- | :--- | :--- | :--- |
| **`RPT`** | `Number of occurrences { ... }` | `RPT 10 { ... }`
