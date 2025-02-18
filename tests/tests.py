

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
      except AssertionError:
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

# Example usage:
# Test Case 1A: Only A sends messages
def test_case_1A():
    return run_test_case(sending_clients=['A'], messages_per_client={'A': N})

# Test Case 1B: Only B sends messages
def test_case_1B():
    return run_test_case(sending_clients=['B'], messages_per_client={'B': N})

# Test Case 1C: Only C sends messages
def test_case_1C():
    return run_test_case(sending_clients=['C'], messages_per_client={'C': N})

# Test Case 2: All clients send equally and sequentially
def test_case_2():
    return run_test_case(sending_clients=['A', 'B', 'C'], messages_per_client={'A': N//3, 'B': N//3, 'C': N//3})

# Test Case 3: All clients send in random order
def test_case_3():
    return run_test_case(sending_clients=['A', 'B', 'C'])

# Test Case 4: Clients send messages based on weighted probabilities
def test_case_4():
    return run_test_case(sending_clients=['A', 'B', 'C'], prob_distribution={'A': 0.5, 'B': 0.3, 'C': 0.2})

# Test Case 5: Fixed number of messages for each client
def test_case_5():
    return run_test_case(sending_clients=['A', 'B', 'C'], messages_per_client={'A': 50, 'B': 30, 'C': 20})

# Example run
pads_used, wastage, collisions = test_case_5()
print(f"Pads Used: {pads_used}, Wastage: {wastage}, Collisions: {collisions}")

def run_multiple_tests_varying(num_runs=10000):
    """
    Runs all test cases multiple times with varying test case parameters (message distribution, probabilities),
    ensuring valid probability distributions and message count constraints.

    Parameters:
    - num_runs (int): Number of times each test case should run.

    Returns:
    - A dictionary containing average pads used, wastage, and collisions per test case.
    - A list of all results with individual runs.
    """

    def valid_probabilities():
        """Generates three valid probabilities that sum exactly to 1."""
        p1, p2 = sorted(np.random.uniform(0.1, 0.8, size=2))  # Ensure sorted for stability
        p3 = round(1 - (p1 + p2), 6)  # Ensure exact sum of 1
        return {'A': p1, 'B': p2, 'C': p3}

    def valid_message_distribution():
        """Generates a valid message split where sum exactly equals N."""
        m1 = np.random.randint(10, N // 2)
        m2 = np.random.randint(10, N // 2)
        m3 = max(0, N - (m1 + m2))  # Ensure sum = N
        return {'A': m1, 'B': m2, 'C': m3}

    test_cases = {
        "Test Case 1A": lambda: run_test_case(sending_clients=['A'], messages_per_client={'A': N}),
        "Test Case 1B": lambda: run_test_case(sending_clients=['B'], messages_per_client={'B': N}),
        "Test Case 1C": lambda: run_test_case(sending_clients=['C'], messages_per_client={'C': N}),
        "Test Case 2": lambda: run_test_case(
            sending_clients=['A', 'B', 'C'],
            messages_per_client=valid_message_distribution()
        ),
        "Test Case 3": lambda: run_test_case(sending_clients=['A', 'B', 'C']),
        "Test Case 4": lambda: run_test_case(
            sending_clients=['A', 'B', 'C'],
            prob_distribution=valid_probabilities()
        ),
        "Test Case 5": lambda: run_test_case(
            sending_clients=['A', 'B', 'C'],
            messages_per_client=valid_message_distribution()
        )
    }

    results = []

    for _ in range(num_runs):
        for test_name, test_func in test_cases.items():
            try:
                pads_used, wastage, collisions = test_func()

                results.append({
                    "Test Case": test_name,
                    "N": N,
                    "D": D,
                    "Pads Used": pads_used,
                    "Wastage": wastage,
                    "Collisions": sum(collisions)
                })
            except ValueError as e:
                print(f"Skipping {test_name} due to invalid parameter: {e}")

    # Convert to DataFrame
    results_df = pd.DataFrame(results)

    # Compute summary statistics
    averages = results_df.groupby("Test Case").agg(
        Avg_Pads_Used=("Pads Used", "mean"),
        Avg_Wastage=("Wastage", "mean"),
        Avg_Collisions=("Collisions", "mean")
    ).to_dict("index")

    return averages, results_df.to_dict("records")

# Run the test and return results
averages, all_results = suppress_all_output(run_multiple_tests_varying, num_runs=10000)


import pprint
pp = pprint.PrettyPrinter(depth=4)
pp.pprint(averages)


def main():
  # test_case_1A()
  # init_globals(n=120, d=20, debug=False)
  # test_case_1B()
  # init_globals(n=120, d=20, debug=False)
  # test_case_1C()
  # test_case_1C()
  print(run_test_case(sending_clients=['A', 'B', 'C'], prob_distribution={'A': 0.9, 'B': 0.05, 'C': 0.05})) #COLLISION CASE
  # test_case_4()
  # test_case_5(messages_A=27, messages_B=26, messages_C=27)


if __name__ == '__main__':
  main()

def test_case_1A():
  '''
  Only A client sends
  '''
  init_globals()
  pads = init_pads(N,3)
  client_A = client('A', pads)
  client_B = client('B', pads)
  client_C = client('C', pads)

  QH = queue_handler([client_A, client_B, client_C])

  for x in range(120):
    try:
      client_A.send_message()
      QH.deliver()
    except AssertionError as e:
      # print('Pads exhausted',e,x)
      break


    # if x%4 == randint(0,4):
    #   QH.deliver_undelivered()
  a = client_A.statistics()
  b = client_B.statistics()
  c = client_C.statistics()
  print('Collisions:',sum(COLLISIONS), COLLISIONS)
  print('Wastage:', N-sum([a[0],b[0],c[0]]))

  # client_A.print_history()
  # client_B.print_history()
  # client_C.print_history()
  return COLLISIONS


def test_case_1B():
  '''
  Only B client sends
  '''
  init_globals()
  pads = init_pads(N,3)
  client_A = client('A', pads)
  client_B = client('B', pads)
  client_C = client('C', pads)

  QH = queue_handler([client_A, client_B, client_C])

  for x in range(120):
    try:
      client_B.send_message()
      QH.deliver()
    except AssertionError as e:
      # print('Pads exhausted',e,x)
      break


    # if x%4 == randint(0,4):
    #   QH.deliver_undelivered()
  a = client_A.statistics()
  b = client_B.statistics()
  c = client_C.statistics()
  print('Collisions:',sum(COLLISIONS), COLLISIONS)
  print('Wastage:', N-sum([a[0],b[0],c[0]]))

  # client_A.print_history()
  # client_B.print_history()
  # client_C.print_history()
  return COLLISIONS


def test_case_1C():
  '''
  Only C client sends
  '''
  init_globals()
  pads = init_pads(N,3)
  client_A = client('A', pads)
  client_B = client('B', pads)
  client_C = client('C', pads)

  QH = queue_handler([client_A, client_B, client_C])

  for x in range(120):
    try:
      client_C.send_message()
      QH.deliver()
    except AssertionError as e:
      # print('Pads exhausted',e,x)
      break


    # if x%4 == randint(0,4):
    #   QH.deliver_undelivered()
  a = client_A.statistics()
  b = client_B.statistics()
  c = client_C.statistics()
  print('Collisions:',sum(COLLISIONS), COLLISIONS)
  print('Wastage:', N-sum([a[0],b[0],c[0]]))
  return COLLISIONS

  # client_A.print_history()
  # client_B.print_history()
  # client_C.print_history()




def test_case_2():
  '''
  All clients send equally and sequentially
  '''
  init_globals()
  pads = init_pads(N,3)
  client_A = client('A', pads)
  client_B = client('B', pads)
  client_C = client('C', pads)
  print('Collisions:',sum(COLLISIONS), COLLISIONS)

  QH = queue_handler([client_A, client_B, client_C])
  can_send = [True, True, True]

  for x in range(N):
    try:
      client_A.send_message()
      QH.deliver()
    except AssertionError as e:
      can_send[0] = False
    try:
      client_B.send_message()
      QH.deliver()
    except AssertionError as e:
      can_send[1] = False
    try:
      client_C.send_message()
      QH.deliver()
    except AssertionError as e:
      can_send[2] = False
    if not any(can_send):
      break

    # if x%4 == randint(0,4):
    #   QH.deliver_undelivered()
  a = client_A.statistics()
  b = client_B.statistics()
  c = client_C.statistics()
  print('Collisions:',sum(COLLISIONS), COLLISIONS)
  print('Wastage:', N-sum([a[0],b[0],c[0]]))

  return COLLISIONS

  # client_A.print_history()
  # client_B.print_history()
  # client_C.print_history()

def test_case_3():
  '''
  All clients send equally but in randm order
  '''
  init_globals()
  pads = init_pads(N,3)
  client_A = client('A', pads)
  client_B = client('B', pads)
  client_C = client('C', pads)

  clients = [client_A, client_B, client_C]

  QH = queue_handler(clients)

  can_send = [True, True, True]
  for x in range(N):
    i = randrange(0,3)
    sender = clients[i]
    try:
      sender.send_message()
      QH.deliver()
    except AssertionError as e:
      can_send[i] = False
      pass

    if not any(can_send):
      break



    # if x%4 == randint(0,4):
    #   QH.deliver_undelivered()
  a = client_A.statistics()
  b = client_B.statistics()
  c = client_C.statistics()
  print('Collisions:',sum(COLLISIONS), COLLISIONS)
  print('Wastage:', N-sum([a[0],b[0],c[0]]))
  return COLLISIONS

  # client_A.print_history()
  # client_B.print_history()
  # client_C.print_history()

test_case_2()



def test_case_4(prob_A=0.33, prob_B=0.33, prob_C=0.34):
    '''
    Clients send messages based on weighted probabilities.
    '''
    init_globals()

    # Ensure probabilities sum to 1
    total_prob = prob_A + prob_B + prob_C
    if abs(total_prob - 1.0) > 1e-6:
        raise ValueError(f"Probabilities must sum to 1. Got {total_prob}")

    pads = init_pads(N, 3)
    client_A = client('A', pads)
    client_B = client('B', pads)
    client_C = client('C', pads)

    clients = [client_A, client_B, client_C]
    client_names = ['A', 'B', 'C']
    probabilities = [prob_A, prob_B, prob_C]

    QH = queue_handler(clients)

    can_send = [True, True, True]
    for x in range(N):
        sender_name = choices(client_names, probabilities)[0]
        sender = next(client for client in clients if client.name == sender_name)

        try:
            sender.send_message()
            QH.deliver()
        except AssertionError:
            can_send[client_names.index(sender.name)] = False
            pass

        if not any(can_send):
            break

    a = client_A.statistics()
    b = client_B.statistics()
    c = client_C.statistics()

    print('Collisions:', sum(COLLISIONS), COLLISIONS)
    print('Wastage:', N-sum([a[0],b[0],c[0]]))
    return COLLISIONS
def test_case_5(messages_A=None, messages_B=None, messages_C=None):
    '''
    Clients send a fixed number of messages.
    Default: Each sends N/3 messages.
    '''
    init_globals()
    # Default values
    messages_A = messages_A if messages_A is not None else N // 3
    messages_B = messages_B if messages_B is not None else N // 3
    messages_C = messages_C if messages_C is not None else N // 3

    # Track remaining messages for each client
    remaining_messages = {'A': messages_A, 'B': messages_B, 'C': messages_C}

    pads = init_pads(N, 3)
    print(N)
    client_A = client('A', pads)
    client_B = client('B', pads)
    client_C = client('C', pads)

    clients = {'A': client_A, 'B': client_B, 'C': client_C}
    active_clients = ['A', 'B', 'C']

    QH = queue_handler(list(clients.values()))

    while any(remaining_messages[client] > 0 for client in active_clients):
        sender_name = choices(active_clients, [remaining_messages[c] for c in active_clients])[0]
        sender = clients[sender_name]

        try:
            sender.send_message()
            QH.deliver()
            remaining_messages[sender_name] -= 1
        except AssertionError:
            active_clients.remove(sender_name)  # Stop selecting this client if they can't send
            pass

    a = client_A.statistics()
    b = client_B.statistics()
    c = client_C.statistics()

    print('Collisions:', sum(COLLISIONS), COLLISIONS)
    print('Wastage:', N-sum([a[0],b[0],c[0]]))
    return COLLISIONS



