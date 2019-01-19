from typing import (  # noqa: F401
    Any,
    Dict,
    Union,
    Optional,
    Callable,
    List,
    Tuple,
    Iterable,
    Collection,
    Set,
)
from pathlib import Path
from eth_utils import is_address, to_normalized_address
from web3 import Web3

PS = Union[Path, str]
StrOrBytes = Union[str, bytes]
DictOfAny = Dict[str, Any]
SetOrList = Union[Set, List]


def to_path(v: PS) -> Path:
    """ Coax a PS value to a Path """
    if not isinstance(v, Path):
        v = Path(v)
    return v.expanduser().resolve()


def to_account(v: StrOrBytes) -> str:
    """ Normalize an account address """
    if not is_address(v):
        raise ValueError('{} is not an account'.format(v))
    return Web3.toChecksumAddress(to_normalized_address(v))
