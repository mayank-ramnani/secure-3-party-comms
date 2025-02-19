# Secure 3 Party Communication using One Time Pads

## Programs
- Protocol Implementation: `secure_3_party_comms/protocol.py`
- Test Cases Implementation: `tests/`

## Initializing the repository
1. Install poetry if you haven't already: `brew install poetry` or `apt install poetry`
2. Install all required dependencies of project: `poetry install`

## Running the protocol
- The protocol implementation is a module that can be imported using:
    `from secure_3_party_comms.protocol import *`
- To change the values of N, d or the probability of a message being undelivered, change the global variables at the top of `secure_3_party_comms/protocol.py`

# Running the testcases
- To run all testcases, run `poetry run pytest`
- To run testcases without output suppression: `poetry run pytest -s`
- To run a particular scenario: `poetry run pytest tests/test_scenario_a.py`
- To run a custom scenario, follow the instructions:
    1. Create a new file in the `tests` directory
    2. Add `from tests.helpers import *` at the top of the file to import protocol functionality
    3. Define a function with name starting with `test_` which calls the helper function `run_test_case` with appropriate parameters.
    Example from `test_scenario_b.py`:
    `run_test_case(sending_clients=['A', 'B'], prob_distribution={'A': 0.5, 'B': 0.5})`
