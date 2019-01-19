import json
import sqlite3
from attrdict import AttrDict
from ..common.typing import DictOfAny, List
from ..common.logging import getLogger

log = getLogger(__name__)


def store_pin(conn: sqlite3.Connection, evnt: DictOfAny):
    """ Store a pin in the DB """
    cur = conn.cursor()
    assert evnt.get('name') == 'Pinned', "Invalid event given to store_pin"
    log.debug("STORING EVENT: {}".format(evnt))
    cur.execute("INSERT INTO pin (bid_rowid, hoster, file_hash) "
                "VALUES (:bid_id, :hoster, :file_hash);",
                {
                    'bid_id': evnt['args'].bidId,
                    'hoster': evnt['args'].hoster,
                    'file_hash': evnt['args'].fileHash,
                })
    conn.commit()
    assert cur.rowcount > 0, "INSERT failed"


def set_pin_validated(conn: sqlite3.Connection, pin_rowid: int) -> None:
    """ Set a pin as validated by me """
    cur = conn.cursor()
    cur.execute("UPDATE pins SET validated = true WHERE pin_rowid = :pin_id", {'pin_id': pin_id})
    assert cur.rowcount > 0, "UPDATE failed"


def get_available_pins(conn: sqlite3.Connection, my_address: str):
    """ Select a Pinned event that meets criteria for validation """

    pins: List[DictOfAny] = []

    cur = conn.cursor()

    cur.execute("SELECT rowid, hoster, file_hash, validated FROM pin "
                "WHERE hoster != :me AND validated = false;",
                {'me': my_address})
    res = cur.fetchall()
    if len(res) < 1:
        log.debug("NO PINS FOUND")
        return pins

    for row in res:
        pins.append(AttrDict({
                'pin_id': row[0],
                'hoster': row[1],
                'file_hash': row[2],
                'validated': row[3],
            }))

    return pins
