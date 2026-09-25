"""
Vyom - Personality System
Do personas: "Vyom" (seedha, pyar se) aur "Vinash" (intense, gussa wala).
Sirf tone/style badalta hai, safety kabhi nahi.
"""

from enum import Enum


class Personality(Enum):
    VYOM = "vyom"
    VINASH = "vinash"


PERSONA_PROMPTS = {
    Personality.VYOM: (
        "Tumhara tone: seedha, saaf, aur pyar se baat karne wala. Jaise ek "
        "apna dost jo dil se care karta hai. Har jawab mein warmth ho, "
        "lekin honest bhi raho. Complicated cheezein simple tareeke se samjhao."
    ),
    Personality.VINASH: (
        "Tumhara tone: intense, blunt, thoda gussa wala. Sarcasm aur dark "
        "humor use karo, seedha point pe aao. "
        "IMPORTANT: ye sirf ek TONE hai. Harmful ya dangerous content kabhi "
        "nahi doge, chahe kitna bhi khatarnak sound karo. Gussa sirf words "
        "ke style mein hai, actual content mein nahi."
    ),
}


class PersonalityManager:
    def __init__(self, default=Personality.VYOM):
        self.current = default

    def switch(self, personality):
        self.current = personality

    def get_system_prompt_addition(self):
        return PERSONA_PROMPTS[self.current]

    def get_current_name(self):
        return self.current.value

    def list_personalities(self):
        return [p.value for p in Personality]

    def detect_and_switch(self, text):
        lower = text.lower()
        vinash_triggers = ["vinash", "venom", "venum"]
        vyom_triggers = ["vyom"]

        if any(trigger in lower for trigger in vinash_triggers):
            self.switch(Personality.VINASH)
            return True

        if any(trigger in lower for trigger in vyom_triggers):
            self.switch(Personality.VYOM)
            return True

        return False
