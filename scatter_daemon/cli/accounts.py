""" account operations """
import sys
from eth_utils import to_checksum_address
from ..accounts import get_available_accounts, create_account
from ..common.config import load_config, set_ini_account
from ..common.const import DEFAULT_CONFIG_PATH
from ..common.logging import getLogger

log = getLogger(__name__)


def add_parser_arguments(parser):
    """ Add additional subcommands onto this command """

    config_args = ('-c', '--config')
    config_kwargs = {
        'type': str,
        'dest': 'config',
        'default': DEFAULT_CONFIG_PATH,
        'help': 'The location of the configuration file'
    }

    parser.add_argument(*config_args, **config_kwargs)
    parser.add_argument('-k', '--keystore', type=str, default='~/.ethereum/keystore',
                        help="The keystore directory containing Ethereum secret store files")

    subparsers = parser.add_subparsers(title='Submcommands', dest='subcommand',
                                       help='Validator commands')

    # scatter accounts create
    create_parser = subparsers.add_parser('create', help="Create a new account")
    create_parser.add_argument('--add-to-ini', action="store_true", dest='add_to_ini',
                               help='Add the new account to the INI')
    create_parser.add_argument('passphrase', type=str, nargs="?",
                               help='Passphrase to encrypt the secret store account file')

    return parser


def main(args):
    """ Execute init """

    if args.subcommand == 'create':
        if not args.config and args.add_to_ini is True:
            log.error("Config must be provided")

        address = create_account(args.keystore, args.passphrase)

        print("Created account {}".format(address))

        if args.add_to_ini is True:
            conf = load_config(args.config)
            set_ini_account(conf, address)
            print("Added account to INI file")

    else:
        accounts = get_available_accounts(args.keystore)
        for addr in accounts.keys():
            print(addr)
