STUDENT_NAME = "Lang Van Huy"
STUDENT_ID = "23020745"

# MSSV 23020745 -> 45 mod 6 = 3
# P = 3 -> A = Yellow, B = Blue, C = Red
ZONE_ASSIGNMENT = {
    "zone_a": "yellow_cube",
    "zone_b": "blue_cube",
    "zone_c": "red_cube",
}

OBJECT_TO_ZONE = {
    "yellow_cube": "zone_a",
    "blue_cube": "zone_b",
    "red_cube": "zone_c",
}

ALLOWED_OBJECTS = ["red_cube", "yellow_cube", "blue_cube", "green_cube", "purple_cube"]
ALLOWED_ZONES = ["zone_a", "zone_b", "zone_c"]
ALLOWED_SKILLS = ["home", "pick", "place"]

OBJECT_ALIASES = {
    "blue": "blue_cube",
    "blue cube": "blue_cube",
    "blue_cube": "blue_cube",
    "yellow": "yellow_cube",
    "yellow cube": "yellow_cube",
    "yellow_cube": "yellow_cube",
    "red": "red_cube",
    "red cube": "red_cube",
    "red_cube": "red_cube",
    "green": "green_cube",
    "green cube": "green_cube",
    "green_cube": "green_cube",
    "purple": "purple_cube",
    "purple cube": "purple_cube",
    "purple_cube": "purple_cube",
    # tieng Viet
    "do": "red_cube",
    "vang": "yellow_cube",
    "xanh duong": "blue_cube",
    "xanh": "blue_cube",
    "xanh la": "green_cube",
    "luc": "green_cube",
    "tim": "purple_cube",
}

ZONE_ALIASES = {
    "zone a": "zone_a",
    "zone_a": "zone_a",
    "a": "zone_a",
    "zone b": "zone_b",
    "zone_b": "zone_b",
    "b": "zone_b",
    "zone c": "zone_c",
    "zone_c": "zone_c",
    "c": "zone_c",
}
