# Secure 3 Party Communication using One Time Pads

## Initializing the repository
1. Install poetry is you haven't already: `brew install poetry` or `apt install poetry`
2. Install all required dependencies of project: `poetry install` 

## Running the protocol
- The protocol implementation is a module that can be imported using:
    `from secure_3_party_comms.protocol import *`
- To change the values of N, d or the probability of a message being undelivered, change the global variables at the top of `secure_3_party_comms/protocol.py`

# Running the testcases
- To run all testcases, run `poetry run pytest`
- To run testcases without output suppression: `poetry run pytest -s`
