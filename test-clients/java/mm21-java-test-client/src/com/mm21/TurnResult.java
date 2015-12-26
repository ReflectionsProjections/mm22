package com.mm21;

import org.json.JSONArray;
import org.json.JSONObject;
import java.util.HashMap;

/**
 * Represents the results of a game turn
 * @competitors You may modify this file, but you shouldn't need to
 */
public class TurnResult {

    // Property values (private to prevent unintentional writing)
    private HashMap<Integer, Node> m_nodes;
    private ActionResult[] m_actionResults;

    // Property getters
    public HashMap<Integer, Node> nodes() { return m_nodes; }
    public ActionResult[] actionResults() { return m_actionResults; }

    // Constructor
    public TurnResult(JSONObject serverResponse) {

        // Serialize map
        JSONArray mapNodes = serverResponse.getJSONArray("map");
        this.m_nodes = new HashMap<Integer, Node>();
        for (int i = 0; i < mapNodes.length(); i++) {
            JSONObject o = mapNodes.getJSONObject(i);
            this.m_nodes.put(o.getInt("id"), new Node(o));
        }

        // Initialize adjacent nodes
        for (int i = 0; i < mapNodes.length(); i++) {
            JSONObject o = mapNodes.getJSONObject(i);
            this.m_nodes.get(o.getInt("id")).initAdjacentNodes(this.m_nodes, o);
        }

        // Serialize action results
        JSONArray actionResults = serverResponse.getJSONArray("turnResult");
        this.m_actionResults = new ActionResult[actionResults.length()];
        for (int i = 0; i < actionResults.length(); i++) {
            JSONObject o = actionResults.getJSONObject(i);
            this.m_actionResults[i] = new ActionResult(o);
        }

        // Initialize power source nodes
        for (int i = 0; i < actionResults.length(); i++) {
            JSONObject o = actionResults.getJSONObject(i);
            if (o.has("powerSources")) {
                this.m_actionResults[i].initPowerSourceNodes(this.m_nodes, o);
            }
        }
    }
}
