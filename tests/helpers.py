from secure_3_party_comms.protocol import *
from random import randint, randrange, choices
import numpy as np
import pandas as pd
import pprint
import pytest

def run_test_case(sending_clients=None, prob_distribution=None, messages_per_client=None):
    """
    A modular test function to execute different test cases based on the provided parameters.

    - `sending_clients`: A list of clients who can send messages. Default: ['A', 'B', 'C'] (all).
    - `prob_distribution`: A dictionary specifying the probability distribution for sending clients.
      Example: {'A': 0.5, 'B': 0.3, 'C': 0.2}. If None, it defaults to equal probability.
    - `messages_per_client`: A dictionary specifying a fixed number of messages for each client.
      Example: {'A': 50, 'B': 30, 'C': 20}. If None, defaults to N/3 per client.

    Returns:
    - `pads_used`: Total pads used for sending messages.
    - `wastage`: Number of wasted pads.
    - `collisions`: List of collision counts per client.
    """

    init_globals()
    global COLLISIONS
    COLLISIONS = [0, 0, 0]

    pads = init_pads(N, 3)
    client_A = client('A', pads)
    client_B = client('B', pads)
    client_C = client('C', pads)

    clients = {'A': client_A, 'B': client_B, 'C': client_C}
    active_clients = sending_clients if sending_clients else ['A', 'B', 'C']
    QH = queue_handler([client_A, client_B, client_C])

    if messages_per_client:
        remaining_messages = {c: messages_per_client.get(c, 0) for c in active_clients}
    else:
        # Default: N/3 messages per client
        remaining_messages = {c: N // len(active_clients) for c in active_clients}

    if prob_distribution:
        probabilities = [prob_distribution.get(c, 0) for c in active_clients]
    else:
        probabilities = [1 / len(active_clients)] * len(active_clients)  # Equal probability

    while any(remaining_messages[c] > 0 for c in active_clients):
        # Ensure weights match the updated client list
        probabilities = [prob_distribution[c] for c in active_clients] if prob_distribution else [1 / len(active_clients)] * len(active_clients)

        sender_name = choices(active_clients, probabilities)[0]
        sender = clients[sender_name]

        try:
            sender.send_message()
            QH.deliver()
            remaining_messages[sender_name] -= 1
        except AssertionError as e:
            # print(e)
            active_clients.remove(sender_name)  # Remove sender if they can't send

    # Collect statistics
    stats_A = client_A.statistics()
    stats_B = client_B.statistics()
    stats_C = client_C.statistics()

    # Calculate pads used
    pads_used = stats_A[0] + stats_B[0] + stats_C[0]

    # Compute wastage
    wastage = N - pads_used

    return pads_used, wastage, COLLISIONS

def suppress_all_output(func, *args, **kwargs):
    with open(os.devnull, 'w') as fnull:
        with contextlib.redirect_stdout(fnull), contextlib.redirect_stderr(fnull):
            return func(*args, **kwargs)
