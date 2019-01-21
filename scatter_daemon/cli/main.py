""" The main CLI handler """
import argparse
from importlib import import_module
from ..common.logging import getLogger

log = getLogger(__name__)

MODULES = [
    'init',
    'validator',
    'accounts',
]
IMPORTED_MODULES = {}


def parse_args(argv=None):
    """ Parse command line arguments """
    global IMPORTED_MODULES

    parser = argparse.ArgumentParser(description='Scatter validator daemon')
    parser.add_argument('-d', action='store_true',
                        help='Print debug level messages')
    parser.add_argument('-k', '--keystore', type=str, dest="keystore",
                        default='~/.ethereum/keystore',
                        help='Ethereum account keystore directory to use.')

    subparsers = parser.add_subparsers(title='Submcommands', dest='command',
                                       help='do the needful')

    """
    Each module must implement the following minimum API:
        - add_parser_arguments(parser) - A function that takes an argparse
            parser and adds the arguments it wants for its command
            implementation.
        - main(parser_args) - The primary function to run that provides
            parser_args as a kwarg
    """
    for mod in MODULES:
        IMPORTED_MODULES[mod] = import_module('scatter_daemon.cli.{}'.format(mod))
        module_subparser = subparsers.add_parser(mod, help=IMPORTED_MODULES[mod].__doc__)
        module_subparser = IMPORTED_MODULES[mod].add_parser_arguments(module_subparser)

    # Help command
    subparsers.add_parser('help', help='print usage')

    return parser.parse_args(argv), parser


def main(argv=None):
    """ Primary entry point for daemon """
    args, parser = parse_args(argv)
    IMPORTED_MODULES[args.command].main(args=args)
