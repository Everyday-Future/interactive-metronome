import json
from metronome.exercise.exercise import Pattern, Exercise, ExerciseFactory


def test_pattern_init():
    test_pattern = Pattern(name='test pattern', left_foot=[[0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5]])
    assert isinstance(test_pattern, Pattern)
    assert len(test_pattern.right_foot) == 1
    assert len(test_pattern.right_hand) == 1
    assert len(test_pattern.left_hand) == 1
    assert test_pattern.right_foot[0] == []
    assert test_pattern.right_hand[0] == []
    assert test_pattern.left_hand[0] == []
    assert test_pattern.num_bars == 1
    assert test_pattern.max_len == 1
    test_pattern = Pattern(name='test pattern',
                           left_foot=[[0.33, 1.33, 2.33, 3.33], [0.33, 1.33, 2.33, 3.33]],
                           num_loops=3)
    assert isinstance(test_pattern, Pattern)
    assert len(test_pattern.right_foot) == 2
    assert len(test_pattern.right_hand) == 2
    assert len(test_pattern.left_hand) == 2
    assert test_pattern.right_foot[1] == []
    assert test_pattern.right_hand[1] == []
    assert test_pattern.left_hand[1] == []
    assert test_pattern.num_bars == 2
    assert test_pattern.max_len == 6


def test_pattern_from_tsv():
    test_pattern = Pattern.from_tsv(name='test pattern', left_foot=['xxx,---,xxx,---'])
    assert len(test_pattern.left_foot) == 1
    assert test_pattern.left_foot[0] == [0.0, 0.33, 0.67, 2.0, 2.33, 2.67]
    assert len(test_pattern.right_foot) == 1
    assert len(test_pattern.right_hand) == 1
    assert len(test_pattern.left_hand) == 1
    assert test_pattern.right_foot[0] == []
    assert test_pattern.right_hand[0] == []
    assert test_pattern.left_hand[0] == []
    assert test_pattern.num_bars == 1
    assert test_pattern.max_len == 1
    test_pattern = Pattern.from_tsv(name='test pattern',
                                    left_foot=['xxx,---,xxx,---', 'x---,x-x-,x---,x--x'],
                                    num_loops=3)
    assert len(test_pattern.left_foot) == 2
    assert test_pattern.left_foot[1] == [0.0, 1.0, 1.5, 2.0, 3.0, 3.75]
    assert len(test_pattern.right_foot) == 2
    assert len(test_pattern.right_hand) == 2
    assert len(test_pattern.left_hand) == 2
    assert test_pattern.right_foot[1] == []
    assert test_pattern.right_hand[1] == []
    assert test_pattern.left_hand[1] == []
    assert test_pattern.num_bars == 2
    assert test_pattern.max_len == 6
    out_pattern = [pat['lf'] for pat in test_pattern]
    assert out_pattern == [[0.0, 0.33, 0.67, 2.0, 2.33, 2.67], [0.0, 1.0, 1.5, 2.0, 3.0, 3.75],
                           [0.0, 0.33, 0.67, 2.0, 2.33, 2.67], [0.0, 1.0, 1.5, 2.0, 3.0, 3.75],
                           [0.0, 0.33, 0.67, 2.0, 2.33, 2.67], [0.0, 1.0, 1.5, 2.0, 3.0, 3.75]]


def test_pattern_last_beat():
    test_pattern = Pattern(name='test pattern', left_foot=[[0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5]], num_loops=1)
    assert test_pattern.__next__()['lf'] == [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5]
    assert test_pattern.is_last_beat() is True
    test_pattern = Pattern(name='test pattern', left_foot=[[0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5]], num_loops=2)
    assert test_pattern.is_last_beat() is False
    test_pattern = Pattern(name='test pattern', left_foot=[[0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5], [1.0, 2.0]],
                           num_loops=2)
    assert test_pattern.__next__()['lf'] == [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5]
    assert test_pattern.__next__()['lf'] == [1.0, 2.0]
    assert test_pattern.__next__()['lf'] == [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5]
    assert test_pattern.__next__()['lf'] == [1.0, 2.0]
    try:
        test_pattern.__next__()
        assert False
    except StopIteration:
        pass


