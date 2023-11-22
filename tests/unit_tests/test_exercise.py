
from metronome.exercise.exercise import BarPattern, Note


def test_beat_pattern_from_recipe():
    whole_notes = BarPattern.from_recipe(increment=Note.WHOLE, offset=0.0, num_beats=4, num_loops=1)
    assert isinstance(whole_notes, BarPattern)
    assert whole_notes.pattern == [0.0, 1.0, 2.0, 3.0]
    whole_notes_offset = BarPattern.from_recipe(increment=Note.WHOLE, offset=0.5, num_beats=4, num_loops=1)
    assert whole_notes_offset.pattern == [0.5, 1.5, 2.5, 3.5]
    quarter_beats = BarPattern.from_recipe(increment=Note.QUARTER, offset=0.5, num_beats=4, num_loops=1)
    assert quarter_beats.pattern == [0.125, 0.375, 0.625, 0.875, 1.125, 1.375, 1.625, 1.875,
                                     2.125, 2.375, 2.625, 2.875, 3.125, 3.375, 3.625, 3.875]
    triplet_beats = BarPattern.from_recipe(increment=Note.QUARTER_TRIPLET, offset=0.5,
                                           num_beats=4, num_loops=1)
    assert triplet_beats.pattern == [0.167, 0.5, 0.833, 1.167, 1.5, 1.833, 2.167, 2.5, 2.833, 3.167, 3.5, 3.833]
    three_four_bar = BarPattern.from_recipe(increment=Note.WHOLE, offset=0.0, num_beats=3)
    assert three_four_bar.pattern == [0.0, 1.0, 2.0]
    three_four_bar = BarPattern.from_recipe(increment=Note.WHOLE, offset=0.5, num_beats=3)
    assert three_four_bar.pattern == [0.5, 1.5, 2.5]

