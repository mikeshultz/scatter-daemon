import json
import sqlite3
from ..common.typing import DictOfAny, List
from ..common.logging import getLogger
from .pins import store_pin

log = getLogger(__name__)


def get_stored_events(conn: sqlite3.Connection) -> List[DictOfAny]:
    events: List[DictOfAny] = []
    cur = conn.cursor()
    cur.execute("SELECT rowid, tx_hash, block_number, name, args FROM event;")
    res = cur.fetchall()
    if len(res) < 1:
        return events

    for row in res:
        events.append({
            'event_id': row[0],
            'tx_hash': row[1],
            'block_number': row[2],
            'name': row[3],
            'args': json.loads(row[4]),
        })

    return events


def store_events(conn: sqlite3.Connection, events: List[DictOfAny]) -> None:
    """ Store events in persistent storage """
    log.debug("store_events()")
    if len(events) < 1:
        return
    log.debug("store_events() - inserting event")
    cur = conn.cursor()

    for evnt in events:
        log.debug("evnt: {}".format(evnt))
        cur.execute("INSERT INTO event (tx_hash, name, block_number, args) "
                    "VALUES (:tx_hash, :name, :block_number, :args);",
                    {
                        'tx_hash': evnt['txhash'],
                        'block_number': evnt['block_number'],
                        'name': evnt['name'],
                        'args': json.dumps(evnt['args']),
                    })
        conn.commit()
        log.debug("Inserted event {}".format(evnt.get('name')))
        if evnt.get('name') == 'Pinned':
            store_pin(conn, evnt)
        elif evnt.get('name') == 'BidSuccessful':
            # store_bid(evnt)
            pass
