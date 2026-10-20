; ==========================================
; Example 2: Advanced Keyboard Combo and Looping (Keyboard Combo)
; ==========================================
MACRO "ComboMaster"
MODE toggle
COUNT 1

Press and release the A key (hold for 50ms, then wait 100ms after releasing).
TAP A 50 100

Press the B key, hold it for 200 ms, release it, and then wait for 100 ms.
KD B 200
KU B 100

Use the RPT loop block and press the C key three times in succession.
Each press is held for 20 milliseconds, and after releasing, it waits for 30 milliseconds.
RPT 3 {
    TAP C 20 30
}

Finally, press the space key (or any letter key).
TAP D 50 100