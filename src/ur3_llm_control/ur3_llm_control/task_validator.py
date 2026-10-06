from ur3_llm_control.student_config import ALLOWED_OBJECTS, ALLOWED_SKILLS, ALLOWED_ZONES


class TaskValidator:
    def validate(self, plan):
        if not isinstance(plan, dict):
            return False, "Plan must be a JSON object"

        if "plan" not in plan or not isinstance(plan["plan"], list):
            return False, "Missing valid 'plan' list"

        for step in plan["plan"]:
            if not isinstance(step, dict):
                return False, "Each plan step must be an object"

            skill = step.get("skill")
            if skill not in ALLOWED_SKILLS:
                return False, f"Invalid skill: {skill}"

            if skill == "pick":
                obj = step.get("object")
                if obj not in ALLOWED_OBJECTS:
                    return False, f"Invalid object for pick: {obj}"

            if skill == "place":
                obj = step.get("object")
                zone = step.get("zone")
                if obj not in ALLOWED_OBJECTS:
                    return False, f"Invalid object for place: {obj}"
                if zone not in ALLOWED_ZONES:
                    return False, f"Invalid zone for place: {zone}"

        return True, "VALID"
