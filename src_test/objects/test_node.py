"""
Tests for the Node object
"""

from src.objects.gamemap import *
from src.objects.game import *
from src.objects.node import *
from src.game_constants import *
import src.misc_constants as misc_constants
import json as JSON
import pytest

"""
misc.
"""


# Debug function
def __prettify(n):
    print sorted([x.id for x in n])


# (Quick n' dirty) no-mans-land filtering helpers
def __cfhRecurse(allNodes, cluster, notCluster, nodeStack, n, i):
    if n in notCluster or n in nodeStack:
        return False
    if n in cluster:
        return True

    ok = False
    if i != 0:
        nodeStack[i] = n
        for n2 in n.getAdjacentNodes():
            if not ok and n2 not in notCluster:
                ok = __cfhRecurse(allNodes, cluster, notCluster, nodeStack, n2, i - 1)
                if ok:
                    break
        nodeStack[i] = None
    
    return ok


def __clusterFilterHelper(allNodes, cluster, notCluster):

    nodeStack = [None] * 13

    for n in allNodes:
        if n not in notCluster and n not in cluster and __cfhRecurse(allNodes, cluster, notCluster, nodeStack, n, 12):
            cluster.append(n)
    print "NC {}".format(notCluster)
    return cluster


# Test toPlayerDict
def test_toPlayerDict():

    _map = GameMap(misc_constants.mapFile)
    _map.addPlayer(1)
    _map.addPlayer(2)
    _node = _map.getPlayerNodes(1)[0]

    # Check value correctness
    _returned = _node.toPlayerDict(False)
    assert _node.id == _returned["id"]
    assert _node.processing == _returned["processingPower"]
    assert _node.networking == _returned["networkingPower"]
    assert _node.ownerId == _returned["owner"]
    #  assert _node.softwareLevel == _returned["softwareLevel"]
    assert _node.isIPSed == _returned["isIPSed"]
    assert _node.infiltration == _returned["infiltration"]
    assert _node.nodetype == _returned["nodetype"]
    assert _node.DDoSed == _returned["isDDoSed"]
    assert _node.upgradeLevel == _returned["upgradeLevel"]
    assert sorted(_node.adjacentIds) == sorted(_returned["adjacentIds"])
    assert sorted(_node.rootkitIds) == sorted(_returned["rootkits"])

    # Check for rootkit hiding
    _node.rootkitIds.append(2)
    assert sorted(_node.toPlayerDict(False)["rootkits"]) == []
    assert sorted(_node.toPlayerDict(True)["rootkits"]) == [2]


"""
decrementPower()
"""


# Test decrementPower with one node
def test_decrementPower_oneNode():

    _map = GameMap(misc_constants.mapFile)
    _map.addPlayer(1)
    _node = _map.getPlayerNodes(1)[0]

    # Test all-at-once deduction
    _node.targeterId = 1
    _node.decrementPower(500, 500, [])
    assert _node.remainingProcessing == 0
    assert _node.remainingNetworking == 0
    _map.resetAfterTurn()

    # Test ordering + multiple deductions
    _node.targeterId = 1
    _node.decrementPower(100, 400, [])
    assert _node.remainingProcessing == 400
    assert _node.remainingNetworking == 100
    _node.decrementPower(400, 100, [])
    assert _node.remainingProcessing == 0
    assert _node.remainingNetworking == 0
    _map.resetAfterTurn()

    # Test single over-deduction + "single power failure"
    # (No deduction should go through)
    _node.targeterId = 1
    with pytest.raises(InsufficientPowerException):
        _node.decrementPower(501, 501, [])
    with pytest.raises(InsufficientPowerException):
        _node.decrementPower(501, 500, [])
    with pytest.raises(InsufficientPowerException):
        _node.decrementPower(500, 501, [])
    assert _node.remainingProcessing == 500
    assert _node.remainingNetworking == 500

    # Test multiple over-deduction
    _node.targeterId = 1
    _node.decrementPower(499, 499, [])
    assert _node.remainingProcessing == 1
    assert _node.remainingNetworking == 1
    with pytest.raises(InsufficientPowerException):
        _node.decrementPower(2, 2, [])
    assert _node.remainingProcessing == 1
    assert _node.remainingNetworking == 1
    _map.resetAfterTurn()


