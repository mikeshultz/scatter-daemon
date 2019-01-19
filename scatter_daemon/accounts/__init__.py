""" Functions for operating with secret store files """
from pathlib import Path
from getpass import getpass
from web3 import Web3
from eth_utils import to_normalized_address
from eth_account import Account
from ..common.utils import read_json_file
from ..common.typing import Optional, List, Dict, Tuple, StrOrBytes, PS, to_path
from ..common.logging import getLogger

log = getLogger(__name__)

PRIVATE_KEY: Optional[Tuple[str, bytes]] = None
ACCOUNTS_CACHE: Optional[Dict[str, Dict]] = None


def get_available_accounts(keystore_dir: Path, force: bool = False) -> Dict[str, Dict]:
    """ Get all available accounts from the secret store files in the keystore directory """
    global ACCOUNTS_CACHE

    if force is True or (ACCOUNTS_CACHE is not None and len(ACCOUNTS_CACHE) > 0):
        return ACCOUNTS_CACHE

    keystore_dir = to_path(keystore_dir)

    accounts: Dict[str, Dict] = {}

    for item in keystore_dir.iterdir():

        try:
            jason = read_json_file(item)
        except Exception:
            log.exception("Error reading file.")

        if not jason:
            log.warning("Unable to read JSON from {}".format(item))
        else:
            accounts[Web3.toChecksumAddress(jason['address'])] = jason

    ACCOUNTS_CACHE = accounts

    return ACCOUNTS_CACHE


def read_account_json(keystore_dir: PS, address: StrOrBytes) -> Dict:
    """ Take an account address and try and load the JSON Secret Store file """
    global ACCOUNTS_CACHE

    keystore_dir = to_path(keystore_dir)
    address = str(to_normalized_address(address))

    if ACCOUNTS_CACHE is not None and address in ACCOUNTS_CACHE:
        return ACCOUNTS_CACHE[address]

    available_accounts = get_available_accounts(keystore_dir)

    if address not in available_accounts:
        raise FileNotFoundError("Unable to find account secret store file!")

    ACCOUNTS_CACHE = available_accounts

    return ACCOUNTS_CACHE[address]


def decrypt_account(keystore_dir: PS, address: StrOrBytes,
                    passphrase: Optional[str] = None) -> bytes:
    """ Decrypt the keyfile and return the private key """
    global PRIVATE_KEY

    address = str(to_normalized_address(address))

    if PRIVATE_KEY is not None and PRIVATE_KEY[0] == address:
        return PRIVATE_KEY[1]

    if not passphrase:
        if not passphrase:
            passphrase = getpass("Enter password to decrypt account ({}):".format(
                address
            ))

    account_json = read_account_json(keystore_dir, address)

    eth_account = Account()
    PRIVATE_KEY = (address, eth_account.decrypt(account_json, passphrase))
    return PRIVATE_KEY[1]
