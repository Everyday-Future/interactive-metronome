
import math
from typing import List
from enum import Enum


class Note(Enum):
    QUARTER = 1.0
    EIGHTH = 0.5
    EIGHTH_TRIPLET = 1.0 / 3.0
    SIXTEENTH = 0.25
    SIXTEENTH_TRIPLET = 1.0 / 6.0
    THIRTY_SECOND = 0.125
    EMPTY = 0.0


class NoteBeat(Enum):
    """
    Mini-phrases to join together like "x---,x---,x---,x---|x---,x---,x---,x---|x---,x---,x---,x---"
    The phrase is split on the commas for each beat and on the bars for each bar.
    Each phrase is evenly distributed across the beat.
    """
    OO = "--"
    XO = "x-"
    OX = "-x"
    XX = "xx"
    OOO = "---"
    XOO = "x--"
    OXO = "-x-"
    XXO = "xx-"
    OOX = "--x"
    XOX = "x-x"
    OXX = "-xx"
    XXX = "xxx"
    XXXX = "----"
    XOOO = "x---"
    OXOO = "-x--"
    XXOO = "xx--"
    OOXO = "--x-"
    XOXO = "x-x-"
    OXXO = "-xx-"
    OOOX = "---x"
    XOOX = "x--x"
    OXOX = "-x-x"
    XXOX = "xx-x"
    OOXX = "--xx"
    XOXX = "x-xx"
    OOOO = "xxxx"

    # def __init__(self):
    #     self.pattern_dict = {
    #         # Triplet phrases
    #         "XOO": "x--",
    #         "OXO": "-x-",
    #         "XXO": "xx-",
    #         "OOX": "--x",
    #         "XOX": "x-x",
    #         "OXX": "-xx",
    #         "XXX": "xxx",
    #         # 16th note phrases
    #         "OOOO": "----",
    #         "XOOO": "x---",
    #         "OXOO": "-x--",
    #         "XXOO": "xx--",
    #         "OOXO": "--x-",
    #         "XOXO": "x-x-",
    #         "OXXO": "-xx-",
    #         "OOOX": "---x",
    #         "XOOX": "x--x",
    #         "OXOX": "-x-x",
    #         "XXOX": "xx-x",
    #         "OOXX": "--xx",
    #         "XOXX": "x-xx",
    #         "OXXX": "-xxx",
    #         "XXXX": "xxxx"
    #     }

    @staticmethod
    def flip_chunk(chunk):
        flipped = ''
        for char in chunk.pattern:
            if char == 'x':
                flipped += '-'
            elif char == '-':
                flipped += 'x'
            else:
                flipped += char
        return flipped

    def phrase(self, beats_per_bar, num_bars=1, is_alternating=False):
        """
        Pick an enum value like XOXO and turn it into a repeating phrase
        """
        phrase_str = self.value
        out_phrase = []
        for idx in range(beats_per_bar * num_bars):
            if idx % 2 == 0:
                out_phrase += phrase_str
            if idx % 2 == 1 and is_alternating is True:
                out_phrase += self.flip_chunk(phrase_str)
            else:
                out_phrase += phrase_str
        out_phrase = ','.join(out_phrase)
        return out_phrase

    @classmethod
    def from_beat_phrase(cls, phrase: str, num_beats=4, is_alternating=False):
        bar_phrase = ""
        for each_beat in num_beats:
            bar_phrase = ','.join(phrase) * num_beats



class NoteChunk(Enum):
    XXXX = "----------------"
    OOOO = "xxxxxxxxxxxxxxxx"
    # quarter notes, offset by 0
    XOOO = "x---x---x---x---"
    # quarter notes, offset by 1
    OXOO = "-x---x---x---x--"
    # quarter notes, offset by 2
    OOXO = "--x---x---x---x-"
    # quarter notes, offset by 3
    OOOX = "---x---x---x---x"
    # leading singles
    XOXO = "x-x-x-x-x-x-x-x-"
    # trailing singles
    OXOX = "-x-x-x-x-x-x-x-x"
    # Leading doubles
    XXOO = "xx--xx--xx--xx--"
    # Trailing doubles
    OOXX = "--xx--xx--xx--xx"
    # leading bar-splitting doubles
    XOOX = "x--xx--xx--xx--x"
    # trailing bar-splitting doubles
    OXXO = "-xx--xx--xx--xx-"
    # leading paradiddles
    DXOXX = "x-xx-x--x-xx-x--"
    # trailing paradiddles
    DOXOO = "-x--x-xx-x--x-xx"
    # leading reverse-paradiddles
    DXXOX = "xx-x--x-xx-x--x-"
    # trailing reverse-paradiddles
    DOOXO = "--x-xx-x--x-xx-x"
    # alternate extended groupings
    XXXXOOOO = "xxxx----xxxx----"
    OOOOXXXX = "----xxxx----xxxx"
    OOO = "------------"
    XXX = "xxxxxxxxxxxx"
    XOO = "x--x--x--x--"
    OXO = "-x--x--x--x-"
    OOX = "--x--x--x--x"
    XXO = "xx-xx-xx-xx-"
    XOX = "x-xx-xx-xx-x"
    OXX = "-xx-xx-xx-xx"
    # alternate triplets
    XOXOXO = "x-x-x-x-x-x-"
    OXOXOX = "-x-x-x-x-x-x"
    # alternate extended groupings
    XXXOOO = "xxx---xxx---"
    OOOXXX = "---xxx---xxx"


