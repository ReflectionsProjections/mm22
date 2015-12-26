package com.mm21;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;

/**
 * A file containing a competitor's AI
 * @competitors Modify this file to your heart's content, including the helper functions
 */
public class AI {

    // Global test client variables
    // @competitors Put your global/between-turn variables here
    public static int MY_PLAYER_ID = -1; // Your client's player ID; initialized in Main.java
    public static int homeBaseId = -1;

    // Determine what actions to do, given the server response
    public static ArrayList<Action> processTurn(TurnResult result) {

        // List of actions to execute
        ArrayList<Action> actions = new ArrayList<Action>();

        // Compute actions
        // @competitors reject our AI and substitute your own.
        HashMap<Integer, Node> allNodes = result.nodes();
        HashMap<Integer, Node> myNodes = filterMyNodes(allNodes);

        // Keep track of home base
        if (homeBaseId == -1) { homeBaseId = ((Node) myNodes.values().toArray()[0]).id(); }
        Node homeBase = allNodes.get(homeBaseId);

        // Upgrade our home base until it has 10000 power
        if (homeBase.networking() < 1000) {
            Action a = homeBase.doUpgrade();
            actions.add(a);
        }

        // If our core node has been fully upgraded, start capturing things
        else {
            HashSet<Node> attackedNodes = new HashSet<Node>(); // Used to prevent duplicate nodes
            for (Node n : myNodes.values()) {

                // Attempt to infiltrate nearby nodes
                HashMap<Integer, Node> adjNodes = filterOthersNodes(n.adjacentNodes());
                if (adjNodes.keySet().size() != 0) {
                    for (Node target : adjNodes.values()) {
                        if (!attackedNodes.contains(target)) {
                            Action a = target.doRootkit(); //.doControl(target.totalPower());
                            actions.add(a);
                            attackedNodes.add(target);
                        }
                    }
                }
            }
        }

        // Done!
        return actions;
    }

    // Helper function to remove nodes you own from a node list
    private static HashMap<Integer, Node> filterMyNodes(HashMap<Integer, Node> inNodes) {
        return filterNodesByOwner(inNodes, MY_PLAYER_ID);
    }

    // Helper function to filter nodes you don't own from a node list
    private static HashMap<Integer, Node> filterOthersNodes(HashMap<Integer, Node> inNodes) {
        HashMap<Integer, Node> outNodes = new HashMap<Integer, Node>();
        for (Node n : inNodes.values()) {
            if (n != null && n.ownerId() != MY_PLAYER_ID) { outNodes.put(n.id(), n); }
        }
        return outNodes;
    }

    // Helper function to filter a node list by player ID
    private static HashMap<Integer, Node> filterNodesByOwner(HashMap<Integer, Node> inNodes, int playerId) {
        HashMap<Integer, Node> outNodes = new HashMap<Integer, Node>();
        for (Node n : inNodes.values()) {
            if (n != null && n.ownerId() == playerId) { outNodes.put(n.id(), n); }
        }
        return outNodes;
    }
}
