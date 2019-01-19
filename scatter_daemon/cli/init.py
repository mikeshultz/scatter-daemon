""" initialize configuration
"""
import sys
from eth_utils import to_checksum_address
from ..common.config import init_config
from ..common.logging import getLogger

log = getLogger(__name__)


def add_parser_arguments(parser):
    """ Add additional subcommands onto this command """

    parser.add_argument('-a', '--account', type=str, dest='account',
                        help='The Ethereum account to use to validate')
    parser.add_argument('-c', '--config', type=str, dest='config',
                        help='The location to save initial configuration')

    return parser


def main(args):
    """ Execute init """
    account = to_checksum_address(args.account)

    log.info("Initializing configuration...")
    dest = init_config(args.config, account)
    log.info("Configuration saved to {}.".format(dest))
