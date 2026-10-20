# MSC Macro Script Language Reference

Welcome to the MSC Macro Compiler. This document details the rules for writing `.ms` source files. All macro scripts you write will be compiled by `msc` into a hardware-compatible `[Init].txt` or `[Init].dat` format.

## 1. Basic Syntax Rules
- **Case-Insensitive**: All commands (e.g., `MOVE`, `move`, `Move`) are automatically recognized.
- **Comments**: Lines starting with a semicolon `;` are treated as comments and ignored during compilation.
- **Unit Conventions**:
  - Time unit is standardized as **milliseconds (ms)**.
  - Coordinate units are typically **pixels** or device-specific low-level counts.

---

## 2. Command Line Compilation

In the terminal, use the following format to compile your script:

    msc <source_file.ms> <target_file.txt/dat> [-O]

**Arguments:**
- `<source_file.ms>`: Path to your source code file (relative or absolute).
- `<target_file>`: Path to the compiled output file (e.g., `"[Init].txt"`). **Note: To prevent system damage, the program is forbidden from writing files to Windows protected directories (e.g., `C:\Windows`, `C:\Program Files`). Attempting to do so will result in an immediate error.**
- `-O` (Optional): Enables **Instruction Folding Optimization**. The compiler will automatically scan for adjacent, same-direction mouse movement commands and merge them into a single command, reducing the total action count and improving execution efficiency.

---

## 3. Global Configuration Commands

These commands are usually placed at the beginning of the source code to define the macro's overall properties.

### MACRO "MacroName"
Sets the name of the macro. The name must be enclosed in double quotes.

    MACRO "MyCombo"

### MODE <mode>
Sets the trigger mode of the macro.
- `count`: Count mode (default). Stops after executing the specified number of loops.
- `toggle`: Toggle mode. Press once to start looping, press again to stop.
- `hold`: Hold mode. Executes while the key is held down, stops when released.

    MODE toggle

### COUNT <number>
Used with `count` mode to set the number of loop iterations.

    COUNT 5

---

## 4. Mouse Operation Commands

### MOVE <X> <Y> [delay]
Moves the mouse.
- `X`: Horizontal displacement (positive for right, negative for left).
- `Y`: Vertical displacement (positive for down, negative for up).
- `[delay]` (Optional): Time to wait after moving.

> ** Note on Automatic Direction Recognition**:
> The compiler automatically determines the movement direction based on the positive/negative values of X and Y:
> - Bottom-Left (X<=0, Y<=0)
> - Top-Left (X<=0, Y>=0)
> - Bottom-Right (X>=0, Y<=0)
> - Top-Right (X>=0, Y>=0)

    ; Move right by 100, down by 50, with a 10ms delay
    MOVE 100 50 10

### MD <L/R/M> [delay] and MU <L/R/M> [delay]
Mouse Down and Mouse Up.
- `L`: Left Button
- `R`: Right Button
- `M`: Middle Button

    MD L 50     ; Press left button, hold for 50ms
    MU L 100    ; Release left button, wait for 100ms after release

---

## 5. Keyboard Operation Commands

### KD <key> [delay] and KU <key> [delay]
Key Down and Key Up.

> ** Note**: The current version only supports **single-character** keys (e.g., A-Z, 0-9, symbols). Multi-character names like `ENTER` or `SPACE` are not supported; please use the corresponding single character.

    KD A 50     ; Press key 'A', hold for 50ms
    KU A 100    ; Release key 'A', wait for 100ms after release

---

## 6. Syntactic Sugar & Flow Control

### TAP <target> [hold_time] [release_delay]
A one-step "Press + Release" combo operation.
- `<target>`: Can be a mouse button (`L`, `R`, `M`) or a single keyboard character (e.g., `A`).

    TAP L 50 100   ; Press left mouse button for 50ms, wait 100ms after release
    TAP A 20 50    ; Press key 'A' for 20ms, wait 50ms after release

### SLEEP <delay>
Pure delay wait, performs no actions.

    SLEEP 1000    ; Pause for 1000 milliseconds (1 second)

### RPT <count> { ... }
**Loop Block Command**. Repeats the code inside the curly braces `{}` a specified number of times. This is designed to significantly reduce code duplication (it is expanded into low-level instructions during compilation).

    RPT 3 {
        TAP A 20 30
        SLEEP 100
    }
    ; The above code is equivalent to executing the key press inside the braces 3 times consecutively.

---

## 7. Complete Example

Below is a typical "Recoil Control + Rapid Fire" mouse macro example:

    ; --- Basic Settings ---
    MACRO "macro"
    MODE hold
    COUNT 1

    ; --- Main Loop ---
    SLEEP 100

    RPT 5 {
        MD L 10
        MU L 20
        MOVE 2 8 15
    }

**Compile and optimize this file:**

    msc macros.ms "[Init].txt" -O