class ChunkGenerator:
    def __init__(self, beats_per_bar=4, num_loops=1):
        self.beats_per_bar = beats_per_bar
        self.num_loops = num_loops

    def generate(self, base_chunk_name):
        if base_chunk_name == 'XXXX':
            return BarPattern.from_note_chunk(chunk='xxxx' * self.beats_per_bar, num_loops=self.num_loops)
    XXXX = "----------------"
    OOOO = "xxxxxxxxxxxxxxxx"
    # quarter notes, offset by 0
    XOOO = "x---x---x---x---"
    # quarter notes, offset by 1
    OXOO = "-x---x---x---x--"
    # quarter notes, offset by 2
    OOXO = "--x---x---x---x-"
    # quarter notes, offset by 3
    OOOX = "---x---x---x---x"
    # leading singles
    XOXO = "x-x-x-x-x-x-x-x-"
    # trailing singles
    OXOX = "-x-x-x-x-x-x-x-x"
    # Leading doubles
    XXOO = "xx--xx--xx--xx--"
    # Trailing doubles
    OOXX = "--xx--xx--xx--xx"
    # leading bar-splitting doubles
    XOOX = "x--xx--xx--xx--x"
    # trailing bar-splitting doubles
    OXXO = "-xx--xx--xx--xx-"
    # leading paradiddles
    DXOXX = "x-xx-x--x-xx-x--"
    # trailing paradiddles
    DOXOO = "-x--x-xx-x--x-xx"
    # leading reverse-paradiddles
    DXXOX = "xx-x--x-xx-x--x-"
    # trailing reverse-paradiddles
    DOOXO = "--x-xx-x--x-xx-x"
    # alternate extended groupings
    XXXXOOOO = "xxxx----xxxx----"
    OOOOXXXX = "----xxxx----xxxx"
    OOO = "------------"
    XXX = "xxxxxxxxxxxx"
    XOO = "x--x--x--x--"
    OXO = "-x--x--x--x-"
    OOX = "--x--x--x--x"
    XXO = "xx-xx-xx-xx-"
    XOX = "x-xx-xx-xx-x"
    OXX = "-xx-xx-xx-xx"
    # alternate triplets
    XOXOXO = "x-x-x-x-x-x-"
    OXOXOX = "-x-x-x-x-x-x"
    # alternate extended groupings
    XXXOOO = "xxx---xxx---"
    OOOXXX = "---xxx---xxx"


def flip_chunk(chunk):
    flipped = ''
    for char in chunk.value:
        if char == 'x':
            flipped += '-'
        elif char == '-':
            flipped += 'x'
        else:
            flipped += char
    return flipped


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

    @classmethod
    def from_note_chunk(cls, chunk: NoteChunk, num_beats: int, num_loops: int = 1):
        chunk_str = chunk.value
        pattern = []
        if int(len(chunk_str) / num_beats) == 3:
            # Triplet notation processing
            for idx, note in enumerate(chunk_str):
                if note == 'x':
                    pattern.append(round(idx * 0.333333, 2))
        elif int(len(chunk_str) / num_beats) == 4:
            # Sixteenth note notation processing
            for idx, note in enumerate(chunk_str):
                if note == 'x':
                    pattern.append(round(idx * 0.25, 2))
        return cls(pattern=pattern, num_loops=num_loops)


