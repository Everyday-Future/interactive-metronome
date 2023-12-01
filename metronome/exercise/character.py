class Skill:
    def __init__(self, name: str, level: float, difficulty_idx):
        self.name = name
        self.level = level
        self.difficulty_idx = difficulty_idx


class CharacterSkills:
    def __init__(self, interests=None, **kwargs):
        if interests is None:
            interests = ["singles", "doubles", "unison", "precision", "beats", "fills", "speed", "independence",
                         "patterns", "hand_independence",
                         "foot_independence", "paradiddles", "rev_paradiddles",
                         "flams_and_drags", "ghost_notes", "accents", "paradiddlediddles",
                         "rev_paradiddlediddles", "linear_drumming", "double_bass", "double_bass_independence",
                         "complexity",
                         "leading_lagging", "polyrhythms", "odd_time", "groupings", "half_and_double_time"]
        self.skill_names = interests
        self.skills = [kwargs.get(skill, Skill(name=skill, level=0.0, difficulty_idx=idx))
                       for idx, skill in enumerate(self.skill_names)]

    def get_weakest_skill(self):
        max_skill = 0.0
        for each_skill in self.skills:
            if each_skill.level <= max_skill:
                return each_skill
        return self.skills[0]


class Character:
    def __init__(self, interests: list = None):
        self.skills = CharacterSkills(interests=interests)
