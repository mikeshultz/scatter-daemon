""" Generic utility functions """
import os
import json
from eth_utils import to_normalized_address
from .typing import Collection, DictOfAny, List, Any, Dict, PS, StrOrBytes, to_path
from .logging import getLogger

log = getLogger(__name__)


def get_from_first(key: str, *ds: DictOfAny) -> Any:
    """ Return a value from the first dict with a value """
    if type(ds) != tuple or len(ds) < 1 or not isinstance(ds[0], dict):
        raise ValueError('No dictionaries provided')

    for d in ds:
        if key in d:
            if d[key] is not None:
                return d[key]
    return None


def read_json_file(json_file: PS) -> dict:
    """ Read a json file into a string """
    json_file = to_path(json_file)

    out: Dict[str, Any] = dict()
    with json_file.open() as _file:
        out = json.loads(_file.read())
    return out


def address_in_keys(address: StrOrBytes, d: Dict[str, Any]) -> bool:
    """ Check if an Ethereum address is a key of the provided dict """
    address = to_normalized_address(address)
    return address in [to_normalized_address(k) for k in d.keys()]


def safe_slice(to_slice: List, start: int, end: int) -> List:
    """ Slice an iterable without throwing an exception even if it's out of bounds """
    iter_len = len(to_slice)
    if iter_len >= end:
        return to_slice[start:end]
    else:
        return to_slice[start:iter_len]


def is_free_space_available(at_path: PS, size_bytes: int) -> bool:
    """ Check if there's at least size_bytes available on disk """
    at_path = to_path(at_path)
    res = os.statvfs(at_path)
    return (res.f_bsize * res.f_bfree) > size_bytes
