""" Functions for creating Web3 contract instances """
import json
from pathlib import Path
from hexbytes import HexBytes
from web3 import Web3
from web3.eth import Contract
from web3.datastructures import AttributeDict
from eth_abi import decode_abi, decode_single
from eth_utils import add_0x_prefix
from attrdict import AttrDict
from .typing import (
    to_account,
    Collection,
    StrOrBytes,
    Dict,
    Tuple,
    List,
    Any,
)
from .utils import safe_slice
from .logging import getLogger

log = getLogger(__name__)

THIS_DIR: Path = Path(__file__).parent
ABI_CACHE: Dict[str, Dict] = {}
ABI_FILE_DIR: Path = THIS_DIR.joinpath('files')


class Web3JsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, AttrDict) or isinstance(obj, AttributeDict):
            return {k: v for k, v in obj.items()}
        if isinstance(obj, HexBytes):
            return obj.hex()
        return json.JSONEncoder.default(self, obj)


def ini_router_contract(): pass


def load_abi(filename: str) -> dict:
    """ Load the ABI from the JSON provided by this package """
    global ABI_CACHE, ABI_FILE_DIR
    if ABI_CACHE.get(filename) is not None:
        return ABI_CACHE[filename]
    ABI_FILE: Path = ABI_FILE_DIR.joinpath(filename)
    with ABI_FILE.open() as _file:
        ABI_CACHE[filename] = json.loads(_file.read())
    return ABI_CACHE[filename]


def init_router_contract(web3: Web3, address: StrOrBytes) -> Contract:
    """ Initialize a Scatter Web3 Contract """
    address = to_account(address)
    abi = load_abi('IRouter.abi')
    return web3.eth.contract(address=address, abi=abi)


def init_scatter_contract(web3: Web3, router: Contract) -> Contract:
    """ Initialize a Scatter Web3 Contract """
    address = router.functions.get(Web3.sha3(text='Scatter')).call()
    address = to_account(address)
    abi = load_abi('IScatter.abi')
    return web3.eth.contract(address=address, abi=abi)


def init_register_contract(web3: Web3, router: Contract) -> Contract:
    """ Initialize a Scatter Web3 Contract """
    address = router.functions.get(Web3.sha3(text='Register')).call()
    address = to_account(address)
    abi = load_abi('IRegister.abi')
    return web3.eth.contract(address=address, abi=abi)


def gen_signature(abi_entry: dict) -> str:
    """ Generate a signature for an ABI entry """
    if not abi_entry.get('name') or not abi_entry.get('type') or not abi_entry.get('inputs') \
            or (abi_entry.get('type') not in ('function', 'event')):
        raise ValueError("Invalid ABI type to generate signature")
    input_types = [x['type'] for x in abi_entry['inputs']]
    sig = '{}({})'.format(abi_entry['name'], ','.join(input_types))
    return Web3.sha3(text=sig).hex()


def events_from_abi(abi: dict) -> dict:
    """ Get all events from an ABI and store with topics signature as key """
    if len(abi) < 1:
        return {}
    events = {}
    for ent in abi:
        if ent.get('type') == 'event':
            events[gen_signature(ent)] = ent
    return events


def get_types_from_inputs(abi_inputs: List[Dict[str, Any]]) -> Tuple[List, List]:
    """ Take the types from an abi and return them as indexed or not """
    indexed_types: List = []
    data_types: List = []

    for i in range(0, len(abi_inputs)):
        if abi_inputs[i]['indexed'] is True:
            indexed_types.append(abi_inputs[i]['type'])
        elif abi_inputs[i]['indexed'] is False:
            data_types.append(abi_inputs[i]['type'])
        else:
            log.error("Not sure if ABI type is indexed. This is probably an error.")

    return (indexed_types, data_types)


def decode_values(types: Collection, values: Collection) -> List:
    """ Decode individual values as the provided types """
    assert len(types) == len(values), "Mismatched types and values"

    types = list(types)
    values = list(values)

    decoded = []

    for i in range(0, len(values)):
        dsingle = decode_single(types[i], values[i])
        decoded.append(dsingle)

    return decoded


def event_from_log(abi: Dict[str, Any], event_log: Dict[str, Any]) -> AttrDict:
    if not abi.get('inputs'):
        log.warning("ABI has no inputs")
        return {}

    indexed_types, data_types = get_types_from_inputs(abi['inputs'])
    indexed_values = safe_slice(event_log['topics'], 1, 4)
    indexed_decoded = decode_values(indexed_types, indexed_values)
    if len(event_log['data']) > 0:
        data_decoded = decode_abi(data_types, HexBytes(event_log['data']))
    else:
        data_decoded = []

    event = AttrDict({
        'args': AttrDict(),
        'name': abi['name'],
    })

    for i in range(0, len(indexed_decoded)):
        if abi['inputs'][i]['type'] in ('bytes32', 'address'):
            if isinstance(indexed_decoded[i], bytes):
                val = add_0x_prefix(indexed_decoded[i].hex())
            else:
                val = indexed_decoded[i]
            event['args'][abi['inputs'][i]['name']] = val
        else:
            event['args'][abi['inputs'][i]['name']] = indexed_decoded[i]

    if len(abi['inputs']) > 3:
        indexed_count = len(indexed_types)
        for i in range(0, len(data_decoded)):
            name = abi['inputs'][indexed_count + i]['name']
            if isinstance(data_decoded[i], bytes):
                val = data_decoded[i].hex()
            else:
                val = data_decoded[i]
            event['args'][name] = val
    return event
