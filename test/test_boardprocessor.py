import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 

import trello
from data import boardprocessor

members = {
    0: 'Member One',
    1: 'Member Two',
    2: 'Member Three',
    3: 'Member Four',
}

lists = {
    'List 1': [{"id":i,"name":"card number {}".format(i), "members":[i]} for i in range(0,4)],
    'List 2': [{"id":i,"name":"card number {}".format(i), "members":[i]} for i in range(0,3)],
    'List 3': [],
}

def test_cardsPerList():
    ''''''

    processor = boardprocessor.BoardListProcessor()
    data = processor.getCardsPerListData(lists)

    assert len(data) == 3
    assert data['List 1'] == 4
    assert data['List 2'] == 3
    assert data['List 3'] == 0

def test_cardsPerMember():
    processor = boardprocessor.BoardListProcessor()
    data = processor.getCardsPerMemberData(lists, members)

    assert len(data) == 3
    assert len(data['List 1']['Member One']) == 1
    assert len(data['List 2']['Member One']) == 1

    assert len(data['List 1']['Member Two']) == 1
    assert len(data['List 2']['Member Two']) == 1

    assert len(data['List 1']['Member Three']) == 1
    assert len(data['List 2']['Member Three']) == 1

    assert len(data['List 1']['Member Four']) == 1