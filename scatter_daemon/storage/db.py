import sqlite3
from ..common.typing import PS, Optional
from ..common.utils import to_path
from ..common.exceptions import StorageError
from ..common.logging import getLogger

log = getLogger(__name__)

cached_connection: Optional[sqlite3.Connection] = None
#TABLES = ['event', 'pin', 'action', 'action_type']
TABLES = ['event', 'bid', 'action', 'action_type']


def structure_exists(connect: sqlite3.Connection) -> bool:
    """ See if the DB structure has been created """
    cur = connect.cursor()
    for tbl in TABLES:
        cur.execute("SELECT name FROM sqlite_master "
                    "WHERE type='table' AND name=:table_name;",
                    {'table_name': tbl})
        res = cur.fetchall()
        if len(res) < 1:
            log.debug('Table {} does not exist.'.format(tbl))
            return False
    return True


def init_structure(connect: sqlite3.Connection):
    """ Create the table structure """

    cur = connect.cursor()

    cur.execute("CREATE TABLE event "
                "(tx_hash TEXT, block_number INT, name TEXT, "
                "args TEXT);")

    cur.execute("CREATE UNIQUE INDEX event_single ON event(tx_hash, name);")

    cur.execute("CREATE TABLE action_type "
                "(name TEXT);")

    cur.execute("CREATE TABLE bid "
                "(tx_hash TEXT UNIQUE, bid_id INT UNIQUE, bidder TEXT, bid_value INT, "
                "validation_pool INT, file_hash TEXT, file_size INT, hoster TEXT, pinned BOOLEAN, "
                "pinned_txhash TEXT, accepted INT, accepted_txhash TEXT, "
                "validated BOOLEAN);")

    cur.execute("CREATE TABLE action "
                "(action_rowid INT, event_rowid INT);")

    # Pre-data
    cur.execute("INSERT INTO action_type (name) VALUES (:name);", {'name': 'validation'})
    cur.execute("INSERT INTO action_type (name) VALUES (:name);", {'name': 'host'})

    connect.commit()


def connect(filename: PS) -> sqlite3.Connection:
    """ Initialize the SQLite connection """
    global cached_connection

    filename = to_path(filename)

    if not filename.parent.exists():
        log.debug('Creating parent directory {} for DB storage.'.format(filename.parent))
        filename.parent.mkdir(parents=True)
    elif filename.parent.exists() and not filename.parent.is_dir():
        raise StorageError('Directory for DB storage is not a directory!')

    # Use the cached connection if possible
    if cached_connection is None:
        cached_connection = sqlite3.connect(filename)

    # Create the schema if necessary
    if not structure_exists(cached_connection):
        init_structure(cached_connection)

    return cached_connection


def cursor(filename=None):
    """ return a cursor, creating a connection if necessary """
    global cached_connection

    if cached_connection is None:
        if not filename:
            raise Exception('Unable to get a cursor without a filename')
        connect(filename)

    return cached_connection.cursor()
