# Python imports
import pickle
import os

# Project imports
from util.util import generate_path


def load(file, root_path, default=None, dirs=list()):
    """
    Load object from file using pickle

    @type file: str
    @param file: file's name to load the object from

    @type root_path: str
    @param root_path: path to start from

    @type default: object
    @param default: if file doesn't exist or pickle failed its loading, return this value

    @type dirs: list
    @param dirs: extra directories between the root path and the file name

    @rtype: object
    @return: the object loaded from the file or the default object
    """
    dirs = ['temp'] + dirs
    file = generate_path(root_path, file, dirs)

    try:
        with open(file, 'rb') as f:
            ret = pickle.load(f)
        os.remove(file)
        return ret
    except:
        return default


def save(obj, file, root_path, dirs=list()):
    """
    Save object to file using pickle

    @type obj: object
    @param obj: the object to save to the file

    @type file: str
    @param file: file's name to save the object to

    @type root_path: str
    @param root_path: path to start from

    @type dirs: list
    @param dirs: extra directories between the root path and the file name
    """
    dirs = ['temp'] + dirs
    file = generate_path(root_path, file, dirs, make_dirs=True)

    try:
        with open(file, 'wb') as f:
            pickle.dump(obj, f)
    except:
        print('Could not save {file}'.format(
            file=file
        ))