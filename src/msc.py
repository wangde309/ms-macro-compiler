import os
import sys
import argparse


# ================= Low-level protocol tools =================
def f3(val):
    """Force conversion to a 3-digit string (e.g., 5 -> '005', 255 -> '255')"""
    return f"{max(0, int(val)):03d}"


# ================= Windows Protected Directory Detection =================
def _norm(p):
    return os.path.normcase(os.path.normpath(os.path.abspath(p)))


def get_protected_dirs():
    """Return the Windows protected directory set (normalized absolute paths)"""
    dirs = set()
    for env in ("SystemRoot", "ProgramFiles", "ProgramFiles(x86)", "ProgramData"):
        p = os.environ.get(env)
        if p:
            dirs.add(_norm(p))
    sysdrive = os.environ.get("SystemDrive", "C:")
    dirs.add(_norm(sysdrive + os.sep))
    return dirs


def is_protected_path(path):
    """Determine whether an absolute path is located within a Windows-protected directory."""
    path = _norm(path)
    for d in get_protected_dirs():
        if path == d:
            return True
        if path.startswith(d + os.sep):
            return True
    return False


# ================= Core Parser =================
def parse_ms(ms_text):
    actions = []
    macro_name = "Test"
    mode = 0     # 0=Count, 1=Switch, 2=Hold
    loop_n = 1

    lines = ms_text.strip().split('\n')
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line or line.startswith(';'):
            i += 1
            continue

        parts = line.split()
        cmd = parts[0].upper()

        if cmd == 'MACRO':
            macro_name = line.split('"')[1]
        elif cmd == 'MODE':
            if parts[1].lower() == 'hold':
                mode = 2
            elif parts[1].lower() == 'switch':
                mode = 1
            elif parts[1].lower() == 'cycle':
                mode = 0
        elif cmd == 'COUNT':
            loop_n = int(parts[1])

        elif cmd == 'MD':
            btn = {"L": 240, "R": 241, "M": 242}.get(parts[1].upper(), 240)
            delay = int(parts[2]) if len(parts) > 2 else 0
            actions.append([1, btn, 0, 0, 0, 0, delay & 0xFF, (delay >> 8) & 0xFF])
        elif cmd == 'MU':
            btn = {"L": 240, "R": 241, "M": 242}.get(parts[1].upper(), 240)
            delay = int(parts[2]) if len(parts) > 2 else 0
            actions.append([2, btn, 0, 0, 0, 0, delay & 0xFF, (delay >> 8) & 0xFF])

        elif cmd == 'KD':
            key = ord(parts[1].upper()[0])
            delay = int(parts[2]) if len(parts) > 2 else 0
            actions.append([1, key, 0, 0, 0, 0, delay & 0xFF, (delay >> 8) & 0xFF])
        elif cmd == 'KU':
            key = ord(parts[1].upper()[0])
            delay = int(parts[2]) if len(parts) > 2 else 0
            actions.append([2, key, 0, 0, 0, 0, delay & 0xFF, (delay >> 8) & 0xFF])

        elif cmd == 'TAP':
            target = parts[1].upper()
            hold = int(parts[2]) if len(parts) > 2 else 0
            wait = int(parts[3]) if len(parts) > 3 else 0
            if target in ["L", "R", "M"]:
                btn = {"L": 240, "R": 241, "M": 242}[target]
                actions.append([1, btn, 0, 0, 0, 0, hold & 0xFF, (hold >> 8) & 0xFF])
                actions.append([2, btn, 0, 0, 0, 0, wait & 0xFF, (wait >> 8) & 0xFF])
            else:
                key = ord(target[0])
                actions.append([1, key, 0, 0, 0, 0, hold & 0xFF, (hold >> 8) & 0xFF])
                actions.append([2, key, 0, 0, 0, 0, wait & 0xFF, (wait >> 8) & 0xFF])

        elif cmd == 'SLEEP':
            d = int(parts[1])
            actions.append([0, 0, 0, 0, 0, 0, d & 0xFF, (d >> 8) & 0xFF])

        elif cmd == 'MOVE':
            x = int(parts[1])
            y = int(parts[2])
            d = int(parts[3]) if len(parts) > 3 else 0

            if x <= 0 and y <= 0:
                move_type = 3
            elif x <= 0 and y >= 0:
                move_type = 4
            elif x >= 0 and y <= 0:
                move_type = 5
            else:
                move_type = 6

            abs_x = abs(x)
            abs_y = abs(y)

            actions.append([
                move_type, 246,
                abs_x & 0xFF, (abs_x >> 8) & 0xFF,
                abs_y & 0xFF, (abs_y >> 8) & 0xFF,
                d & 0xFF, (d >> 8) & 0xFF
            ])

        elif cmd == 'RPT':
            count = int(parts[1])
            if '{' in line:
                block_lines = []
                j = i + 1
                while j < len(lines) and lines[j].strip() != '}':
                    block_lines.append(lines[j])
                    j += 1
                sub_actions, _, _, _ = parse_ms("\n".join(block_lines))
                actions.extend(sub_actions * count)
                i = j

        i += 1

    return actions, macro_name, mode, loop_n


