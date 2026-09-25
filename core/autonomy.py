"""
Vyom - Autonomy Levels
Level 0: Only answers
Level 1: Suggests
Level 2: Action after approval
Level 3: Pre-approved routines
Level 4: Limited autonomous workflows
Level 5: High-risk always needs confirmation
"""

from enum import IntEnum


class AutonomyLevel(IntEnum):
    ANSWER_ONLY = 0
    SUGGEST = 1
    APPROVE_THEN_ACT = 2
    PRE_APPROVED_ROUTINE = 3
    LIMITED_AUTONOMOUS = 4
    ALWAYS_CONFIRM_HIGH_RISK = 5


class AutonomyManager:
    def __init__(self, default_level=AutonomyLevel.APPROVE_THEN_ACT):
        self.default_level = default_level
        self.pre_approved_routines = {}

    def approve_routine(self, routine_name):
        self.pre_approved_routines[routine_name] = True

    def revoke_routine(self, routine_name):
        self.pre_approved_routines.pop(routine_name, None)

    def should_ask_confirmation(self, action_name, risk_is_high, level=None):
        level = level or self.default_level

        if risk_is_high:
            return True

        if level == AutonomyLevel.ANSWER_ONLY:
            return True
        if level == AutonomyLevel.SUGGEST:
            return True
        if level == AutonomyLevel.APPROVE_THEN_ACT:
            return True
        if level == AutonomyLevel.PRE_APPROVED_ROUTINE:
            return not self.pre_approved_routines.get(action_name, False)
        if level == AutonomyLevel.LIMITED_AUTONOMOUS:
            return False
        return True
