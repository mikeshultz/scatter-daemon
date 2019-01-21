# Scatter Daemon

This is a client for [scatter.online](https://scatter.online).  This client can act as a
[hoster](docs/defs.md#hoster) and [validator](docs/defs.md#hoster).  For bidding to get IPFS files
pinned, use the dapp at https://scatter.online.

**NOTE**: Please see the below "Security Considerations" section before running the node yourself.

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

## Security Considerations

It's recommended to use the docker containers given for this system.  They take all of the below
into account.

### Validator Daemon

The validator daemon requires a running IPFS node with an IPFS API available to the daemon. This is
usually easily achieved by firewalling the API to only accept localhost connections.  However, keep
in mind that any users of this system will be able to make requests.

### Hoster Daemon

The hoster daemon requires an IPFS node with a **public** IPFS API.  This, obviously, is not ideal
in most situations, but it's the only way for validators to verify that pins exist.  The provided
Docker containers include an HTTP firewall that limit requests to only the relevant IPFS HTTP API
URIs.  If you decide to roll your own, **do not** leave the HTTP API open for all.  Using the IPFS
HTTP API, they can add files and pins to your node on a whim.  There are plans to add auth and
permissions to the IFPS daemon but they are not currently available.