# Test decrementPower with multiple nodes
def test_decrementPower_multiNodes():

    _map = GameMap(misc_constants.mapFile)
    _map.addPlayer(1)
    _node = _map.getPlayerNodes(1)[0]

    # Conquer all nodes adjacent to the base
    _node.targeterId = 1
    for n in _node.getAdjacentNodes():
        n.own(1)
    _nodes = _map.getPlayerNodes(1)
    totalP = sum(x.processing for x in _nodes)
    totalN = sum(x.networking for x in _nodes)

    # Test all-at-once deduction
    _node.targeterId = 1
    _node.decrementPower(totalP, totalN, [])
    for n in _nodes:
        assert n.remainingProcessing == 0
        assert n.remainingNetworking == 0
    _map.resetAfterTurn()

    # Test ordering + multiple deductions
    _node.targeterId = 1
    _node.decrementPower(totalP - 100, 100, [])
    assert sum(x.remainingProcessing for x in _nodes) == 100
    assert sum(x.remainingNetworking for x in _nodes) == totalN - 100
    _node.decrementPower(100, totalN - 100, [])
    for n in _nodes:
        assert n.remainingProcessing == 0
        assert n.remainingNetworking == 0
    _map.resetAfterTurn()

    # Test single over-deduction + "single power failure"
    _node.targeterId = 1
    with pytest.raises(InsufficientPowerException):
        _node.decrementPower(totalP + 1, totalN + 1, [])
    with pytest.raises(InsufficientPowerException):
        _node.decrementPower(totalP + 1, totalN, [])
    with pytest.raises(InsufficientPowerException):
        _node.decrementPower(totalP, totalN + 1, [])
    assert sum(x.remainingNetworking for x in _nodes) == totalN
    assert sum(x.remainingProcessing for x in _nodes) == totalP

    # Test multiple over-deduction
    _node.targeterId = 1
    _node.decrementPower(totalP - 1, totalN - 1, [])
    assert sum(x.remainingNetworking for x in _nodes) == 1
    assert sum(x.remainingProcessing for x in _nodes) == 1
    with pytest.raises(InsufficientPowerException):
        _node.decrementPower(2, 2, [])
    assert sum(x.remainingNetworking for x in _nodes) == 1
    assert sum(x.remainingProcessing for x in _nodes) == 1


# Test decrementPower with negative values
def test_decrementPower_negative():

    _map = GameMap(misc_constants.mapFile)
    _map.addPlayer(1)
    _node = _map.getPlayerNodes(1)[0]

    # Should raise an exception
    _node.targeterId = 1
    with pytest.raises(ValueError):
        _node.decrementPower(-1, 1, [])
    with pytest.raises(ValueError):
        _node.decrementPower(1, -1, [])
    assert _node.remainingProcessing == 500
    assert _node.remainingNetworking == 500


# Test decrementPower with specified supplier IDs
def test_decrementPower_supplierIds():

    _map = GameMap(misc_constants.mapFile)
    _map.addPlayer(1)
    _node = _map.getPlayerNodes(1)[0]
    _neighbors = _node.getAdjacentNodes()
    _node2 = _neighbors[0]
    _node2.own(1)

    # Test normal supplier ID functionality
    _node.targeterId = 1
    _node.decrementPower(_node2.processing + 1, _node2.networking + 1, [_node2.id])
    assert _node2.remainingNetworking == 0
    assert _node2.remainingProcessing == 0
    assert _node.remainingNetworking == 499
    assert _node.remainingProcessing == 499
    _map.resetAfterTurn()

    # Test out-of-range supplier IDs
    with pytest.raises(KeyError):
        _node.targeterId = 1
        _node.decrementPower(1, 1, [-1])

    # Test supplier IDs not connected to an active cluster
    _separateNode = None
    for n in _map.nodes.values():
        _adj = n.getAdjacentNodes()
        if _node in _adj or _node2 in _adj:
            continue
        _separateNode = n
        break
    assert _separateNode is not None
    _separateNode.own(1)
    with pytest.raises(InsufficientPowerException):
        _separateNode.targeterId = 1
        _separateNode.decrementPower(_separateNode.networking + 1, _separateNode.processing + 1, [_node.id, _node2.id, _separateNode.id])
    _map.resetAfterTurn()

    # Test supplier IDs of unowned nodes
    with pytest.raises(InsufficientPowerException):
        _separateNode.targeterId = 1
        _separateNode.decrementPower(_separateNode.networking + 1, _separateNode.processing + 1, _separateNode.adjacentIds)


"""
getClusteredNodes()
"""


# Test one node
def test_getClusteredNodes_oneNode():

    _map = GameMap(misc_constants.mapFile)
    _map.addPlayer(1)
    _node = _map.getPlayerNodes(1)[0]

    _result = []
    _node.getClusteredNodes(_result)
    assert sorted(_result) == sorted(_map.getPlayerNodes(1))


