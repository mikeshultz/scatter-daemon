import json
import sqlite3
from attrdict import AttrDict
from ..common.typing import DictOfAny, List
from ..common.logging import getLogger

log = getLogger(__name__)


def store_bid(conn: sqlite3.Connection, evnt: DictOfAny):
    """ Store a pin in the DB """
    cur = conn.cursor()
    assert evnt.get('name') == 'BidSuccessful', "Invalid event given to store_bid"
    try:
        cur.execute("INSERT INTO bid (tx_hash, bid_id, bidder, bid_value, validation_pool, "
                    "file_size, file_hash) "
                    "VALUES (:tx_hash, :bid_id, :bidder, :bid_value, :validation_pool, "
                    ":file_size, :file_hash);",
                    {
                        'tx_hash': evnt['txhash'],
                        'bid_id': evnt['args'].bidId,
                        'bidder': evnt['args'].bidder,
                        'bid_value': evnt['args'].bidValue,
                        'validation_pool': evnt['args'].validationPool,
                        'file_size': evnt['args'].fileSize,
                        'file_hash': evnt['args'].fileHash,
                    })
    except sqlite3.IntegrityError as err:
        if 'UNIQUE' in str(err):
            log.debug("Event already exists.")
            pass
        else:
            raise err
    else:
        assert cur.rowcount > 0, "INSERT failed"
        conn.commit()


def get_bids_to_pin(conn: sqlite3.Connection, my_address: str):
    """ Get bids that have been pinned and are open for validation """

    bids: List[DictOfAny] = []

    cur = conn.cursor()

    cur.execute("SELECT tx_hash, bid_id, bidder, file_hash, file_size, validated FROM bid "
                "WHERE bidder != :me AND pinned = false;",
                {'me': my_address})
    res = cur.fetchall()
    if len(res) < 1:
        log.debug("NO BIDS FOUND")
        return bids

    for row in res:
        bids.append(AttrDict({
                'bid_id': row[1],
                'bidder': row[2],
                'file_hash': row[3],
                'file_size': row[4],
                'validated': row[5],
            }))

    return bids


def get_bids_to_validate(conn: sqlite3.Connection, my_address: str):
    """ Get bids that have been pinned and are open for validation """

    bids: List[DictOfAny] = []

    cur = conn.cursor()

    cur.execute("SELECT tx_hash, bid_id, hoster, file_hash, file_size, validated FROM bid "
                "WHERE hoster != :me AND pinned = true "
                "AND (validated is null or validated = false);",
                {'me': my_address})
    res = cur.fetchall()
    if len(res) < 1:
        log.debug("NO BIDS FOUND")
        return bids

    for row in res:
        bids.append(AttrDict({
                'bid_id': row[1],
                'hoster': row[2],
                'file_hash': row[3],
                'file_size': row[4],
                'validated': row[5],
            }))

    return bids
