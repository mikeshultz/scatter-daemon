# Transaction settings
BLOCK_GAS_LIMIT = int(8e6)
MAX_TX_GAS_LIMIT = int(3e6)
GAS_LIMITS = {  # TODO: Get these accurate once there's accurate estimates
    'Register': {
        'register': MAX_TX_GAS_LIMIT,
    }
}

# Validation Selection Defaults
VALIDATION_DEFAULTS = {
    'min_file_size': 0,
    'max_file_size': 1073741824,  # 1GB
    'min_reward': int(1e9),  # 1 gwei
    'min_duration': 0,
    'max_duration': 2678400,  # 31 days
}

# Default place to locate the configuration file
DEFAULT_CONFIG_PATH = '~/.scatter/daemon.ini'
DEFAULT_KEYSTORE_PATH = '~/.ethereum/keystore'
DEFAULT_DB_FILE = '~/scatter/scatter.db'

# Delays, in seconds, for continually running processes
STD_PROCESS_DELAY = 3
SETTLED_PROCESS_DELAY = 30

MAINNET_ROUTER_ADDRESS = 'TODO'  # TODO: Once deployed on mainnet
