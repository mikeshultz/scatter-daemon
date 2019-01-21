""" Handle functionality around the Register contract """
import json
import ipfsapi
from pathlib import Path
from eth_utils import remove_0x_prefix
from web3.eth import Contract
from multihash import from_hex_string, to_b58_string
from jsonschema import validate as validate_json
from jsonschema.exceptions import SchemaError, ValidationError
from ..common.ipfs import ipfs_get_json
from ..common.typing import Optional, Any, Dict
from ..common.logging import getLogger

log = getLogger(__name__)

registration_cache: Dict = {}
schema_cache: Dict[str, Dict] = {}


def load_registration_schema(version='0.1') -> Dict[str, Any]:
    """ Load the Registration JSON schema """

    if schema_cache.get(version) is not None:
        return schema_cache[version]

    schema_file = Path(__file__).parent.parent.joinpath('common', 'files',
                                                        'registration-{}.schema.json')
    schema_string: str = ''
    with schema_file.open() as _file:
        schema_string = _file.read()

    if not schema_string:
        raise ValueError('Schema file empty')

    schema_object: Dict = {}
    try:
        schema_object = json.loads(schema_string)
    except json.JSONDecodeError as err:
        log.exception("Registration file invalid")
        raise err

    return schema_object


def get_registration(ipfs: ipfsapi.client.Client, register: Contract,
                     address: str) -> Optional[Dict[str, Any]]:
    """ Retrieve a user's registration """
    global registration_cache

    hex_hash = register.functions.getUserFile(address).call()
    user_json = ipfs_get_json(ipfs, hex_hash)

    schema = load_registration_schema()
    try:
        validate_json(user_json, schema)
    except SchemaError as err:
        log.error("Error validation Registration schema.  Invalid schema.")
        raise err
    except ValidationError as err:
        log.exception("Invalid Registration schema.")
        return None

    return user_json
