package com.mm21;

import java.io.IOException;
import java.util.ArrayList;

/**
 * The entry-point class of the test client
 * @competitors Add your team name, but don't modify anything else
 * @competitors Your AI itself should go in AI.java
 */

public class Main {

    // @competitors Modify me
    private static final String TEAM_NAME = "YOUR_TEAM_NAME_HERE";
    private static final boolean DEBUG_CONNECTION = false;
    private static int TEAM_ID; // Assigned by the server

    /**
     * Run the game
     * @competitors Do not modify
     */
    public static void main(String[] args) {

        // Connect
        if (DEBUG_CONNECTION)
            System.out.println("Connecting to server...");
        try {
            AI.MY_PLAYER_ID = ServerConnection.connect(TEAM_NAME);
        } catch (IOException e) {
            System.out.println("!!! CONNECTION FAILED !!!");
            e.printStackTrace(System.out);
        }
        if (DEBUG_CONNECTION)
            System.out.println("Successfully connected to server.");

        // Main game loop
        boolean gameOver = false;
        int turnCounter = 1;
        while (!gameOver) {
            try {

                // Execute turn
                // @competitors DO NOT PUT YOUR AI HERE - use AI.java instead!
                TurnResult serverResponse = ServerConnection.readTurn();
                ArrayList<Action> clientActions = AI.processTurn(serverResponse);
                ServerConnection.sendTurn(clientActions);
                if (DEBUG_CONNECTION)
                    System.out.println("Turn sent...");

                // Update variables
                turnCounter++;

            } catch (IOException e) {
                System.out.println("!!! ERROR, SEE BELOW !!!");
                e.printStackTrace(System.out);
            }
        }
    }
}
