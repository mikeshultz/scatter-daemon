""" Handles web3 related operations """
from typing import Callable, List
from web3 import Web3
from web3.providers import HTTPProvider, WebsocketProvider, IPCProvider
from .config import ConfigParser, ROOT_EL, config_get
from .logging import getLogger

log = getLogger(__name__)


def resolve_web3_provider(s: str) -> Callable:
    """ Return a provider from a type from config """
    if s == 'websocket':
        return WebsocketProvider
    elif s == 'ipc':
        return IPCProvider
    return HTTPProvider


def init_web3(conf: ConfigParser) -> Web3:
    """ Initialize a Web3 instance """

    provider_string = config_get(conf, 'web3_provider')
    provider_args_string = config_get(conf, 'web3_provider_args')

    web3_provider: Callable = resolve_web3_provider(provider_string)
    provider_args: List = []
    if provider_args_string:
        provider_args = provider_args_string.split(',')
    return Web3(web3_provider(*provider_args))


def eth_getLogs(web3, from_block: str, address: str, to_block: str = 'latest', topics: List = []):
    """ Run eth_getLogs """
    params = {
        'fromBlock': from_block,
        'toBlock': to_block,
        'address': address,
        'topics': topics,
    }
    return web3.eth.getLogs(params)
