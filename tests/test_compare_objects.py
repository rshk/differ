from __future__ import division

from differ import compare_objects


def test_compare_base_types():
    assert compare_objects("Hello", "Hello") == {
        'distance': 0.0, 'left': "Hello", 'right': "Hello"}
    assert compare_objects("Hello", "World") == {
        'distance': 1.0, 'left': "Hello", 'right': "World"}

    assert compare_objects(1, 1) == {
        'distance': 0.0, 'left': 1, 'right': 1}
    assert compare_objects(1, 2) == {
        'distance': 1.0, 'left': 1, 'right': 2}

    assert compare_objects(True, True) == {
        'distance': 0.0, 'left': True, 'right': True}
    assert compare_objects(True, False) == {
        'distance': 1.0, 'left': True, 'right': False}

    assert compare_objects(1.0, 1.0) == {
        'distance': 0.0, 'left': 1.0, 'right': 1.0}
    assert compare_objects(1.0, 2.0) == {
        'distance': 1.0, 'left': 1.0, 'right': 2.0}


def test_compare_simple_dicts():
    dict1 = dict(aaa='A', bbb='B', ccc='C1')
    dict2 = dict(bbb='B', ccc='C2', ddd='D')

    diff = compare_objects(dict1, dict2)
    assert diff['distance'] == 3/4
    assert diff['added'] == ['ddd']
    assert diff['removed'] == ['aaa']
    assert diff['changed'] == ['ccc']
    assert diff['equal'] == ['bbb']
    assert diff['changes'] == {
        'ccc': {'distance': 1.0,
                'left': 'C1',
                'right': 'C2'}}


def test_compare_simple_sequences():
    seq1 = ['A', 'B', 'C', 'D']
    seq2 = ['A', 'D', 'E', 'C']
    diff = compare_objects(seq1, seq2)

    assert diff['distance'] == 4 / 5
    assert diff['added'] == [2]
    assert diff['removed'] == [1]
    assert diff['changed'] == [2, 3]
    assert sorted(diff['changes'].keys()) == [2, 3]
    assert diff['equal'] == [0]

    assert diff['changes'][2]['distance'] == 0.0
    assert diff['changes'][2]['pos'] == 3
    assert diff['changes'][3]['distance'] == 0.0
    assert diff['changes'][3]['pos'] == 1

    assert diff['total'] == 5


def test_compare_simple_sequences_different_length():
    seq1 = ['A', 'B', 'C', 'D']
    seq2 = ['A', 'D', 'E', 'C', 'F', 'G']
    diff = compare_objects(seq1, seq2)

    assert diff['distance'] == 6 / 7
    assert sorted(diff['added']) == [2, 4, 5]
    assert diff['removed'] == [1]
    assert sorted(diff['changed']) == [2, 3]
    assert sorted(diff['changes'].keys()) == [2, 3]
    assert diff['equal'] == [0]

    assert diff['changes'][2]['distance'] == 0.0
    assert diff['changes'][2]['pos'] == 3
    assert diff['changes'][3]['distance'] == 0.0
    assert diff['changes'][3]['pos'] == 1

    assert diff['total'] == 7


def test_compare_sequence_of_dicts():
    pass
