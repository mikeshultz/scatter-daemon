""" initialize configuration
"""
import sys
from pathlib import Path
from eth_utils import is_address, to_checksum_address
from ..validator import validate_run
from ..accounts import get_available_accounts
from ..common.config import init_config, load_config
from ..common.const import DEFAULT_CONFIG_PATH
from ..common.utils import address_in_keys
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

    subparsers = parser.add_subparsers(title='Submcommands', dest='subcommand',
                                       help='Validator commands')

    init_parser = subparsers.add_parser('init', help="Initialize configuration")
    init_parser.add_argument('-a', '--account', type=str, dest='account',
                             required=True,
                             help=('The account that will act as validator.  It must exist in the '
                                   'keystore.'))
    init_parser.add_argument(*config_args, **config_kwargs)

    run_parser = subparsers.add_parser('run', help="Run the validator")
    run_parser.add_argument(*config_args, **config_kwargs)

    return parser


def main(args):
    """ Execute init """
    log.info("Starting validator daemon...")

    if args.subcommand == 'init':

        config_path = Path(args.config).expanduser().resolve()
        if config_path.exists():
            log.error('Config file already exists at {}'.format(args.config))
            sys.exit(1)

        log.info('Initializing configuration at {}'.format(args.config))

        validator_account = to_checksum_address(args.account)
        available_accounts = get_available_accounts(args.keystore)

        if not address_in_keys(validator_account, available_accounts):
            log.error("Provided account {} does not appear to be in the keystore directory {}.".format(
                validator_account,
                args.keystore,
            ))
            sys.exit(1)

        init_config(args.config, validator_account)

    else:

        conf = load_config(args.config)
        validate_run(conf)
