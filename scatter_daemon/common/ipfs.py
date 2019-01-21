import os
import json
import tempfile
import ipfsapi
from pathlib import Path
from multihash import from_hex_string, to_b58_string
from eth_utils import is_0x_prefixed, remove_0x_prefix, is_hex
from .typing import Optional, Dict, Any, PS
from .exceptions import ScatterError


def ipfs_get_json(ipfs_conn: ipfsapi.client.Client, file_hash: str, tmpdir: Optional[PS] = None) -> Dict[str, Any]:
    """ Perform an ipfs.get and return the json object as a Python dict """

    if isinstance(file_hash, bytes):
        file_hash = to_b58_string(from_hex_string('1220' + remove_0x_prefix(file_hash.hex())))
    elif is_0x_prefixed(file_hash):
        file_hash = to_b58_string(from_hex_string('1220' + remove_0x_prefix(file_hash)))
    elif is_hex(file_hash):
        file_hash = to_b58_string(from_hex_string('1220' + file_hash))
    elif file_hash.startswith('Qm'):
        pass
    else:
        raise ValueError("Invalid file_hash")

    with tempfile.TemporaryDirectory(dir=tmpdir) as _workdir:
        workdir = Path(_workdir)
        orig_dir = Path.cwd()
        assert orig_dir is not None
        os.chdir(workdir)

        ipfs_conn.get(file_hash)

        downloaded: Path = workdir.joinpath(file_hash)
        if not downloaded.exists() or not downloaded.is_file():
            raise ScatterError("Download filed.  File not found.")

        contents = ''
        with downloaded.open() as _userfile:
            userfile_text = _userfile.read()
            print("Downloaded... {}".format(userfile_text))
            contents = json.loads(userfile_text)

        os.chdir(orig_dir)
        downloaded.unlink()
        return contents
