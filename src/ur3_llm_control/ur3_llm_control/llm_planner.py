import json
import re

from ur3_llm_control.student_config import OBJECT_ALIASES, ZONE_ALIASES, OBJECT_TO_ZONE


class LLMPlanner:
    def __init__(self):
        self.object_aliases = OBJECT_ALIASES
        self.zone_aliases = ZONE_ALIASES

    def _match_object(self, text):
        lower = text.lower()
        for alias, value in sorted(self.object_aliases.items(), key=lambda kv: len(kv[0]), reverse=True):
            if alias in lower:
                return value
        return None

    def _match_zone(self, text):
        lower = text.lower()
        for alias, value in sorted(self.zone_aliases.items(), key=lambda kv: len(kv[0]), reverse=True):
            if alias in lower:
                return value
        return None

    def _make_plan_from_object_and_zone(self, obj, zone):
        return {
            "plan": [
                {"skill": "pick", "object": obj},
                {"skill": "place", "object": obj, "zone": zone},
                {"skill": "home"},
            ]
        }

    def plan_from_text(self, text):
        if not isinstance(text, str):
            raise ValueError("Text must be a string")

        lower = text.lower()
        obj = self._match_object(text)
        zone = self._match_zone(text)

        # Basic command: "Put the red cube in zone B"
        if obj and zone:
            return self._make_plan_from_object_and_zone(obj, zone)

        # Advanced command: arrange according to student plan
        if "arrange" in lower or "student id" in lower or "student_id" in lower or "my student" in lower:
            plan = []
            for obj_name, target_zone in OBJECT_TO_ZONE.items():
                plan.extend([
                    {"skill": "pick", "object": obj_name},
                    {"skill": "place", "object": obj_name, "zone": target_zone},
                ])
            plan.append({"skill": "home"})
            return {"plan": plan}

        # Fallback default: if only object known, move it to assigned zone
        if obj:
            target_zone = OBJECT_TO_ZONE.get(obj, "zone_a")
            return self._make_plan_from_object_and_zone(obj, target_zone)

        # Hard fail safe
        return {"plan": [{"skill": "home"}]}

    def plan_from_json_text(self, text):
        try:
            loaded = json.loads(text)
            if isinstance(loaded, dict) and "plan" in loaded:
                return loaded
        except Exception:
            pass
        return self.plan_from_text(text)