# Test one node cluster
def test_getClusteredNodes_oneCluster():

    _map = GameMap(misc_constants.mapFile)
    _map.addPlayer(1)
    _node = _map.getPlayerNodes(1)[0]

    for n in _node.getAdjacentNodes():
        n.own(1)

    _result = []
    _node.getClusteredNodes(_result)
    assert sorted(_result) == sorted(_map.getPlayerNodes(1))


# Test two separate node clusters
@pytest.mark.skipif(True, reason="TODO @ace-n fix this")
def test_getClusteredNodes_twoClusters():

    _map = GameMap(misc_constants.mapFile)
    _map.addPlayer(1)
    _node = _map.getPlayerNodes(1)[0]

    # -- Build cluster 1 --
    _cluster1 = [_node]
    _cluster1.extend(_node.getAdjacentNodes())
    for n in _node.getAdjacentNodes():
        n.own(1)

    # -- Build no man's land --
    _noMansLand = []
    for n in _cluster1:
        _noMansLand.extend(n.getAdjacentNodes())
    _noMansLand = list(set([x for x in _noMansLand if x.ownerId != 1]))
    for n in _noMansLand:
        n.own(2)

    # -- Build cluster 2 --
    # Part 1: Build cluster
    _notCluster2 = _noMansLand + _cluster1
    _cluster2 = [[x for x in _map.nodes if x not in _notCluster2][0]]
    _cluster2 = __clusterFilterHelper(_map.nodes.values(), _cluster2, _notCluster2)

    # Part 2: owning
    for n in _cluster2:
        _map.nodes[n].own(1)

    # Check cluster sizes
    assert len(_cluster1) > 1
    assert len(_cluster2) > 1

    # Check getClusteredNodes()' correctness
    _result1 = []
    _result2 = []
    _node.getClusteredNodes(_result1)
    _cluster2[0].getClusteredNodes(_result2)
    assert sorted(_cluster1) == sorted(_result1)
    assert sorted(_cluster2) == sorted(_result2)


# Test custom playerId specifier
def test_getClusteredNodes_customPlayerId():

    _map = GameMap(misc_constants.mapFile)
    _map.addPlayer(1)
    _node = _map.getPlayerNodes(1)[0]

    # Find clusters
    _cluster1 = [_node]
    _cluster1.extend(_node.getAdjacentNodes())
    _cluster2 = [n for n in _map.nodes.values() if n not in _cluster1]

    # Assign ownership (cluster 1 - blob based around initial base)
    for n in _node.getAdjacentNodes():
        n.own(1)

    # Make sure cluster shows up correctly depending on player ID
    _result1 = []
    _result2 = []
    _node.getClusteredNodes(_result1)
    _node.getClusteredNodes(_result2, 2)
    assert sorted(_result1) == sorted(_map.getPlayerNodes(1))
    assert len(_result2) == 0


"""
getVisibleNodes()
"""


# Test one node
def test_getVisibleNodes_oneNode():

    _map = GameMap(misc_constants.mapFile)
    _map.addPlayer(1)
    _node = _map.getPlayerNodes(1)[0]

    _expected = [_node]
    _expected.extend(_node.getAdjacentNodes())

    _result = []
    _node.getVisibleNodes(_result)
    assert sorted(_expected) == sorted(_result)


# Test one node cluster
def test_getVisibleNodes_oneCluster():

    _map = GameMap(misc_constants.mapFile)
    _map.addPlayer(1)

    # Construct cluster
    _node = _map.getPlayerNodes(1)[0]
    for n in _node.getAdjacentNodes():
        n.own(1)

    # Determine expected answer
    _expected = [_node]
    _expected.extend(_node.getAdjacentNodes())
    for n in _node.getAdjacentNodes():
        _expected.extend(n.getAdjacentNodes())
    _expected = list(set(_expected))

    # Check expected vs. returned answers
    _returned = []
    _node.getVisibleNodes(_returned)
    assert sorted(_expected) == sorted(_returned)


