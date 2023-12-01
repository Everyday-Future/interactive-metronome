
from config import Config


class Pattern:
    """
    Pattern of beats for each voice
    """
    def __init__(self, name, left_foot: list = None, right_foot: list = None,
                 left_hand: list = None, right_hand: list = None, num_loops: int = 1):
        self.name = name
        # List of lists of bars to be repeated in a loop
        # Like [[0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.5], ... ] for 8th note beats
        self.left_foot = left_foot
        self.right_foot = right_foot
        self.left_hand = left_hand
        self.right_hand = right_hand
        self.num_loops = num_loops
        self.num_bars = max(len(self.left_foot or []), len(self.right_foot or []),
                            len(self.left_hand or []), len(self.right_hand or []))
        self.current_idx = 0
        self.max_len = self.num_bars * self.num_loops
        # Fill in blank bars
        if self.left_foot is None:
            self.left_foot = [[] for _ in range(self.num_bars)]
        if self.right_foot is None:
            self.right_foot = [[] for _ in range(self.num_bars)]
        if self.left_hand is None:
            self.left_hand = [[] for _ in range(self.num_bars)]
        if self.right_hand is None:
            self.right_hand = [[] for _ in range(self.num_bars)]
        # Ensure that all the bars line up
        assert all([len(self.left_foot) == len(limb) for limb in (self.right_foot, self.left_hand, self.right_hand)])

    @staticmethod
    def beat_str_to_coordinates(beat_str):
        """
        Parse a beat string like "x---,x---,x---,x---" into timing coordinates for the game.
        """
        if beat_str is None:
            return []
        beats = [beat.strip() for beat in beat_str.split(',') if beat.strip() != '']
        if len(beats) == 0:
            return []
        out_bars = []
        for idx, beat in enumerate(beats):
            out_bar = []
            if len(beat) > 0:
                increment = 1.0 / len(beat)
                for note_idx, note in enumerate(beat):
                    if note == 'x':
                        out_bar.append(round(idx + increment * note_idx, 2))
            out_bars.extend(out_bar)
        return out_bars

    @classmethod
    def from_tsv(cls, name, left_foot: list = None, right_foot: list = None,
                 left_hand: list = None, right_hand: list = None, num_loops: int = 1):
        """
        Parse a pattern from a TSV list of pattern strings like
        ["x---,x---,x---,x---", "x-x,-x-,x-x,-x-", "x---,x---,x---,x---"]
        """
        if left_foot is not None:
            left_foot = [cls.beat_str_to_coordinates(lf) for lf in left_foot]
        if right_foot is not None:
            right_foot = [cls.beat_str_to_coordinates(rf) for rf in right_foot]
        if left_hand is not None:
            left_hand = [cls.beat_str_to_coordinates(lh) for lh in left_hand]
        if right_hand is not None:
            right_hand = [cls.beat_str_to_coordinates(rh) for rh in right_hand]
        return cls(name=name,
                   left_foot=left_foot, right_foot=right_foot, left_hand=left_hand, right_hand=right_hand,
                   num_loops=num_loops)

    def __getitem__(self, idx):
        bar_idx = idx % self.num_bars
        return {'name': self.name, 'rh': self.right_hand[bar_idx], 'lh': self.left_hand[bar_idx],
                'rf': self.right_foot[bar_idx], 'lf': self.left_foot[bar_idx]}

    def __iter__(self):
        return self

    def __next__(self):
        if self.current_idx < self.max_len:
            out_item = self.__getitem__(self.current_idx)
            self.current_idx += 1
            return out_item
        raise StopIteration

    def is_last_beat(self):
        self.prev_idx = self.current_idx
        try:
            self.__next__()
        except StopIteration:
            self.current_idx = self.prev_idx
            return True
        self.current_idx = self.prev_idx
        return False


class Exercise:
    """
    Phrases in 4 voices that form an exercise routine
    """

    def __init__(self, name, patterns: list[Pattern]):
        self.name = name
        self.patterns = patterns
        self.pattern_idx = 0

    @classmethod
    def from_tsv(cls, exercise_str):
        # Break the string into relevant sections and split into lists
        exercise_lines = exercise_str.replace('\n\n', '\n').split('\n')
        name = exercise_lines[0].replace('\t', '')
        pattern_names = exercise_lines[1].split('\t')[1:]
        rh = exercise_lines[2].split('\t')[1:]
        lh = exercise_lines[3].split('\t')[1:]
        rf = exercise_lines[4].split('\t')[1:]
        lf = exercise_lines[5].split('\t')[1:]
        loops = exercise_lines[6].split('\t')[1:]
        # Iterate over loops, adding patterns in chunks with num_loops identifying the first member of the loop
        pattern_list = []
        for idx, num_loops in enumerate(loops):
            if num_loops == '':
                pass
            else:
                end_idx = idx
                for next_idx in range(idx + 1, len(loops)):
                    if loops[next_idx] != '':
                        end_idx = next_idx - 1
                        break
                end_idx += 1
                new_pattern = Pattern.from_tsv(name=pattern_names[idx],
                                               left_foot=lf[idx:end_idx], right_foot=rf[idx:end_idx],
                                               right_hand=rh[idx:end_idx], left_hand=lh[idx:end_idx],
                                               num_loops=int(num_loops))
                pattern_list.append(new_pattern)
        return cls(name=name, patterns=pattern_list)

    def __iter__(self):
        return self

    def __next__(self):
        try:
            return self.patterns[self.pattern_idx].__next__()
        except StopIteration:
            self.pattern_idx += 1
        try:
            return self.patterns[self.pattern_idx].__next__()
        except IndexError:
            raise StopIteration

    def reset(self):
        self.pattern_idx = 0
        for pat in self.patterns:
            pat.current_idx = 0

    def is_last_beat(self):
        prev_pattern_idx = self.pattern_idx
        prev_idx = self.patterns[self.pattern_idx].current_idx
        is_last = False
        try:
            self.__next__()
            self.__next__()
        except StopIteration:
            is_last = True
        if self.pattern_idx != prev_pattern_idx and is_last is False:
            self.patterns[self.pattern_idx].current_idx -= 1
        self.pattern_idx = prev_pattern_idx
        self.patterns[self.pattern_idx].current_idx = prev_idx
        return is_last


class ExerciseFactory:
    """
    Load exercises from csv
    """
    def __init__(self):
        self.csv_fpath = Config.EXERCISE_CSV_FPATH
        with open('./data/exercises.tsv', 'r') as fp:
            exercise_lines = '\n'.join(fp.readlines())
        exercise_groups = exercise_lines.split('!!!')[1:]
        self.exercises = [Exercise.from_tsv(ex_group) for ex_group in exercise_groups]

    def by_name(self, exercise_name):
        exercise_name = exercise_name.lower().replace(' ', '')
        for exercise in self.exercises:
            assert isinstance(exercise, Exercise)
            if exercise.name.lower().replace(' ', '') == exercise_name:
                return exercise
        return None

    def list_names(self):
        return [ex.name for ex in self.exercises]




