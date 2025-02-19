"""
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
# pads_used, wastage, collisions = test_case_5()
# print(f"Pads Used: {pads_used}, Wastage: {wastage}, Collisions: {collisions}")

print(run_test_case(sending_clients=['A', 'B', 'C'], prob_distribution={'A': 0.9, 'B': 0.05, 'C': 0.05})) #COLLISION CASE
print(COLLISIONS)
# test_case_4()
# test_case_5(messages_A=27, messages_B=26, messages_C=27)
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

# test_case_2()

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
"""
