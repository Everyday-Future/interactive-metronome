
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


def test_exercise():
    test_pattern_1 = Pattern.from_tsv(name='test pattern', left_foot=['xxx,---,xxx,---'])
    test_pattern_2 = Pattern.from_tsv(name='test pattern',
                                      left_foot=['xxx,---,xxx,---', 'x---,x-x-,x---,x--x'],
                                      num_loops=3)
    test_ex = Exercise(name='test_exercise', patterns=[test_pattern_1, test_pattern_2])
    assert test_ex.__next__() == {'lf': [0.0, 0.33, 0.67, 2.0, 2.33, 2.67], 'lh': [], 'rf': [], 'rh': []}
    assert test_ex.__next__() == {'lf': [0.0, 0.33, 0.67, 2.0, 2.33, 2.67], 'lh': [], 'rf': [], 'rh': []}
    assert test_ex.__next__() == {'lf': [0.0, 1.0, 1.5, 2.0, 3.0, 3.75], 'lh': [], 'rf': [], 'rh': []}
    assert test_ex.__next__() == {'lf': [0.0, 0.33, 0.67, 2.0, 2.33, 2.67], 'lh': [], 'rf': [], 'rh': []}
    exercise_str = """
    Hand-To-Hand																
N	Quarter Note Warmup	Quarter Note Warmup	Alternating 8th Notes	Alternating 8th Notes	Triplet Warmup	Triplet Warmup	Alternating Triplets	Alternating Triplets	Alternating 8th Flams	Alternating 8th Flams	Alternating 16th Singles	Alternating 16th Singles	Alternating 16th Doubles	Alternating 16th Doubles	Paradiddles	Rev. Paradiddles	5 Stroke Roll
RH	x---,x---,x---,x---		x---,x---,x---,x---	--x-,--x-,--x-,--x-	x--,x--,x--,x--		x-x,-x-,x-x,-x-	-x-,x-x,-x-,x-x	x---,x---,x---,x---	--x-,--x-,--x-,--x-	x-x-,x-x-,x-x-,x-x-	-x-x,-x-x,-x-x,-x-x	xx--,xx--,xx--,x-xx	--xx,--xx,--xx,-x--	x-xx,-x--,x-xx,-x--	xx-x,--x-,xx-x,--x-	x-x-x---,-x-x----,x-x-x---,-x-x----
LH		x---,x---,x---,x---	--x-,--x-,--x-,--x-	x---,x---,x---,x---		x--,x--,x--,x--	-x-,x-x,-x-,x-x	x-x,-x-,x-x,-x-	--x-,--x-,--x-,--x-	x---,x---,x---,x---	-x-x,-x-x,-x-x,-x-x	x-x-,x-x-,x-x-,x-x-	--xx,--xx,--xx,-x--	xx--,xx--,xx--,x-xx	-x--,x-xx,-x--,x-xx	--x-,xx-x,--x-,xx-x	-x-x----,x-x-x---,-x-x----,x-x-x---
RF																	
LF																	
Loops	4		4		4		4		2		8				4		4
    """
    test_ex = Exercise.from_tsv(exercise_str=exercise_str.strip())
    assert test_ex.name == "Hand-To-Hand"
    assert len(test_ex.patterns) == 8
    assert test_ex.patterns[0].right_hand == [[0.0, 1.0, 2.0, 3.0], []]
    assert test_ex.patterns[0].left_hand == [[], [0.0, 1.0, 2.0, 3.0]]
    assert test_ex.__next__() == {'rh': [0.0, 1.0, 2.0, 3.0], 'lh': [], 'rf': [], 'lf': []}
    assert test_ex.__next__() == {'lf': [], 'lh': [0.0, 1.0, 2.0, 3.0], 'rf': [], 'rh': []}
    assert test_ex.__next__() == {'rh': [0.0, 1.0, 2.0, 3.0], 'lh': [], 'rf': [], 'lf': []}
    assert test_ex.__next__() == {'lf': [], 'lh': [0.0, 1.0, 2.0, 3.0], 'rf': [], 'rh': []}
    assert test_ex.__next__() == {'rh': [0.0, 1.0, 2.0, 3.0], 'lh': [], 'rf': [], 'lf': []}
    assert test_ex.__next__() == {'lf': [], 'lh': [0.0, 1.0, 2.0, 3.0], 'rf': [], 'rh': []}
    assert test_ex.__next__() == {'rh': [0.0, 1.0, 2.0, 3.0], 'lh': [], 'rf': [], 'lf': []}
    assert test_ex.__next__() == {'lf': [], 'lh': [0.0, 1.0, 2.0, 3.0], 'rf': [], 'rh': []}
    assert test_ex.__next__() == {'lf': [], 'lh': [0.5, 1.5, 2.5, 3.5], 'rf': [], 'rh': [0.0, 1.0, 2.0, 3.0]}
    all_results = [exs for exs in test_ex]
    assert len(all_results) < 10000
    test_ex.reset()
    all_results = [exs for exs in test_ex]
    assert len(all_results) < 10000


def test_exercise_factory():
    ex_f = ExerciseFactory()
    assert len(ex_f.exercises) >= 3
    assert isinstance(ex_f.exercises[0], Exercise)
    assert ex_f.exercises[0].name == 'Happy Feet'
    assert ex_f.exercises[0].patterns[0].right_foot == [[0.0, 1.0, 2.0, 3.0], []]
    assert ex_f.exercises[0].patterns[0].left_foot == [[], [0.0, 1.0, 2.0, 3.0]]