# Test two separate node clusters
@pytest.mark.skipif(True, reason="TODO @ace-n fix this")
def test_getVisibleNodes_twoClusters():

    _map = GameMap(misc_constants.mapFile)
    _map.addPlayer(1)
    _node = _map.getPlayerNodes(1)[0]

    # -- Build cluster 1 --
    _cluster1 = [_node]
    _cluster1.extend(_node.getAdjacentNodes())
    for n in _node.getAdjacentNodes():
        n.own(1)

    # -- Build no man's land --
    _noMansLand = []
    for n in _cluster1:
        _noMansLand.extend(n.getAdjacentNodes())
    _noMansLand = list(set([x for x in _noMansLand if x.ownerId != 1]))
    for n in _noMansLand:
        n.own(2)

    # -- Build cluster 2 --
    # Part 1: Build cluster
    _notCluster2 = _noMansLand + _cluster1
    _cluster2 = [[x for x in _map.nodes if x not in _notCluster2][0]]
    _cluster2 = __clusterFilterHelper(_map.nodes.values(), _cluster2, _notCluster2)

    # Part 2: owning
    for n in _cluster2:
        _map.nodes[n].own(1)

    # Check cluster sizes
    assert len(_cluster1) > 1
    assert len(_cluster2) > 1

    # Add visible nodes to clusters
    _anchor2 = _cluster2[0]
    _cluster1plus = list(_cluster1)
    _cluster2plus = list(_cluster2)
    for n in _cluster1:
        _cluster1plus.extend(n.getAdjacentNodes())
    for n in _cluster2:
        _cluster2plus.extend(n.getAdjacentNodes())
    _cluster1 = list(set(_cluster1plus))
    _cluster2 = list(set(_cluster2plus))

    # Check getVisibleNodes()' correctness
    _result1 = []
    _result2 = []
    _node.getVisibleNodes(_result1)
    _anchor2.getVisibleNodes(_result2)
    assert sorted(_cluster1) == sorted(_result1)
    assert sorted(_cluster2) == sorted(_result2)


# Test custom playerId specifier
def test_getVisibleNodes_customPlayerId():

    _map = GameMap(misc_constants.mapFile)
    _map.addPlayer(1)
    _node = _map.getPlayerNodes(1)[0]

    _expected = [_node]
    _expected.extend(_node.getAdjacentNodes())
    _visible1 = []
    _visible2 = []
    _node.getVisibleNodes(_visible1)
    _node.getVisibleNodes(_visible2, 2)
    assert sorted(_expected) == sorted(_visible1)
    assert len(_visible2) == 0


# Test two nodes connected by a rootkit chain (1 cluster)
def test_getVisibleNodes_rootkitChain():

    _map = GameMap(misc_constants.mapFile)
    _map.addPlayer(1)

    # Build cluster
    _node = _map.getPlayerNodes(1)[0]
    for n in _node.getAdjacentNodes():
        n.rootkitIds.append(1)

    # Determine expected answer
    _expected = [_node]
    _expected.extend(_node.getAdjacentNodes())
    for n in _node.getAdjacentNodes():
        _expected.extend(n.getAdjacentNodes())
    _expected = list(set(_expected))

    # Check expected vs. returned answers
    _returned = []
    _node.getVisibleNodes(_returned, 1)
    assert sorted(_expected) == sorted(_returned)


# Test two nodes not connected by a rootkit chain (2 clusters)
@pytest.mark.skipif(True, reason="TODO @ace-n fix")
def test_getVisibleNodes_severedRootkitChain():

    _map = GameMap(misc_constants.mapFile)
    _map.addPlayer(1)
    _node = _map.getPlayerNodes(1)[0]

    # -- Build cluster 1 --
    _cluster1 = [_node]
    _cluster1.extend(_node.getAdjacentNodes())
    for n in _node.getAdjacentNodes():
        n.rootkitIds = [1]

    # -- Build no man's land --
    _noMansLand = []
    for n in _cluster1:
        _noMansLand.extend(n.getAdjacentNodes())
    _noMansLand = list(set([x for x in _noMansLand if len(x.rootkitIds) == 0 and x.ownerId != 1]))
    for n in _noMansLand:
        n.rootkitIds = []

    # -- Build cluster 2 --
    # Part 1: Build cluster
    _notCluster2 = _noMansLand + _cluster1
    _cluster2 = [[x for x in _map.nodes if x not in _notCluster2][0]]
    _cluster2 = __clusterFilterHelper(_map.nodes.values(), _cluster2, _notCluster2)

    # Part 2: owning
    for n in _cluster2:
        _map.nodes[n].rootkitIds = [1]

    # Check cluster sizes
    assert len(_cluster1) > 1
    assert len(_cluster2) > 1

    # Add visible nodes to clusters
    _anchor2 = _cluster2[0]
    _cluster1plus = list(_cluster1)
    _cluster2plus = list(_cluster2)
    for n in _cluster1:
        _cluster1plus.extend(n.getAdjacentNodes())
    for n in _cluster2:
        _cluster2plus.extend(n.getAdjacentNodes())
    _cluster1 = list(set(_cluster1plus))
    _cluster2 = list(set(_cluster2plus))

    # Check getVisibleNodes()' correctness
    _result1 = []
    _result2 = []
    _node.getVisibleNodes(_result1, 1)
    _anchor2.getVisibleNodes(_result2, 1)
    print _anchor2.id
    __prettify(_noMansLand)
    __prettify(_cluster2)
    __prettify(_result2)
    assert sorted(_cluster1) == sorted(_result1)
    assert sorted(_cluster2) == sorted(_result2)

