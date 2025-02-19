from tests.helpers import *

# Test Case 1A: Only A sends messages
def test_case_1A():
    pads_used, wastage, collisions = run_test_case(sending_clients=['A'], messages_per_client={'A': N})
    assert pads_used == N/2
    assert wastage == N/2
    assert collisions == [0,0,0]

# Test Case 1B: Only B sends messages
def test_case_1B():
    pads_used, wastage, collisions = run_test_case(sending_clients=['B'], messages_per_client={'B': N})
    assert pads_used == N/2
    assert wastage == N/2
    assert collisions == [0,0,0]

# Test Case 1C: Only C sends messages
def test_case_1C():
    pads_used, wastage, collisions = run_test_case(sending_clients=['C'], messages_per_client={'C': N})
    assert pads_used == N/2
    assert wastage == N/2
    assert collisions == [0,0,0]

"""
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
"""
