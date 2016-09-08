# Python imports
import os
import sys

# Project imports
from util import logger
from util.animate import animate

logger.init()

PYTHON_COMPILER = sys.executable
SCRIPT_PATH = sys.argv[0]

try:
    animate()
except:
    if len(sys.argv) != 1:
        raise

while len(sys.argv) == 1:
    try:
        os.system(PYTHON_COMPILER + ' ' + SCRIPT_PATH + ' arg')
    except:
        pass