def test_exercise():
    test_pattern_1 = Pattern.from_tsv(name='test pattern', left_foot=['xxx,---,xxx,---'])
    test_pattern_2 = Pattern.from_tsv(name='test pattern',
                                      left_foot=['xxx,---,xxx,---', 'x---,x-x-,x---,x--x'],
                                      num_loops=3)
    test_ex = Exercise(name='test_exercise', patterns=[test_pattern_1, test_pattern_2])
    assert test_ex.__next__() == {'name': 'test pattern', 'lf': [0.0, 0.33, 0.67, 2.0, 2.33, 2.67], 'lh': [], 'rf': [], 'rh': []}
    assert test_ex.__next__() == {'name': 'test pattern', 'lf': [0.0, 0.33, 0.67, 2.0, 2.33, 2.67], 'lh': [], 'rf': [], 'rh': []}
    assert test_ex.__next__() == {'name': 'test pattern', 'lf': [0.0, 1.0, 1.5, 2.0, 3.0, 3.75], 'lh': [], 'rf': [], 'rh': []}
    assert test_ex.__next__() == {'name': 'test pattern', 'lf': [0.0, 0.33, 0.67, 2.0, 2.33, 2.67], 'lh': [], 'rf': [], 'rh': []}
    exercise_str = """
    Hand-To-Hand																
N	Quarter Note Warmup1	Quarter Note Warmup2	Alternating 8th Notes1	Alternating 8th Notes2	Triplet Warmup1	Triplet Warmup2	Alternating Triplets	Alternating Triplets	Alternating 8th Flams	Alternating 8th Flams	Alternating 16th Singles	Alternating 16th Singles	Alternating 16th Doubles	Alternating 16th Doubles	Paradiddles	Rev. Paradiddles	5 Stroke Roll
RH	x---,x---,x---,x---		x---,x---,x---,x---	--x-,--x-,--x-,--x-	x--,x--,x--,x--		x-x,-x-,x-x,-x-	-x-,x-x,-x-,x-x	x---,x---,x---,x---	--x-,--x-,--x-,--x-	x-x-,x-x-,x-x-,x-x-	-x-x,-x-x,-x-x,-x-x	xx--,xx--,xx--,x-xx	--xx,--xx,--xx,-x--	x-xx,-x--,x-xx,-x--	xx-x,--x-,xx-x,--x-	x-x-x---,-x-x----,x-x-x---,-x-x----
LH		x---,x---,x---,x---	--x-,--x-,--x-,--x-	x---,x---,x---,x---		x--,x--,x--,x--	-x-,x-x,-x-,x-x	x-x,-x-,x-x,-x-	--x-,--x-,--x-,--x-	x---,x---,x---,x---	-x-x,-x-x,-x-x,-x-x	x-x-,x-x-,x-x-,x-x-	--xx,--xx,--xx,-x--	xx--,xx--,xx--,x-xx	-x--,x-xx,-x--,x-xx	--x-,xx-x,--x-,xx-x	-x-x----,x-x-x---,-x-x----,x-x-x---
RF																	
LF																	
Loops	2		2		2		2		2		2				2		2
    """
    test_ex = Exercise.from_tsv(exercise_str=exercise_str.strip())
    assert test_ex.name == "Hand-To-Hand"
    assert len(test_ex.patterns) == 8
    assert test_ex.patterns[0].right_hand == [[0.0, 1.0, 2.0, 3.0], []]
    assert test_ex.patterns[0].left_hand == [[], [0.0, 1.0, 2.0, 3.0]]
    # assert test_ex.__next__() == {'name': 'Quarter Note Warmup1', 'rh': [0.0, 1.0, 2.0, 3.0], 'lh': [], 'rf': [], 'lf': []}
    # assert test_ex.__next__() == {'name': 'Quarter Note Warmup2', 'lf': [], 'lh': [0.0, 1.0, 2.0, 3.0], 'rf': [], 'rh': []}
    # assert test_ex.__next__() == {'name': 'Quarter Note Warmup1', 'rh': [0.0, 1.0, 2.0, 3.0], 'lh': [], 'rf': [], 'lf': []}
    # assert test_ex.__next__() == {'name': 'Quarter Note Warmup2', 'lf': [], 'lh': [0.0, 1.0, 2.0, 3.0], 'rf': [], 'rh': []}
    # assert test_ex.__next__() == {'name': 'Alternating 8th Notes1', 'lf': [], 'lh': [0.5, 1.5, 2.5, 3.5], 'rf': [], 'rh': [0.0, 1.0, 2.0, 3.0]}
    # assert test_ex.__next__() == {'name': 'Alternating 8th Notes2', 'lf': [], 'lh': [0.0, 1.0, 2.0, 3.0], 'rf': [], 'rh': [0.5, 1.5, 2.5, 3.5]}
    test_ex.reset()
    all_results = [exs for exs in test_ex]
    print('len(all_results)', len(all_results))
    print('(all_results)', json.dumps([res for res in all_results]))
    assert len(all_results) < 10000
    test_ex.reset()
    all_results = [exs for exs in test_ex]
    assert len(all_results) < 10000


def test_exercise_last_beat():
    test_pattern_1 = Pattern.from_tsv(name='test pattern', left_foot=['xxx,---,xxx,---'])
    test_pattern_2 = Pattern.from_tsv(name='test pattern',
                                      left_foot=['xxx,-x-,xxx,-x-', 'x---,x-x-,x---,x--x'],
                                      num_loops=1)
    test_ex = Exercise(name='test_exercise', patterns=[test_pattern_1, test_pattern_2])
    assert test_ex.is_last_beat() is False
    assert test_ex.__next__()['lf'] == [0.0, 0.33, 0.67, 2.0, 2.33, 2.67]
    assert test_ex.__next__()['lf'] == [0.0, 0.33, 0.67, 1.33, 2.0, 2.33, 2.67, 3.33]
    assert test_ex.is_last_beat() is True
    assert test_ex.__next__()['lf'] == [0.0, 1.0, 1.5, 2.0, 3.0, 3.75]
    try:
        test_ex.__next__()
        assert False
    except StopIteration:
        pass


def test_exercise_factory():
    ex_f = ExerciseFactory()
    assert len(ex_f.exercises) >= 3
    assert isinstance(ex_f.exercises[1], Exercise)
    assert ex_f.exercises[1].name == 'Happy Feet'
    assert ex_f.exercises[1].patterns[0].right_foot == [[0.0, 1.0, 2.0, 3.0], []]
    assert ex_f.exercises[1].patterns[0].left_foot == [[], [0.0, 1.0, 2.0, 3.0]]
