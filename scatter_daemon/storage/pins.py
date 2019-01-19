import json
import sqlite3
from datetime import datetime
from attrdict import AttrDict
from ..common.typing import DictOfAny, List
from ..common.logging import getLogger

log = getLogger(__name__)


def store_accept(conn: sqlite3.Connection, evnt: DictOfAny):
    """ Store an accept in the DB """
    cur = conn.cursor()
    assert evnt.get('name') == 'Accepted', "Invalid event given to store_pin"
    try:
        cur.execute("SELECT true FROM bid WHERE accepted_txhash = :txhash", {
            'txhash': evnt['txhash']
        })
        if len(cur.fetchall()) == 0:
            log.debug("!!!!!! accepted")
            cur.execute("UPDATE bid SET accepted = :accept_stamp, accepted_txhash = :txhash, "
                        " hoster = :hoster;", {
                            'accept_stamp': evnt['args'].when,
                            'txhash': evnt['txhash'],
                            'hoster': evnt['args'].hoster,
                        })
            assert cur.rowcount > 0, "UPDATE failed"
            conn.commit()
        else:
            log.warning("Accept already exists")
    except Exception as err:
        raise err


def store_pin(conn: sqlite3.Connection, evnt: DictOfAny):
    """ Store a pin in the DB """
    cur = conn.cursor()
    assert evnt.get('name') == 'Pinned', "Invalid event given to store_pin"
    try:
        cur.execute("SELECT true FROM bid WHERE pinned_txhash = :txhash", {
            'txhash': evnt['txhash']
        })
        if len(cur.fetchall()) == 0:
            cur.execute("UPDATE bid SET pinned = true, pinned_txhash = :txhash, "
                        "hoster = :hoster", {
                            'txhash': evnt['txhash'],
                            'hoster': evnt['args'].hoster,
                        })
            assert cur.rowcount > 0, "UPDATE failed"
            conn.commit()
    except Exception as err:
        raise err


def set_pin_validated(conn: sqlite3.Connection, bid_id: int) -> None:
    """ Set a pin as validated by me """
    cur = conn.cursor()
    cur.execute("UPDATE bid SET validated = true WHERE bid_id = :bid_id", {
        'bid_id': bid_id
    })
    assert cur.rowcount > 0, "UPDATE failed"
