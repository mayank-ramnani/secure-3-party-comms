from tests.helpers import *

def test_scenario_b():
    # scenario b: only two, randomly chosen, parties repeatedly send messages,
    # where the decision of who sends the next message is also randomly chosen
    pads_used, wastage, collisions = run_test_case(sending_clients=['A', 'B'], prob_distribution={'A': 0.5, 'B': 0.5})
    print(pads_used, wastage, collisions)
    assert collisions == [0,0,0]