# ================= Core compilation logic =================
def compile_macro(ms_content, optimize=False):
    actions, macro_name, mode, loop_n = parse_ms(ms_content)
    act_count = len(actions)

    # Optional Optimization: Adjacent Same-Direction Moving Folding
    if optimize:
        optimized = []
        if actions:
            optimized.append(actions[0])
            for current in actions[1:]:
                prev = optimized[-1]
                if (
                    current[0] in [3, 4, 5, 6]
                    and prev[0] in [3, 4, 5, 6]
                    and current[0] == prev[0]
                ):
                    prev_d = prev[6] + (prev[7] << 8)
                    curr_d = current[6] + (current[7] << 8)
                    if prev_d + curr_d <= 999:
                        prev_x = prev[2] + (prev[3] << 8) + current[2] + (current[3] << 8)
                        prev_y = prev[4] + (prev[5] << 8) + current[4] + (current[5] << 8)
                        prev[2], prev[3] = prev_x & 0xFF, (prev_x >> 8) & 0xFF
                        prev[4], prev[5] = prev_y & 0xFF, (prev_y >> 8) & 0xFF
                        prev[6], prev[7] = (prev_d + curr_d) & 0xFF, ((prev_d + curr_d) >> 8) & 0xFF
                        continue
                optimized.append(current)
        actions = optimized
        act_count = len(actions)

    # Complete 275 actions
    while len(actions) < 275:
        actions.append([0] * 8)

    # 1. Name Section (60 bytes)
    n = macro_name.encode('utf-16-le')
    n = n + b'\x00' * (60 - len(n)) if len(n) < 60 else n[:60]
    n_str = "".join([f3(b) for b in n])

    # 2. Parameter Header (21 bytes)
    p_str = (
        f3(0) + f3(1) + f3(0) + f3(act_count)
        + f3(0) * 11
        + f3(loop_n) + f3(mode)
        + f3(0) * 4
    )

    # 3. Action Area
    a_str = "".join([f3(b) for a in actions for b in a])

    # 4. Tail: 340 bytes
    t_str = f3(0) * 340

    data = (
        f"[Init]\r\n"
        f"DAT_VER=3\r\n"
        f"[Macros]\r\n"
        f"macroNum=1\r\n"
        f"0={n_str}{p_str}{a_str}{t_str}\r\n"
    )
    return data, act_count, macro_name, mode, loop_n


# ================= Command-line interface =================
def main():
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

    parser = argparse.ArgumentParser(
        prog="msc",
        description="MS Macro Compiler: Compiles .ms source code into [Init].txt"
    )
    # 增加 --version 支持
    parser.add_argument(
        "-v", "--version", 
        action="version", 
        version="msc 26.1.0.1"
    )
    
    parser.add_argument("source", help="MS source code file (relative or absolute path)")
    parser.add_argument("target", help="Target file (relative or absolute path)")
    parser.add_argument("-O", "--optimize", action="store_true", help="Enable instruction folding optimization.")
    args = parser.parse_args()

    source_path = os.path.abspath(args.source)
    target_path = os.path.abspath(args.target)

    # 1. Source File Inspection
    if not os.path.exists(source_path):
        print(f"[ERROR] Source file does not exist: {source_path}")
        sys.exit(1)
    if not os.path.isfile(source_path):
        print(f"[ERROR] Source path is not a file.: {source_path}")
        sys.exit(1)

    # 2. Target Path Protection Check (Resolved Absolute Path)
    if is_protected_path(target_path):
        print(f"[ERROR] The target path is located in a Windows-protected directory; write access is denied.: {target_path}")
        sys.exit(1)

    # 3. Target Parent Directory Check
    target_dir = os.path.dirname(target_path)
    if target_dir and not os.path.isdir(target_dir):
        print(f"[ERROR] The target directory does not exist.: {target_dir}")
        sys.exit(1)

    # 4. The target and source cannot be the same file.
    if _norm(source_path) == _norm(target_path):
        print(f"[ERROR] The target file cannot be the same as the source file.: {target_path}")
        sys.exit(1)

    # 5. Read the source file
    try:
        with open(source_path, "r", encoding="utf-8") as f:
            ms_content = f.read()
    except Exception as e:
        print(f"[ERROR] Failed to read the source file.: {e}")
        sys.exit(1)

    # 6. Compilation
    try:
        data, act_count, macro_name, mode, loop_n = compile_macro(
            ms_content, optimize=args.optimize
        )
    except Exception as e:
        print(f"[ERROR] Compilation failed: {e}")
        sys.exit(1)

    opt_tag = "ON" if args.optimize else "OFF"
    print(
        f"[INFO] Macro Name [{macro_name}] Action Count [{act_count}]  "
        f"Mode [{mode}] Loop [{loop_n}] Optimization [{opt_tag}]"
    )

    # 7. Write Target
    try:
        with open(target_path, "w", encoding="utf-8", newline='') as f:
            f.write(data)
    except PermissionError as e:
        print(f"[ERROR] Insufficient permissions to write to the target file.: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Failed to write to the target file.: {e}")
        sys.exit(1)

    print(f"Compilation successful: {target_path}")


if __name__ == "__main__":
    main()