"""
more misc.
"""


# Test canMoveThrough
def test_canMoveThrough():

    _map = GameMap(misc_constants.mapFile)
    _map.addPlayer(1)
    _node = _map.getPlayerNodes(1)[0]

    # Test unowned node
    _unownedNode = _node.getAdjacentNodes()[0]
    assert _unownedNode.canMoveThrough(1) is False

    # Test owned node
    assert _node.canMoveThrough(1) is True

    # Test rootkitted node
    _unownedNode.rootkitIds.append(1)
    assert _node.canMoveThrough(1) is True

    # Test custom playerID specifier
    assert _node.canMoveThrough(2) is False


# Test own
def test_own():

    _map = GameMap(misc_constants.mapFile)
    _map.addPlayer(1)
    _node = _map.getPlayerNodes(1)[0]

    # Test owning an unowned node
    _unownedNode = _node.getAdjacentNodes()[0]
    _unownedNode.own(1)
    assert _unownedNode.ownerId == 1

    # Test that owning an already-owned node throws an exception
    with pytest.raises(ActionOwnershipException):
        _node.own(1)

    # Test resetting of isIPSed/rootkits/infiltration
    _unownedNode.own(0)
    assert _unownedNode.ownerId == 0
    _unownedNode.isIPSed = True
    _unownedNode.rootkitIds.append(1)
    _unownedNode.infiltration[1] = 999
    _unownedNode.own(1)
    assert _unownedNode.isIPSed is False
    assert len(_unownedNode.rootkitIds) == 0
    assert _unownedNode.infiltration[1] == 0


"""
Per-node action criteria
"""


# Test requireNotDDoSed
def test_requireNotDDoSed():

    _map = GameMap(misc_constants.mapFile)
    _map.addPlayer(1)
    _node = _map.getPlayerNodes(1)[0]

    _node.requireNotDDoSed("")
    _node.DDoSed = True
    with pytest.raises(NodeIsDDoSedException):
        _node.requireNotDDoSed("")


# Test requireOwned
def test_requireOwned():

    _map = GameMap(misc_constants.mapFile)
    _map.addPlayer(1)
    _node = _map.getPlayerNodes(1)[0]

    _node.targeterId = 1
    _node.requireOwned()
    with pytest.raises(ActionOwnershipException):
        _other = _node.getAdjacentNodes()[0]
        _other.targeterId = 1
        _other.requireOwned()


# Test requireNotOwned
def test_requireNotOwned():

    _map = GameMap(misc_constants.mapFile)
    _map.addPlayer(1)
    _node = _map.getPlayerNodes(1)[0]

    _other = _node.getAdjacentNodes()[0]
    _other.targeterId = 1
    _other.requireNotOwned()
    with pytest.raises(ActionOwnershipException):
        _node.targeterId = 1
        _node.requireNotOwned()


# Test requireNotIPSed
def test_requireNotIPSed():

    _map = GameMap(misc_constants.mapFile)
    _map.addPlayer(1)
    _node = _map.getPlayerNodes(1)[0]

    _target = _node.getAdjacentNodes()[0]
    _target.requireNotIPSed()
    _target.isIPSed = True
    with pytest.raises(IpsPreventsActionException):
        _target.requireNotIPSed()


"""
Player actions
"""


# Test doControl in attacking mode
def test_doControl_attack():

    _map = GameMap(misc_constants.mapFile)
    _map.addPlayer(1)
    _node = _map.getPlayerNodes(1)[0]

    _target = _node.getAdjacentNodes()[0]
    _target.own(2)
    _target.targeterId = 1

    # Test attacking without multiplier
    assert _target.infiltration[1] == 0
    _target.doControl()
    assert _target.infiltration[1] == 1

    # Test attacking with multiplier
    _target.doControl(9)
    assert _target.infiltration[1] == 10


# Test doControl in healing mode
def test_doControl_heal():

    _map = GameMap(misc_constants.mapFile)
    _map.addPlayer(1)
    _map.addPlayer(2)
    _node = _map.getPlayerNodes(1)[0]

    _target = [x for x in _node.getAdjacentNodes() if "City" in x.nodetype][0]
    _target.isIPSed = False
    if _target.ownerId != 2:
        _target.own(2)
    _target.targeterId = 1
    _target.doControl(5)
    assert _target.infiltration[1] == 5

    # Test healing a damaged node without multiplier
    _target.targeterId = 2
    _target.doControl()
    assert _target.infiltration[1] == 4

    # Test overhealing a damaged node with multiplier
    # (Should reduce initially, then reset)
    _target.doControl(5)
    assert _target.infiltration[1] == -1
    _map.resetAfterTurn()
    assert _target.infiltration[1] == 0

    # Test overhealing a fully-healed node without multiplier
    _target.targeterId = 2
    _target.doControl()
    assert _target.infiltration[1] == -1
    _map.resetAfterTurn()
    assert _target.infiltration[1] == 0