class Phrase:
    """
    list of BarPattern to be iterated over. Next bar can be pulled with .next()
    """

    def __init__(self, bars: List[BarPattern]):
        self.bars = bars
        self.bar_idx = 0
        self.current_loop = 0

    @classmethod
    def from_chunks(cls, chunk_list: list[NoteChunk], num_beats: int, num_loops: int = 1):
        bars = [BarPattern.from_note_chunk(chunk=chunk, num_beats=num_beats, num_loops=num_loops)
                for chunk in chunk_list]
        return cls(bars=bars)

    @staticmethod
    def preprocess_notation_chunk(notation_str):
        notation_str = notation_str.replace('\r\n', '\r').replace('\n\r', '\r')
        notation_str = notation_str.replace('\r\r', '\r').replace('\r\r', '\r').strip().split('\r')
        return [notes.strip() for notes in notation_str.split('|') if len(notes.strip()) > 0]

    @classmethod
    def from_chunk_str(cls, chunk_str: str, num_beats: int, num_loops: int = 1):
        chunk_list = cls.preprocess_notation_chunk(chunk_str)
        bars = [BarPattern.from_note_chunk(chunk=chunk, num_beats=num_beats, num_loops=num_loops)
                for chunk in chunk_list]
        return cls(bars=bars)

    @classmethod
    def from_note_beat_str(cls, beat_str, beats_per_bar: int, num_loops: int = 1):
        bars = cls.preprocess_notation_chunk(beat_str)
        pattern = []
        if int(len(chunk_str) / num_beats) == 3:
            # Triplet notation processing
            for idx, note in enumerate(chunk_str):
                if note == 'x':
                    pattern.append(round(idx * 0.333333, 2))
        elif int(len(chunk_str) / num_beats) == 4:
            # Sixteenth note notation processing
            for idx, note in enumerate(chunk_str):
                if note == 'x':
                    pattern.append(round(idx * 0.25, 2))
        return cls(pattern=pattern, num_loops=num_loops)

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

    def __init__(self, name, left_foot: Phrase = None, right_foot: Phrase = None,
                 left_hand: Phrase = None, right_hand: Phrase = None):
        self.name = name
        self.left_foot = left_foot
        self.right_foot = right_foot
        self.left_hand = left_hand
        self.right_hand = right_hand
        self.bar_idx = 0

    @staticmethod
    def parse_rlrl_pattern_into_bars(rlrl_pattern):
        right_bars = []
        left_bars = []
        for notation_bar in rlrl_pattern.upper().split('|'):
            if notation_bar == '':
                right_bars.append(BarPattern(pattern=[]))
                left_bars.append(BarPattern(pattern=[]))
            else:
                right_pattern = []
                left_pattern = []
                for idx, hand in enumerate(notation_bar):
                    if hand == 'L':
                        left_pattern.append(idx * 0.25)
                    else:
                        right_pattern.append(idx * 0.25)
                right_bars.append(BarPattern(pattern=right_pattern))
                left_bars.append(BarPattern(pattern=left_pattern))
        return right_bars, left_bars

    @classmethod
    def from_sixteenth_notes_RLRL(cls, hand_pattern: str, is_feet: bool = False, name=None):
        """
        Expect a string of LRLLRLRRLLRRLLRR|RRLLRRLLRLRRLRLL etc... and build a pattern from it.
        """
        right_bars, left_bars = cls.parse_rlrl_pattern_into_bars(rlrl_pattern=hand_pattern)
        if name is None:
            name = f"16th Notes RLRL {'Feet' if is_feet else 'Hands'}"
        if is_feet:
            return cls(name=name, left_foot=Phrase(bars=left_bars), right_foot=Phrase(bars=right_bars))
        else:
            return cls(name=name, left_hand=Phrase(bars=left_bars), right_hand=Phrase(bars=right_bars))

    @classmethod
    def from_sixteenth_notes_rlRL(cls, hand_pattern: str, foot_pattern: str, name=None):
        """
        Expect a string of LRLLRLRRLLRRLLRR|RRLLRRLLRLRRLRLL etc... and build a pattern from it.
        One for each, upstairs and downstairs
        """
        right_hand_bars, left_hand_bars = cls.parse_rlrl_pattern_into_bars(rlrl_pattern=hand_pattern)
        right_foot_bars, left_foot_bars = cls.parse_rlrl_pattern_into_bars(rlrl_pattern=foot_pattern)
        return cls(name=name or "16th Notes RLRL Upstairs to Downstairs",
                   left_hand=Phrase(bars=left_hand_bars), right_hand=Phrase(bars=right_hand_bars),
                   left_foot=Phrase(bars=left_foot_bars), right_foot=Phrase(bars=right_foot_bars))

    @staticmethod
    def preprocess_notation_chunk(notation_str):
        notation_str = notation_str.replace('\r\n', '\r').replace('\n\r', '\r')
        notation_str = notation_str.replace('\r\r', '\r').replace('\r\r', '\r').strip().split('\r')
        return [notes.strip() for notes in notation_str]

    @classmethod
    def preprocess_notation_string(cls, notation_str):
        notation_list = cls.preprocess_notation_chunk(notation_str)
        assert len(notation_list) == 4
        first_len = len(notation_list[0])
        assert all([len(notes) == first_len for notes in notation_list])
        return notation_list

    @classmethod
    def from_sixteenth_notes_xxxx(cls, notation_str: str):
        """
        Build a pattern from rows of xxxx notation from right_hand, left_hand, right_foot, left_foot
        For example:
        RH xxxx----xxxx----|----------------|xxxxxxxx--------|xxxxxxxx--------
        LH ----xxxx----xxxx|----------------|--------xxxxxxxx|--------xxxxxxxx
        RF ----------------|xxxx----xxxx----|xxxxxxxx--------|--------xxxxxxxx
        LF ----------------|----xxxx----xxxx|--------xxxxxxxx|xxxxxxxx--------
        """

    @classmethod
    def from_note_chunk_array(cls, hand_chunks: list, feet_chunks: list):
        assert len(hand_chunks) == len(feet_chunks)
        for idx in range(len(hand_chunks)):
            pass


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
        return cls(name='Note Tree, Alternating Feet', left_foot=left_foot_phrase, right_foot=right_foot_phrase)

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
        return cls(name="Note Tree, Left to Right", left_foot=left_foot_phrase, right_foot=right_foot_phrase)

    @classmethod
    def by_name(cls, exercise_name, beats_per_bar=4):
        if exercise_name == 'Happy Feet':
            return cls.note_tree_feet_alternating(num_beats=beats_per_bar, num_loops=4)

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
