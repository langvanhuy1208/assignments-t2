"""CLI dieu khien UR3: go 1 lenh la robot tu gap cube va tha vao zone.

ros2 run ur3_llm_control ur3_cli                  # che do go lenh lien tuc
ros2 run ur3_llm_control ur3_cli red c            # chay 1 lenh roi thoat
ros2 run ur3_llm_control ur3_cli --no-attach      # cube khong bam theo tool
"""
import re
import sys

import rclpy
from rclpy.utilities import remove_ros_args

from ur3_llm_control.skill_executor import SkillExecutor
from ur3_llm_control.student_config import (
    STUDENT_NAME,
    STUDENT_ID,
    ZONE_ASSIGNMENT,
)

COLORS = {
    "red": "red_cube", "r": "red_cube", "do": "red_cube",
    "yellow": "yellow_cube", "y": "yellow_cube", "vang": "yellow_cube",
    "blue": "blue_cube", "b": "blue_cube", "xanh": "blue_cube",
    "green": "green_cube", "g": "green_cube", "luc": "green_cube",
    "purple": "purple_cube", "p": "purple_cube", "tim": "purple_cube",
    "red_cube": "red_cube", "yellow_cube": "yellow_cube", "blue_cube": "blue_cube",
    "green_cube": "green_cube", "purple_cube": "purple_cube",
}
ZONES = {
    "a": "zone_a", "b": "zone_b", "c": "zone_c",
    "zone_a": "zone_a", "zone_b": "zone_b", "zone_c": "zone_c",
    "zonea": "zone_a", "zoneb": "zone_b", "zonec": "zone_c",
}
# Tu dem bo qua khi doc lenh
FILLER = {
    "move", "place", "put", "pick", "gap", "dat", "dua", "bo", "dem",
    "to", "in", "into", "on", "the", "cube", "zone", "vao", "sang", "khoi",
    "vat", "mau", "o", "vung", "and", "then", "please",
}

HELP = f"""
Chi can go: <mau> <zone>   -> robot tu gap cube roi tha vao zone, xong ve home
  red c                 gap cube do, tha vao zone C
  yellow a              gap cube vang, tha vao zone A
  blue b                gap cube xanh duong, tha vao zone B
  green a               gap cube xanh la, tha vao zone A
  purple c              gap cube tim, tha vao zone C
Cung duoc:  move red c | put the red cube in zone c | do c | vang a | xanh b
            xanh la a | tim c | g b | p a   (mau: red yellow blue green purple)

Lenh khac:
  arrange   xep 3 cube (do, vang, xanh duong) theo MSSV {STUDENT_ID}:
            {', '.join(f'{z[-1].upper()}={c.split("_")[0]}' for z, c in ZONE_ASSIGNMENT.items())}
  home      ve vi tri home
  status    xem cube nao dang o dau
  help      hien bang nay
  exit      thoat
"""


def tokenize(line):
    """Tach lenh; 'place(red_cube, zone_b)' cung duoc chap nhan."""
    line = line.lower()
    # mau hai tu trong tieng Viet -> gop thanh mot tu
    line = line.replace("xanh la", "green").replace("xanh duong", "blue")
    return [t for t in re.split(r"[\s(),]+", line.strip()) if t]


def build_plan(tokens):
    """Tra ve (plan | None, thong bao loi)."""
    if not tokens:
        return None, "empty"

    first = tokens[0].lower()
    if first == "home" and len(tokens) == 1:
        return {"plan": [{"skill": "home"}]}, None

    if first == "arrange" and len(tokens) == 1:
        steps = []
        for zone, obj in ZONE_ASSIGNMENT.items():
            steps.append({"skill": "pick", "object": obj})
            steps.append({"skill": "place", "object": obj, "zone": zone})
        steps.append({"skill": "home"})
        return {"plan": steps}, None

    words = [t.lower() for t in tokens if t.lower() not in FILLER]

    # xac dinh dau la mau, dau la zone (chu 'b' vua la blue vua la zone B)
    obj = zone = None
    if len(words) == 2:
        w1, w2 = words
        if w1 in COLORS and w2 in ZONES and not (w1 in ZONES and w1 not in COLORS):
            obj, zone = COLORS[w1], ZONES[w2]
        elif w2 in COLORS and w1 in ZONES:
            obj, zone = COLORS[w2], ZONES[w1]
    elif len(words) == 1 and words[0] in COLORS:
        return None, "Thieu zone. Vi du:  %s c" % words[0]

    if obj is None or zone is None:
        return None, "Lenh khong hop le. Vi du:  red c   (go 'help' de xem them)"

    return {"plan": [
        {"skill": "pick", "object": obj},
        {"skill": "place", "object": obj, "zone": zone},
        {"skill": "home"},
    ]}, None


def print_plan(plan):
    print("PLAN:")
    for s in plan["plan"]:
        if s["skill"] == "home":
            print("  home()")
        elif s["skill"] == "pick":
            print(f"  pick({s['object']})")
        else:
            print(f"  place({s['object']}, {s['zone']})")
    print("EXECUTION:")


def print_status(executor):
    sk = executor.skills
    print("TRANG THAI:")
    for obj in ("yellow_cube", "blue_cube", "red_cube"):
        if sk.held_object == obj:
            where = "dang cam tren tool"
        else:
            where = sk.cube_zone.get(obj, "vi tri ban dau tren ban")
        print(f"  {obj:12s}: {where}")


def run_command(executor, tokens):
    if tokens and tokens[0].lower() == "status":
        print_status(executor)
        return

    plan, err = build_plan(tokens)
    if plan is None:
        print(err)
        return

    # Neu dang cam san cube do (lan truoc dung giua chung) thi bo buoc pick
    held = executor.skills.held_object
    steps = plan["plan"]
    if held is not None and steps[0]["skill"] == "pick":
        if steps[0]["object"] == held:
            steps = steps[1:]
        else:
            print(f"Robot dang cam {held}. Hay xu ly cube nay truoc.")
            return
    plan = {"plan": steps}

    print_plan(plan)
    executor.execute_plan(plan)


def main(args=None):
    argv = remove_ros_args(sys.argv)[1:]
    attach = True
    if "--no-attach" in argv:
        attach = False
        argv.remove("--no-attach")

    rclpy.init(args=args)
    executor = SkillExecutor(attach_cubes=attach)

    print(f"UR3 CLI - {STUDENT_NAME} ({STUDENT_ID})")
    if not attach:
        print("[--no-attach] Cube se KHONG bam theo tool, chi robot di chuyen.")

    try:
        if argv:                       # chay mot lenh roi thoat
            run_command(executor, tokenize(" ".join(argv)))
        else:                          # che do tuong tac
            print(HELP)
            while True:
                try:
                    line = input("ur3> ").strip()
                except (EOFError, KeyboardInterrupt):
                    print()
                    break
                if not line:
                    continue
                if line.lower() in ("exit", "quit", "q"):
                    break
                if line.lower() == "help":
                    print(HELP)
                    continue
                run_command(executor, tokenize(line))
    finally:
        try:
            executor.destroy_node()
        except Exception:
            pass
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
