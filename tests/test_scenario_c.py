from tests.helpers import *
import random

def run_multiple_tests_varying(num_runs=10000):
    """
    Runs test case multiple times with varying test case parameters (message distribution, probabilities),
    ensuring valid probability distributions and message count constraints.

    Parameters:
    - num_runs (int): Number of times each test case should run.

    Returns:
    - A dictionary containing average pads used, wastage, and collisions per test case.
    - A list of all results with individual runs.
    """

    def valid_probabilities():
        """Generates three valid probabilities that sum exactly to 1."""
        probs = np.random.dirichlet([1, 1, 1])
        probs.sort()
        return {'A': float(probs[0]), 'B': float(probs[1]), 'C': float(probs[2])}

    def valid_message_distribution():
        """Generates a valid message split where sum exactly equals N."""
        a, b = sorted(random.sample(range(1, N), 2))  # pick 2 cut points
        m1 = a
        m2 = b - a
        m3 = N - b # total sum is N
        return {'A': m1, 'B': m2, 'C': m3}

    results = []

    for _ in range(num_runs):
        test_name = "TC3"
        try:
            probs = valid_probabilities()
            dists = valid_message_distribution()
            # print(dists)
            # print(probs)
            pads_used, wastage, collisions = run_test_case(['A', 'B', 'C'], probs, dists)
            results.append({
                "TC": test_name,
                "N": N,
                "D": D,
                "Pads Used": pads_used,
                "Wastage": wastage,
                "Collisions": sum(collisions)
            })
        except ValueError as e:
            print(f"Skipping {test_name} due to invalid parameter: {e}")

    # Convert to DataFrame
    pprint.pprint(results)
    results_df = pd.DataFrame(results)

    # Compute summary statistics
    print(results_df)
    averages = results_df.groupby("TC").agg(
        Avg_Pads_Used=("Pads Used", "mean"),
        Avg_Wastage=("Wastage", "mean"),
        Avg_Collisions=("Collisions", "mean")
    ).to_dict("index")

    return averages, results_df.to_dict("records")


def test_scenario_c():
    # scenario c
    # Run the test and return results
    averages, all_results = suppress_all_output(run_multiple_tests_varying, num_runs=10000)
    # num_runs = 10
    # averages, all_results = run_multiple_tests_varying(num_runs)
    pp = pprint.PrettyPrinter(depth=4)
    pp.pprint(averages)
    assert (averages['TC3']['Avg_Collisions']) == 0.0
