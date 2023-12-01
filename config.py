
import os
from dotenv import load_dotenv


def parse_env_boolean(env_var):
    """
    Get a boolean value passed by an environmental variable
    :param env_var:
    :return:
    """
    if isinstance(env_var, str):
        env_var = env_var.strip()
    if env_var in (0, '0', 'false', 'False', False):
        return False
    if env_var in (1, '1', 'true', 'True', True):
        return True


class Config(object):
    # Load dotenv credentials if specified and available
    if os.path.isfile('.env'):
        load_dotenv('.env')
    DATE_STR_FORMAT = "%Y_%m_%d-%H_%M_%S"
    DATE_STR_PRINT = "%A %B %d, %Y"
    ENV = os.environ.get("ENV", "testing")
    DEBUG_MODE = parse_env_boolean(os.environ.get("DEBUG_MODE", False))
    IS_VERBOSE = parse_env_boolean(os.environ.get("IS_VERBOSE", True))
    COM_PORT = os.environ.get("COM_PORT", 'COM3')
    BAURDRATE = os.environ.get("BAURDRATE", 115200)
    EXERCISE_CSV_FPATH = os.environ.get('EXERCISE_CSV_FPATH', './data/exercises.tsv')
    SOUND_TRUMPET_FPATH = os.environ.get('EXERCISE_CSV_FPATH', './data/sounds/the-price-is-right-losing-horn.mp3')
