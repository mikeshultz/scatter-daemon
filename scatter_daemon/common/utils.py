import json
from eth_utils import to_normalized_address
from .typing import Iterable, DictOfAny, Any, Dict, PS, StrOrBytes, to_path


def get_from_first(key: str, *ds: DictOfAny) -> Any:
    """ Return a value from the first dict with a value """
    if len(ds) < 1:
        raise ValueError('No dictionaries provided')

    for d in ds:
        if key in d:
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


def safe_slice(to_slice: Iterable, start: int, length: int) -> Iterable:
    """ Slice an iterable without throwing an exception even if it's out of bounds """
    iter_len = len(to_slice)
    if iter_len >= length:
        return to_slice[start:length]
    else:
        return to_slice[start:iter_len]
