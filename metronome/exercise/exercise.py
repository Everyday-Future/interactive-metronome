
import math
from typing import List
from enum import Enum


class Note(Enum):
    WHOLE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    HALF = 0.5
    QUARTER = 0.25
    QUARTER_TRIPLET = 1.0 / 3.0
    SIXTEENTH = 0.125
    SIXTEENTH_TRIPLET = 1.0 / 6.0
    THIRTY_SECOND = 0.125
    EMPTY = 0.0


class BarPattern:
    """
    Pattern of notes in a bar

    Should be a list of indexes for beats like [0.5, 1.0, 1.3333, 1.66666, 2.0] etc...
    Where the whole number is the beat location and the decimal is the distribution within the beat.
    """

    def __init__(self, pattern: list, num_loops: int = 1):
        self.pattern = pattern
        self.num_loops = num_loops

    @classmethod
    def from_recipe(cls, increment: Note, offset: float, num_beats: int, num_loops: int = 1):
        """
        Build a bar of beats from an increment, offset, and bar length
        """
        offset_value = increment.value * offset
        if increment == Note.EMPTY:
            return cls(pattern=[], num_loops=num_loops)
        note_count = math.ceil((num_beats - offset_value) / increment.value)
        if note_count <= 0:
            raise ValueError(f"invalid recipe: increment={increment}  offset={offset}  num_beats={num_beats}")
        pattern = [round(increment.value * idx + offset_value, 3) for idx in range(note_count)]
        return cls(pattern=pattern, num_loops=num_loops)

    @classmethod
    def from_notes(cls, notes: list[Note], num_beats: int, num_loops: int = 1):
        """
        Build a bar from a list of Note values. For example:
        [Q Q Q Q QR QR QR Q Q Q Q QS QS QS QS Q Q]
        """
        pattern_sum = 0.0
        pattern = []
        for each_note in notes:
            pattern.append(pattern_sum)
            pattern_sum += each_note.value
            if pattern_sum >= num_beats:
                return cls(pattern=pattern, num_loops=num_loops)
        return cls(pattern=pattern, num_loops=num_loops)


class Phrase:
    """
    list of BarPattern to be iterated over. Next bar can be pulled with .next()
    """

    def __init__(self, bars: List[BarPattern]):
        self.bars = bars
        self.bar_idx = 0
        self.current_loop = 0

    @property
    def bar_count(self):
        return sum([bar.num_loops for bar in self.bars])

    def query(self, target_idx):
        target_idx %= self.bar_count - 1
        current_count = 0
        for bar in self.bars:
            if (target_idx - current_count) < bar.num_loops:
                return bar
            else:
                current_count += 1
        # reset the loop if none found
        self.bar_idx = 1
        return self.bars[0]

    def __iter__(self):
        return self

    # def __next__(self):
    #     self.bar_idx += 1
    #     next_bar = self.query(self.bar_idx - 1)
    #     assert isinstance(next_bar, BarPattern)
    #     return next_bar.pattern

    def __next__(self):
        self.bar_idx %= len(self.bars)
        current_bar = self.bars[self.bar_idx]

        if self.current_loop < current_bar.num_loops:
            self.current_loop += 1
            return current_bar.pattern
        else:
            self.bar_idx += 1
            self.bar_idx %= len(self.bars)
            self.current_loop = 0
            return self.bars[self.bar_idx].pattern


