""" The Validator """
import time
import sqlite3
from typing import List
from configparser import ConfigParser
from web3 import Web3
from web3.eth import Contract
from attrdict import AttrDict
from ..storage import connect, store_events, get_bids_to_validate
from ..common.const import STD_PROCESS_DELAY, SETTLED_PROCESS_DELAY, DEFAULT_DB_FILE
from ..common.config import VALIDATOR_EL, config_get
from ..common.contracts import (
    init_router_contract,
    init_scatter_contract,
    events_from_abi,
    event_from_log
)
from ..common.web3 import init_web3, eth_getLogs
from ..common.exceptions import ValidatorError
from ..common.logging import getLogger
from .logic import select_random_pin_for_validation

log = getLogger(__name__)


def validate(): pass
def get_job():
    """ Get a bid that needs to be serviced """
    pass


def process_events(contract: Contract, logs: List) -> List[AttrDict]:
    """ Process all events """
    events = []
    event_lookup = events_from_abi(contract.abi)
    for event_log in logs:
        topic_sig = event_log['topics'][0].hex()
        log.debug("topic_sig: {}".format(topic_sig))
        log.debug("event_lookup: {}".format(event_lookup))
        if topic_sig in event_lookup:
            new_event = event_from_log(event_lookup[topic_sig], event_log)
            new_event['name'] = event_lookup[topic_sig].get('name')
            new_event['txhash'] = logs[0]['transactionHash'].hex()
            new_event['block_number'] = logs[0]['blockNumber']
            log.info("Received event {}.".format(new_event['name']))
            events.append(new_event)
    return events


def fetch_events(conn: sqlite3.Connection, web3: Web3, scatter: Contract):
    """ Retrieve and store all events """
    log.debug("Getting events for Scatter")

    logs = eth_getLogs(web3, from_block='0x0', address=scatter.address)

    log.debug("Found {} logs.".format(len(logs)))

    if logs:
        events = process_events(scatter, logs)
        if events:
            store_events(conn, events)


def validate_bid(scatter: Contract, bid_id: int):
    """ Perform validation """
    print('#######################################################################################')
    print('#######################################################################################')
    print('#######################################################################################')
    pass


def validate_run(conf: ConfigParser) -> None:
    """ Run a continuous process and validate everything eligible that meets the filters in the
    provided configuration.
    """
    log.info("Preparing to start validation run...")

    web3 = init_web3(conf)
    my_account = config_get(conf, 'account')
    router_address = config_get(conf, 'router_address')

    if not my_account or not router_address:
        raise ValidatorError("Missing an address for router or validator.")

    router = init_router_contract(web3, router_address)
    scatter = init_scatter_contract(web3, router)
    db_conn = connect(config_get(conf, 'db_file', DEFAULT_DB_FILE))

    while True:
        log.info("Fetching events...")
        fetch_events(db_conn, web3, scatter)

        log.info("Selecting pin to validate...")
        pins = get_bids_to_validate(db_conn, my_account)
        log.debug("Found {} available pins".format(len(pins)))
        bid_id = select_random_pin_for_validation(scatter, pins, {
            'max_file_size': config_get(conf, 'max_file_size', section=VALIDATOR_EL),
        })

        if bid_id > -1:
            log.error("VALIDATE_BID")
            log.info('Validating bid #{}'.format(bid_id))
            validate_bid(scatter, bid_id)

            # Let's not go crazy here
            time.sleep(STD_PROCESS_DELAY)
        else:
            log.info('Nothing to validate')
            time.sleep(SETTLED_PROCESS_DELAY)
