"""
Tests for the GameMap object
"""

import src.misc_constants as misc_constants
from src.misc_constants import printColors
from src.objects.gamemap import *
import pytest

# to run, must have pytest installed see: http://pytest.org/latest/getting-started.html
# to get the import statement to run correctly, you must run
# <export PYTHONPATH=`pwd`> in the root directory


# Test addPlayer's basic functionality
def test_addPlayer():

    # Check player adding
    _map = GameMap(misc_constants.mapFile)
    _map.addPlayer(1)
    assert _map.players[0] == 1

    # Check initial node assignment
    myNodes = _map.getPlayerNodes(1)
    assert len(myNodes) == 1
    assert myNodes[0].isIPSed is True
    assert myNodes[0].nodetype == "Large City"

    # Check infiltration values
    for n in _map.nodes.values():
        assert 1 in n.infiltration


# Test handling of wrongly-formatted player IDs
# (Tested here since it may cause 'insidious' errors down the line)
def test_addPlayer_ForceInt():
    _map = GameMap(misc_constants.mapFile)
    with pytest.raises(ValueError):
        _map.addPlayer("1")
    with pytest.raises(ValueError):
        _map.addPlayer(None)
    with pytest.raises(ValueError):
        _map.addPlayer(-1)


# Test dupe-team checking
def test_addDupeTeam():
    _map = GameMap(misc_constants.mapFile)
    with pytest.raises(DuplicatePlayerException):
        _map.addPlayer(1)
        _map.addPlayer(1)
    assert _map.players[0] == 1
    assert len(_map.players) == 1


# Test getPlayerNodes
def test_getPlayerNodes():
    _map = GameMap(misc_constants.mapFile)
    _map.addPlayers(1)
    _result = _map.getPlayerNodes(1)
    _correct = [x.id for x in _map.nodes.values() if x.playerId == 1]
    assert sorted(_result) == sorted(_correct)


# Test handling of wrongly-formatted player IDs
def test_getPlayerNodes():
    _map = GameMap(misc_constants.mapFile)
    with pytest.raises(ValueError):
        _map.getPlayerNodes("1")
    with pytest.raises(ValueError):
        _map.getPlayerNodes(None)
    with pytest.raises(ValueError):
        _map.getPlayerNodes(-1)


# Test getNodesOfType
def test_getNodesOfType():
    _map = GameMap(misc_constants.mapFile)
    _result = _map.getNodesOfType("Large City")
    _correct = [x for x in _map.nodes.values() if x.nodetype == "Large City"]
    assert sorted(_result) == sorted(_correct)


# Test resetAfterTurn's DDoS updates
def test_resetAfterTurn_DDoS():
    _map = GameMap(misc_constants.mapFile)
    _map.addPlayer(1)
    _node = _map.getPlayerNodes(1)[0]
    _node.isIPSed = False  # In case the player is assigned this node

    # Test DDoSing a node
    _node.targeterId = 1
    assert _node.DDoSPending is False
    assert _node.DDoSed is False
    _node.doDDoS()
    assert _node.DDoSPending is True
    assert _node.DDoSed is False
    _map.resetAfterTurn()
    assert _node.DDoSPending is False
    assert _node.DDoSed is True

    # Test resetting the DDoS
    _map.resetAfterTurn()
    assert _node.DDoSed is False


# Test that resetAfterTurn allows only one IPSed node
def test_resetAfterTurn_ipsMultiple():
    _map = GameMap(misc_constants.mapFile)
    _node = _map.nodes[0]
    _node2 = _map.nodes[1]

    _map.addPlayer(1)
    for x in [_node, _node2]:
        if x.ownerId != 1:
            x.own(1)
        x.isIPSed = False
        x.IPSPending = True

    _map.resetAfterTurn()
    assert _node.IPSPending is False
    assert _node2.IPSPending is False
    assert _node.isIPSed or _node2.isIPSed
    assert _node.isIPSed is not _node2.isIPSed
    

# Test resetAfterTurn's conquering updates
# NOTE: This only cares about CONQUERING - not about mere infiltration attempts
def test_resetAfterTurn_conquer():
    _map = GameMap(misc_constants.mapFile)
    _node = _map.nodes[0]
    _map.addPlayer(1)
    _map.addPlayer(2)
    _map.addPlayer(3)
    if _node.ownerId != 3:
        _node.own(3)

    # Test conquering unoccupied nodes
    _node.infiltration[1] = 99999
    assert _node.ownerId == 3
    _map.resetAfterTurn()
    assert _node.infiltration[1] == 0
    assert _node.ownerId == 1

    # Test conquering occupied nodes
    _node.infiltration[2] = 99999
    _map.resetAfterTurn()
    assert _node.infiltration[1] == 0
    assert _node.infiltration[2] == 0
    assert _node.ownerId == 2

    # Test absolute tiebreaking (one player has more infiltration than the other)
    _node.infiltration[3] = 99999
    _node.infiltration[1] = 99998
    _map.resetAfterTurn()
    for i in range(1, 4):
        assert _node.infiltration[i] == 0
    assert _node.ownerId == 3

    # Test random tiebreaking (two players have equal infiltration)
    # NOTE: In extreme circumstances, THIS CAN FAIL!
    _timeout = 1000
    _team1 = 0
    _team2 = 0
    while (_team1 == 0 or _team2 == 0) and _timeout > 0:
        _timeout -= 1

        # Infiltrate the node
        _node.infiltration[1] = 99999
        _node.infiltration[2] = 99999
        _map.resetAfterTurn()

        # Record winner
        if _node.ownerId == 1:
            _team1 += 1
        elif _node.ownerId == 2:
            _team2 += 1
        else:
            assert False  # This should never happen

        # Reset node
        _node.own(3)
        assert _node.ownerId == 3

    # Check for timeout (if timeout == 0, the test failed)
    if _timeout == 0:
        print printColors.RED + "NOTE: This test involves randomness; try running again." + printColors.RESET
        assert False


# Test resetAfterTurn's targetId/supplierIds updates
def test_resetAfterTurn_targetSupplierIds():
    _map = GameMap(misc_constants.mapFile)
    _map.addPlayer(1)
    _node = _map.getPlayerNodes(1)[0]
    _node.isIPSed = False  # In case the player is assigned this node

    # Test resetting targetId
    assert _node.targeterId is None
    _node.targeterId = 1
    _map.resetAfterTurn()
    assert _node.targeterId is None

    # Test resetting supplierIds
    assert _node.supplierIds == []
    _node.supplierIds = [1]
    _map.resetAfterTurn()
    assert _node.supplierIds == []
