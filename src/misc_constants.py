"""
Holds constants used by the server and visualizer
"""

import os


# Default server port
port = 1337

# Default map
mapFile = "src/gamerunner/map.json"

# Default logfile path
logFile = "src/gamerunner/log.json"

# Default client path
defaultClient = "test-clients/python/"


# Python terminal colors; useful for debugging
# Make sure to concat a "printColors.RESET" to the end of your statement!
class printColors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
