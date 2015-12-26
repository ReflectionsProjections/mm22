package com.mm21;

import org.json.JSONArray;
import org.json.JSONObject;
import java.util.ArrayList;

/**
 * Represents a single turn of the game
 * @competitors You may modify this file, but you shouldn't need to
 */
public class Action {

    // Action types
    public enum ActionType { CLEAN, CONTROL, DDOS, IPS, PORTSCAN, ROOTKIT, SCAN, UPGRADE }

    // Property values (feel free to write to these, unless it's an ActionResult)
    public int multiplier = 1;
    public int targetId;
    public ActionType actionType;
    public ArrayList<Node> supplierNodes = new ArrayList<Node>(); // The list of nodes to draw resources from first

    // Constructor
    public Action(ActionType p_actionType, int p_multiplier, int p_targetId) {
        multiplier = p_multiplier;
        targetId = p_targetId;
        actionType = p_actionType;
    }

    // Convert to JSON object
    public JSONObject toJSONObject() {

        JSONObject o = new JSONObject();

        // Simple properties
        o.put("action", this.actionType.toString());
        o.put("multiplier", this.multiplier);
        o.put("target", this.targetId);

        // Complex property #1 (Supplier IDs)
        JSONArray supplierIds = new JSONArray();
        for (Node n: supplierNodes) {
            supplierIds.put(n.id());
        }
        o.put("supplierIds", supplierIds);

        // Done!
        return o;
    }
}
