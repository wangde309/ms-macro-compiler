; ==========================================
; Example 1: Basic mouse movement and clicking (Mouse Test)
; ==========================================
MACRO "MouseClicker"
MODE count
COUNT 5

; Move diagonally down-right (x=100, y=100)
MOVE 100 100 0
SLEEP 100

Press the left mouse button, hold for 50 milliseconds, release, and then wait for 500 milliseconds.
MD L 50
MU L 500

Move up and to the left back to the original position (x=-100, y=-100).
MOVE -100 -100 0
SLEEP 1000
