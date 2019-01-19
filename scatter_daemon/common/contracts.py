""" Functions for creating Web3 contract instances """
import json
from pathlib import Path
from hexbytes import HexBytes
from web3 import Web3
from web3.eth import Contract
from web3.datastructures import AttributeDict
from eth_abi import decode_abi
from eth_utils import remove_0x_prefix, add_0x_prefix
from attrdict import AttrDict
from .typing import (
    to_account,
    Optional,
    StrOrBytes,
    Dict,
    Tuple,
    Set,
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


def gen_signature(abi_entry: dict) -> str:
    """ Generate a signature for an ABI entry """
    if not abi_entry.get('name') or not abi_entry.get('type') or not abi_entry.get('inputs') \
            or (abi_entry.get('type') not in ('function', 'event')):
        raise ValueError("Invalid ABI type to generate signature")
    input_types = [x['type'] for x in abi_entry['inputs']]
    return Web3.sha3(text='{}({})'.format(abi_entry['name'], ','.join(input_types))).hex()


def events_from_abi(abi: dict) -> dict:
    """ Get all events from an ABI and store with topics signature as key """
    log.debug("events_from_abi: len(abi) {}".format(len(abi)))
    if len(abi) < 1:
        return {}
    events = {}
    for ent in abi:
        log.debug("processing... {}".format(ent))
        if ent.get('type') == 'event':
            events[gen_signature(ent)] = ent
    return events


def get_types_from_inputs(abi_inputs: List[Dict[str, Any]]) -> Tuple[Set, Set]:
    """ Take the types from an abi and return them as indexed or not """
    indexed_types: Set = set()
    data_types: Set = set()

    log.debug("abi_inputs: {}".format(abi_inputs))
    for i in range(0, len(abi_inputs) - 1):
        if abi_inputs[i]['indexed'] is True:
            indexed_types.add(abi_inputs[i]['type'])
        elif abi_inputs[i]['indexed'] is False:
            data_types.add(abi_inputs[i]['type'])
        else:
            log.error("Not sure if ABI type is indexed. This is probably an error.")

    return (indexed_types, data_types)


def event_from_log(abi: Dict[str, Any], event_log: Dict[str, Any]) -> AttrDict:
    log.debug("abi: {}".format(abi))
    log.debug("event_log: {}".format(event_log))
    if not abi.get('inputs'):
        log.warning("ABI has no inputs")
        return {}

    indexed_types, data_types = get_types_from_inputs(abi['inputs'])
    indexed_values = safe_slice(event_log['topics'], 1, 3)
    log.debug("len(indexed_values): {}".format(len(indexed_values)))
    log.debug("len(indexed_types): {}".format(len(indexed_types)))
    log.debug("len(data_types): {}".format(len(data_types)))
    indexed_decoded = decode_abi(indexed_types,
                                 HexBytes(''.join(remove_0x_prefix(x.hex()) for x in indexed_values)))
    if len(event_log['data']) > 0:
        data_decoded = decode_abi(data_types, HexBytes(event_log['data']))
    else:
        data_decoded = []

    event = AttrDict({
        'args': AttrDict(),
        'name': abi['name'],
    })

    for i in range(0, len(indexed_decoded)):
        if abi['inputs'][i]['type'] == 'bytes32':
            event['args'][abi['inputs'][i]['name']] = add_0x_prefix(indexed_decoded[i].hex())
        else:
            event['args'][abi['inputs'][i]['name']] = indexed_decoded[i]

    if len(abi['inputs']) > 3:
        for i in range(0, len(data_decoded)):
            event['args'][abi['inputs'][i]['name']] = data_decoded[i]
    log.debug("event_from_log() -> {}".format(event))
    return event
