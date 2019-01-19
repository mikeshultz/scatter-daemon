# Scatter Daemon

This is a client for [scatter.online](https://scatter.online).  This client can act as a
[hoster](docs/defs.md#hoster) and [validator](docs/defs.md#hoster).  For bidding to get IPFS files
pinned, use the dapp at https://scatter.online.

**NOTE**: This daemon requires a running IPFS node with an IPFS API available to the daemon.

## Overview

This package includes daemons for hosting and validation.  They are generally used as an automated
system.  You can bring up the docker instance and just leave it running and earn Ether!

**NOTE**: Keep in mind, you will only get paid if you keep files pinned for the entire requested
duration.  If you instance drops out or you lose the files, you will not be compensated.

### Validator

The validator validates, or confirms, that IPFS files are actually pinned to the network.  It uses
your IPFS server to validate that bidded files have been pinned by the hoster.

### Hoster

The hoster actually processes bids and pins files that match your filter parameters.