# Test doDDoS
def test_doDDoS():

    _map = GameMap(misc_constants.mapFile)
    _map.addPlayer(1)
    _node = _map.getPlayerNodes(1)[0]

    # Test on 1) owned node, and 2) unowned node
    _node.isIPSed = False
    for _target in [_node, _node.getAdjacentNodes()[0]]:
        _target.targeterId = 1
        _target.doDDoS()
        assert _target.DDoSPending is True
        _map.resetAfterTurn()
        assert _target.DDoSed is True
        assert _target.remainingProcessing == 0
        assert _target.remainingNetworking == 0
        _map.resetAfterTurn()

    # Test that DDoSing prevents actions
    _node.targeterId = 1
    _node.doDDoS()
    _map.resetAfterTurn()
    with pytest.raises(InsufficientPowerException):
        _node.targeterId = 1
        _node.doDDoS()
    assert _node.DDoSPending is False

    # Test that double-DDoSing DOES NOT raise an exception
    # If it did, players would know whether someone else was DDoSing their DDoS target
    _map.resetAfterTurn()
    _node.targeterId = 1
    _node.doDDoS()
    _node.doDDoS()


# Test doDDoS interrupted by doControl
def test_doDDoS_controlInterrupt():

    _map = GameMap(misc_constants.mapFile)
    _map.addPlayer(1)
    _map.addPlayer(2)
    _node = _map.getPlayerNodes(1)[0]
    _node.isIPSed = False

    # Initialize _attacker
    _attacker = _node.getAdjacentNodes()[0]
    _attacker.remainingProcessing = 99999
    _attacker.remainingNetworking = 99999
    if _attacker.ownerId != 2:
        _attacker.own(2)

    # Attempt DDoS
    _node.targeterId = 2
    _node.doDDoS()
    assert _node.DDoSPending is True

    # Interrupt DDoS with control
    _node.doControl(9999)
    _map.resetAfterTurn()
    assert _node.ownerId == 2
    assert _node.DDoSPending is False
    assert _node.DDoSed is False


# Test that actions conform to DDoSing restrictions (as described on the Wiki)
def test_actionConformityToDDoS():

    _map = GameMap(misc_constants.mapFile)
    _map.addPlayer(1)
    _node = _map.getPlayerNodes(1)[0]
    _node.isIPSed = False
    _node2 = _node.getAdjacentNodes()[0]
    _node2.own(1)

    # Initialization pt 2
    _node.targeterId = 1
    _node.doDDoS()
    _map.resetAfterTurn()
    _node2.remainingProcessing = 9999
    _node2.remainingNetworking = 9999
    _node.targeterId = 1

    # Clean
    with pytest.raises(NodeIsDDoSedException):
        _node.doClean()

    # Control
    with pytest.raises(NodeIsDDoSedException):
        _node.doControl(1)

    # Port scan
    with pytest.raises(NodeIsDDoSedException):
        _node.doPortScan()

    # Rootkit
    with pytest.raises(NodeIsDDoSedException):
        _node.doRootkit()

    # Scan
    with pytest.raises(NodeIsDDoSedException):
        _node.doScan()

    # Upgrade
    with pytest.raises(NodeIsDDoSedException):
        _node.doUpgrade()

    # Check that no resources were consumed
    assert _node2.remainingNetworking == 9999
    assert _node2.remainingProcessing == 9999

    # IPS (should go through)
    _node.doIPS()
    assert _node.IPSPending is True

    # DDoS (should go through)
    _node.doDDoS()
    assert _node.DDoSPending is True