class Exercise:
    """
    Phrases in 4 voices that form an exercise routine
    """

    def __init__(self, left_foot: Phrase = None, right_foot: Phrase = None,
                 left_hand: Phrase = None, right_hand: Phrase = None):
        self.left_foot = left_foot
        self.right_foot = right_foot
        self.left_hand = left_hand
        self.right_hand = right_hand
        self.bar_idx = 0

    @classmethod
    def note_tree_feet_alternating(cls, num_beats: int = 4, num_loops: int = 2):
        increment_pattern = [Note.TWO, Note.WHOLE, Note.HALF, Note.QUARTER, Note.HALF, Note.WHOLE]
        # Iterate over increments for each foot
        right_foot_bars = [BarPattern.from_recipe(increment=increment, offset=0.0,
                                                  num_beats=num_beats, num_loops=num_loops)
                           for increment in increment_pattern]
        right_foot_phrase = Phrase(bars=right_foot_bars)
        left_foot_bars = [BarPattern.from_recipe(increment=increment, offset=0.5,
                                                 num_beats=num_beats, num_loops=num_loops)
                          for increment in increment_pattern]
        left_foot_phrase = Phrase(bars=left_foot_bars)
        return cls(left_foot=left_foot_phrase, right_foot=right_foot_phrase)

    @classmethod
    def left_to_right_note_tree(cls, num_beats: int = 4, num_loops: int = 2):
        right_foot_bars = [
            BarPattern.from_notes(notes=[
                Note.WHOLE,
                Note.HALF, Note.HALF,
                Note.QUARTER_TRIPLET, Note.QUARTER_TRIPLET, Note.QUARTER_TRIPLET,
                Note.QUARTER, Note.QUARTER, Note.QUARTER, Note.QUARTER,
            ], num_beats=num_beats, num_loops=num_loops),
            BarPattern.from_notes(notes=[], num_beats=num_beats, num_loops=num_loops),
            BarPattern.from_notes(notes=[
                Note.WHOLE,
                Note.HALF, Note.HALF,
                Note.QUARTER_TRIPLET, Note.QUARTER_TRIPLET, Note.QUARTER_TRIPLET,
                Note.QUARTER, Note.QUARTER, Note.QUARTER, Note.QUARTER,
            ], num_beats=num_beats, num_loops=num_loops),
            BarPattern.from_notes(notes=[
                Note.WHOLE,
                Note.HALF, Note.HALF,
                Note.QUARTER_TRIPLET, Note.QUARTER_TRIPLET, Note.QUARTER_TRIPLET,
                Note.QUARTER, Note.QUARTER, Note.QUARTER, Note.QUARTER,
            ], num_beats=num_beats, num_loops=num_loops)
        ]
        right_foot_phrase = Phrase(bars=right_foot_bars)
        left_foot_bars = [
            BarPattern.from_notes(notes=[], num_beats=num_beats, num_loops=num_loops),
            BarPattern.from_notes(notes=[
                Note.WHOLE,
                Note.HALF, Note.HALF,
                Note.QUARTER_TRIPLET, Note.QUARTER_TRIPLET, Note.QUARTER_TRIPLET,
                Note.QUARTER, Note.QUARTER, Note.QUARTER, Note.QUARTER,
            ], num_beats=num_beats, num_loops=num_loops),
            BarPattern.from_notes(notes=[
                Note.WHOLE,
                Note.HALF, Note.HALF,
                Note.QUARTER_TRIPLET, Note.QUARTER_TRIPLET, Note.QUARTER_TRIPLET,
                Note.QUARTER, Note.QUARTER, Note.QUARTER, Note.QUARTER,
            ], num_beats=num_beats, num_loops=num_loops),
            BarPattern.from_notes(notes=[
                Note.WHOLE,
                Note.HALF, Note.HALF,
                Note.QUARTER_TRIPLET, Note.QUARTER_TRIPLET, Note.QUARTER_TRIPLET,
                Note.QUARTER, Note.QUARTER, Note.QUARTER, Note.QUARTER,
            ], num_beats=num_beats, num_loops=num_loops)
        ]
        left_foot_phrase = Phrase(bars=left_foot_bars)
        return cls(left_foot=left_foot_phrase, right_foot=right_foot_phrase)

    def __iter__(self):
        return self

    def __next__(self):
        self.bar_idx += 1
        left_foot_pattern = []
        right_foot_pattern = []
        left_hand_pattern = []
        right_hand_pattern = []
        if self.left_foot is not None:
            left_foot_pattern = self.left_foot.__next__()
        if self.right_foot is not None:
            right_foot_pattern = self.right_foot.__next__()
        if self.left_hand is not None:
            left_hand_pattern = self.left_hand.__next__()
        if self.right_hand is not None:
            right_hand_pattern = self.right_hand.__next__()
        return [right_foot_pattern, left_foot_pattern, right_hand_pattern, left_hand_pattern]

    def preview(self):
        """
        Take a peek at the next upcoming pattern.
        """
        left_foot_pattern = []
        right_foot_pattern = []
        left_hand_pattern = []
        right_hand_pattern = []
        if self.left_foot is not None:
            left_foot_pattern = self.left_foot.query((self.left_foot.bar_idx + 1) % self.left_foot.bar_count)
        if self.right_foot is not None:
            right_foot_pattern = self.right_foot.query((self.right_foot.bar_idx + 1) % self.right_foot.bar_count)
        if self.left_hand is not None:
            left_hand_pattern = self.left_hand.query((self.left_hand.bar_idx + 1) % self.left_hand.bar_count)
        if self.right_hand is not None:
            right_hand_pattern = self.right_hand.query((self.right_hand.bar_idx + 1) % self.right_hand.bar_count)
        return [right_foot_pattern, left_foot_pattern, right_hand_pattern, left_hand_pattern]
