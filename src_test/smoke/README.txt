This file contains high-level smoke tests for Mechmania 21.
There are two classes of smoke tests: Game tests (for the game itself), and Client tests (for the sample testclients)

Game tests function as follows:
1) A test client executes a certain predefined set of actions against the server
2) The test client outputs what it receives to a file (the "current answer")
3) That file is compared with a known-correct client response (the "correct answer")
4) The test passes if the correct answer and the current answer are the same

Client tests function as follows:
1) All test clients execute a certain set of actions (predefined or otherwise) against the server
2) Their outputs are dumped to files
3) The test passes if all the output files are identical.