# Test doUpgrade
def test_doUpgrade():

    _map = GameMap(misc_constants.mapFile)
    _map.addPlayer(1)
    _node = _map.getPlayerNodes(1)[0]

    # Test upgrading a node
    assert _node.upgradeLevel == 0
    _node.targeterId = 1
    _node.doUpgrade()
    assert _node.upgradeLevel == 0
    assert _node.initialProcessing == _node.processing
    assert _node.initialNetworking == _node.networking
    assert _node.upgradePending is True
    _map.resetAfterTurn()
    assert _node.upgradePending is False
    assert _node.upgradeLevel == 1

    # Test stats of upgraded node
    assert _node.processing == 1.1 * _node.initialProcessing
    assert _node.networking == 1.1 * _node.initialNetworking
    assert _node.totalPower == _node.processing + _node.networking

    # Test stats after DDoS (to make sure they're re-initialized correctly)
    _node.DDoSPending = True
    _map.resetAfterTurn()
    _map.resetAfterTurn()
    assert _node.processing == 1.1 * _node.initialProcessing
    assert _node.networking == 1.1 * _node.initialNetworking
    assert _node.processing == _node.remainingProcessing
    assert _node.networking == _node.remainingNetworking
    _map.resetAfterTurn()

    # Test upgrading nodes a second time
    _node.targeterId = 1
    _node.doUpgrade()
    _map.resetAfterTurn()
    assert _node.upgradeLevel == 2
    assert _node.processing == 1.2 * _node.initialProcessing
    assert _node.networking == 1.2 * _node.initialNetworking
    assert _node.totalPower == _node.processing + _node.networking
    assert _node.processing == _node.remainingProcessing
    assert _node.networking == _node.remainingNetworking

    # Test upgrading a node multiple times per turn
    _node.upgradePending = True
    with pytest.raises(RepeatedActionException):
        _node.targeterId = 1
        _node.doUpgrade()


# Test doUpgrade interrupted by doControl
def test_doUpgrade_controlInterrupt():

    _map = GameMap(misc_constants.mapFile)
    _map.addPlayer(1)
    _map.addPlayer(2)
    _node = _map.getPlayerNodes(1)[0]
    _node.isIPSed = False

    # Init _attacker
    _attacker = _node.getAdjacentNodes()[0]
    if _attacker.ownerId != 2:
        _attacker.own(2)
    _attacker.remainingProcessing = 99999
    _attacker.remainingNetworking = 99999

    # Do upgrade on initial node, then interrupt it
    # The upgrade should go through
    _node.targeterId = 1
    _node.doUpgrade()
    assert _node.upgradePending is True
    _node.targeterId = 2
    _node.doControl(9999)
    _map.resetAfterTurn()

    # Check values
    assert _node.upgradeLevel == 1
    assert _node.ownerId == 2
    assert _node.upgradePending is False


# Test that doUpgrade() increases the maximum infiltration of a node

    _map = GameMap(misc_constants.mapFile)
    _map.addPlayer(1)
    _map.addPlayer(2)
    _node = _map.getPlayerNodes(1)[0]
    _node.isIPSed = False

    # Upgrade _node several times
    for i in range(500):
        _node.targeterId = 1
        _node.doUpgrade()
        _map.resetAfterTurn()

    # Init _attacker
    _attacker = _node.getAdjacentNodes()[0]
    if _attacker.ownerId != 2:
        _attacker.own(2)
    _attacker.remainingProcessing = 99999
    _attacker.remainingNetworking = 99999

    # Attempt to take over _node
    _node.targeterId = 2
    _node.doControl(5000)  # Will control any un-upgraded node
    _map.resetAfterTurn()
    assert _node.ownerId == 1  # Node should not change hands


# Test doClean
def test_doClean():

    _map = GameMap(misc_constants.mapFile)
    _map.addPlayer(1)
    _map.addPlayer(2)
    _node = _map.getPlayerNodes(1)[0]

    _node.rootkitIds.append(2)
    assert len(_node.rootkitIds) == 1
    _node.targeterId = 1
    _node.doClean()
    assert len(_node.rootkitIds) == 1
    assert _node.cleanPending is True

    _map.resetAfterTurn()
    assert _node.rootkitIds == []
    assert _node.cleanPending is False


# Test doClean colliding with doRootkit
# The rootkit should ultimately be removed
def test_doClean_collideWithRootkit():

    _map = GameMap(misc_constants.mapFile)
    _map.addPlayer(1)
    _map.addPlayer(2)
    _node = _map.getPlayerNodes(1)[0] 

    _node.isIPSed = False

    # Give player 2 an attacking node
    _node2 = _node.getAdjacentNodes()[0]
    if _node2.ownerId != 2:
        _node2.own(2)
    _node2.remainingProcessing = 999
    _node2.remainingNetworking = 999

    assert _node.rootkitIds == []
    assert _node.cleanPending is False
    _node.targeterId = 1
    _node.doClean()
    _node.targeterId = 2
    _node.doRootkit()
    assert _node.rootkitIds == [2]
    assert _node.cleanPending is True

    _map.resetAfterTurn()
    assert _node.rootkitIds == []
    assert _node.cleanPending is False


# Test doScan
def test_doScan():

    _map = GameMap(misc_constants.mapFile)
    _map.addPlayer(1)
    _map.addPlayer(2)
    _node = _map.getPlayerNodes(1)[0]

    assert _node.scanPending is False
    _node.targeterId = 1
    _node.doScan()
    assert _node.scanPending is True
    _map.resetAfterTurn()
    assert _node.scanPending is False


