""" functions to handle configuration
"""
from configparser import ConfigParser, NoOptionError
from pathlib import Path
from eth_utils import is_address, to_checksum_address
from .typing import (
    to_path,
    to_account,
    Optional,
    PS,
    StrOrBytes,
    Any,
)
from .exceptions import ConfigurationError
from .const import VALIDATION_DEFAULTS, DEFAULT_CONFIG_PATH, MAINNET_ROUTER_ADDRESS
from .logging import getLogger

log = getLogger(__name__)

CONFIG = None
LOADED_FILE = None
ROOT_EL = 'scatter'
VALIDATOR_EL = 'validator'


def initial_config_structure(parser, overrides={}) -> None:
    """ Create a configuration structure from scratch using the provided ConfigParser """
    parser.add_section(ROOT_EL)
    parser.set(ROOT_EL, 'account', overrides.get('account', ''))
    parser.set(ROOT_EL, 'router_address', overrides.get('router', MAINNET_ROUTER_ADDRESS))
    parser.set(ROOT_EL, 'db_file', overrides.get('db_file', '~/.scatter/scatter.db'))
    parser.set(ROOT_EL, 'db_file', overrides.get('db_file', '~/.scatter/scatter.db'))

    parser.add_section(VALIDATOR_EL)
    parser.set(ROOT_EL, 'max_file_size', overrides.get(
        'max_file_size',
        str(VALIDATION_DEFAULTS.get('max_file_size'))
    ))


def init_config(_file: PS, account: StrOrBytes) -> Path:
    """ Initialize the daemon's config file """
    global LOADED_FILE, CONFIG

    if not is_address(account):
        raise ConfigurationError("Invalid account provided.")

    _file = to_path(_file)
    account = to_account(account)

    CONFIG = ConfigParser()
    CONFIG.read(_file)
    if len(CONFIG.sections()) > 0:
        raise ConfigurationError("Config exists!  Aborting...")

    # Get the default config options
    initial_config_structure(CONFIG)

    # Set the account
    CONFIG.set(ROOT_EL, 'account', account)

    with _file.open('w') as _config_fh:
        log.info("Writing new configuration...")
        CONFIG.write(_config_fh)

    LOADED_FILE = _file

    log.debug("New configuration saved to {}.".format(_file))

    return _file


def load_config(_file: PS) -> ConfigParser:
    """ Load a configuration file and return ConfigParser instance """
    global LOADED_FILE, CONFIG

    _file = to_path(_file)

    if CONFIG is not None and _file == LOADED_FILE:
        return CONFIG

    CONFIG = ConfigParser()
    CONFIG.read(_file)
    LOADED_FILE = _file
    return CONFIG


def config_get(conf: ConfigParser, key: str, default: Optional[Any] = None,
               section: Optional[str] = None) -> Optional[str]:
    """ Return a value or None from a ConfigParser instance """
    try:
        return conf.get(section or ROOT_EL, key)
    except NoOptionError:
        return default
