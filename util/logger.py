# Python imports
import sys

# Project imports
from manager.Log import Log
from configs import store


def init():
    sys.stdout = Log(store['configs']['log_directory'], 'console')
    sys.stderr = sys.stdout