# Test doRootkit
def test_doRootkit():

    _map = GameMap(misc_constants.mapFile)
    _map.addPlayer(1)
    _node = _map.getPlayerNodes(1)[0]

    _target = _node.getAdjacentNodes()[0]
    assert len(_target.rootkitIds) == 0
    _target.targeterId = 1
    _target.doRootkit()
    assert _target.rootkitIds == [1]


# Test doIPS
def test_doIPS():
 
    _map = GameMap(misc_constants.mapFile)
    _map.addPlayer(1)
    _node = _map.getPlayerNodes(1)[0]

    # Init
    _node.isIPSed = False
    _node.targeterId = 1

    # Test IPS-pending
    assert _node.isIPSed is False
    _node.doIPS()
    assert _node.IPSPending is True
    _map.resetAfterTurn()

    # Test IPS-active
    assert _node.isIPSed is True
    _map.resetAfterTurn()
    assert _node.isIPSed is True


# Test doIPS interrupted by doControl
def test_doIPS_controlInterrupt():

    _map = GameMap(misc_constants.mapFile)
    _map.addPlayer(1)
    _map.addPlayer(2)
    _node = _map.getPlayerNodes(1)[0]

    # Move IPS
    _node2 = [x for x in _map.nodes.values() if x.ownerId == -1][0]
    _node2.own(1)
    _node2.targeterId = 1
    _node2.doIPS()
    _map.resetAfterTurn()
    assert _node.isIPSed is False

    # Super-charge attacker
    _attacker = [x for x in _node.getAdjacentNodes() if x.ownerId != 1][0]
    if _attacker.ownerId != 2:
        _attacker.own(2)
    _attacker.remainingProcessing = 99999
    _attacker.remainingNetworking = 99999

    # Attempt IPS
    _node.targeterId = 1
    _node.doIPS()

    # Interrupt IPS with control
    _node.targeterId = 2
    _node.doControl(9999)
    _map.resetAfterTurn()

    # IPS should fail, and control should go through
    assert _node.isIPSed is False
    assert _node.IPSPending is False
    assert _node.ownerId == 2


# Test doPortScan
# TODO Write a test that checks for this in server response
def test_doPortScan_gameLogic():

    _map = GameMap(misc_constants.mapFile)
    _map.addPlayer(1)
    _node = _map.getPlayerNodes(1)[0]
    _node2 = _node.getAdjacentNodes()[0]
    _node2.own(1)

    # Test doing a port scan
    assert len(_map.portScans) == 0
    _node.targeterId = 1
    _node.doPortScan()
    assert _map.portScans == [1]
    _map.resetAfterTurn()
    assert len(_map.portScans) == 0

    # Test that multiple port-scan requests are rejected
    _node.targeterId = 1
    _node2.targeterId = 1
    _node.doPortScan()
    with pytest.raises(RepeatedActionException):
        _node2.doPortScan()


# Test that actions conform to ownership restrictions (as described on the Wiki)
def test_actionConformityToOwnership():

    _map = GameMap(misc_constants.mapFile)
    _map.addPlayer(1)
    _map.addPlayer(2)
    _node = _map.getPlayerNodes(1)[0]
    _oNode = _node.getAdjacentNodes()[0]

    # Initialize nodes
    if _oNode.ownerId != 2:
        _oNode.own(2)
    for x in [_node, _oNode]:
        x.remainingNetworking = 99999
        x.remainingProcessing = 99999
        x.targeterId = 1
        x.isIPSed = False

    # Clean
    _node.doClean()
    with pytest.raises(ActionOwnershipException):
        _oNode.doClean()

    # Control
    _node.doControl(1)
    _oNode.doControl(1)

    # DDoS
    for x in [_node, _oNode]:
        x.doDDoS()
        assert x.DDoSPending is True

    # IPS
    _node.doIPS()
    assert _node.IPSPending is True
    with pytest.raises(ActionOwnershipException):
        _oNode.doIPS()
    assert _oNode.IPSPending is False

    # Port scan
    _node.doPortScan()
    with pytest.raises(ActionOwnershipException):
        _oNode.doPortScan()

    # Rootkit
    with pytest.raises(ActionOwnershipException):
        _node.doRootkit()
    _oNode.doRootkit()

    # Scan
    _node.doScan()
    with pytest.raises(ActionOwnershipException):
        _oNode.doScan()

    # Upgrade
    _node.doUpgrade()
    with pytest.raises(ActionOwnershipException):
        _oNode.doUpgrade()
