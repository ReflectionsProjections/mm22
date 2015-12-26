package com.mm21;
import org.json.JSONObject;
import org.json.JSONTokener;
import org.json.JSONArray;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.net.Socket;
import java.util.ArrayList;

/**
 * Handles connections to the game server
 * @competitors Do not modify
 */
public class ServerConnection {

    // Connection values
    private static final String SERVER_ADDR = "localhost";
    private static final int SERVER_PORT = 1337;
    private static Socket socket;
    private static OutputStreamWriter writer;
    private static BufferedReader reader;
    private static String TEAM_NAME;

    // Initialize connection to server
    public static int connect(String teamName) throws IOException {

        // Connect to server
        TEAM_NAME = teamName;
        socket = new Socket(SERVER_ADDR, SERVER_PORT);
        writer = new OutputStreamWriter(socket.getOutputStream());
        reader = new BufferedReader(new InputStreamReader(socket.getInputStream()));

        // Send team data
        JSONObject teamData = new JSONObject();
        teamData.put("teamName", TEAM_NAME);
        teamData.write(writer);
        writer.write("\n");
        writer.flush();

        // Return team ID
        JSONObject teamObj = (JSONObject) new JSONTokener(reader.readLine()).nextValue();
        return teamObj.getInt("id");
    }

    // Convert JSON response from game into a Turn object
    public static TurnResult readTurn() throws IOException {

        // Get server response
        String serverResponse = reader.readLine();
        if (serverResponse == null) {
            System.out.println("!!! SERVER DID NOT RESPOND, OR WAS TERMINATED !!!");
        }

        // Get turn JSON
        JSONObject turnJson = (JSONObject) new JSONTokener(serverResponse).nextValue();

        // Convert turn JSON into a Turn object
        TurnResult turnObj = new TurnResult(turnJson);
        return turnObj;
    }

    // Send client's actions to server
    public static void sendTurn(ArrayList<Action> actions) throws IOException {

        // Convert actions to JSON
        JSONArray jsonActions = new JSONArray();
        for (int i = 0; i < actions.size(); i++) {
            JSONObject action = actions.get(i).toJSONObject();
            jsonActions.put(i, action);
        }

        // Send turn JSON
        JSONObject turnJson = new JSONObject();
        turnJson.put("actions", jsonActions);
        turnJson.put("teamName", TEAM_NAME);
        writer.write(turnJson.toString() + "\n");
        writer.flush();
    }
}