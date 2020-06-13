from brain import Brain
from brain.activation_functions import Identity, ReLU, Sigmoid

test_samples = (
    {"input": (0, 0), "target": (0,)},
    {"input": (1, 0), "target": (1,)},
    {"input": (0, 1), "target": (1,)},
    {"input": (1, 1), "target": (0,)},
)


def test_brain_weight_gradients_sigmoid():
    brain_topology = (
        (2, None),
        (3, Sigmoid),
        (1, Sigmoid),
    )

    # Make sure the difference between analytical and numerical calculation is less than 0.1%
    test_brain = Brain(brain_topology)
    diff_percentages = validate_weight_gradients(test_brain, test_samples)
    assert max(diff_percentages) < 0.1


def test_brain_weight_gradients_relu_sigmoid():
    brain_topology = (
        (2, None),
        (3, ReLU),
        (1, Sigmoid),
    )

    # Make sure the difference between analytical and numerical calculation is less than 0.1%
    test_brain = Brain(brain_topology)
    diff_percentages = validate_weight_gradients(test_brain, test_samples)
    assert max(diff_percentages) < 0.1


def test_brain_weight_gradients_identity_sigmoid():
    brain_topology = (
        (2, None),
        (3, Identity),
        (1, Sigmoid),
    )

    # Make sure the difference between analytical and numerical calculation is less than 0.1%
    test_brain = Brain(brain_topology)
    diff_percentages = validate_weight_gradients(test_brain, test_samples)
    assert max(diff_percentages) < 0.1


def test_brain_weight_gradients_deep_mix():
    brain_topology = (
        (2, None),
        (3, Identity),
        (4, Sigmoid),
        (3, ReLU),
        (1, Sigmoid),
    )

    # Make sure the difference between analytical and numerical calculation is less than 0.1%
    test_brain = Brain(brain_topology)
    diff_percentages = validate_weight_gradients(test_brain, test_samples)
    assert max(diff_percentages) < 0.1


def validate_weight_gradients(brain, samples, verbose=False):

    # Initialize input and target of the network
    brain.convert_training_samples(samples)

    # Propagate input through the network to get the output / hypothesis
    brain.forward_prop()

    # Propagate backwards to calculate the gradients of the weights
    brain.back_prop()

    # Verify the calculated gradients by nudging each weight to get a numerical gradient
    nudge_step = 1e-4
    diff_percentages = []
    for index, cluster in enumerate(brain.synapse_clusters):
        print(f"Synapse cluster #{index + 1}")

        rows, cols = cluster.weights.shape
        for i in range(rows):
            for j in range(cols):

                # Nudge the weight up and down and calculate the cost difference
                orig_weight = cluster.weights[i, j]
                costs = []
                for nudge in (-nudge_step, nudge_step):
                    cluster.weights[i, j] = orig_weight + nudge
                    brain.forward_prop()
                    costs.append(brain.cost())

                est_gradient = (costs[1] - costs[0]) / (2 * nudge_step)
                diff_percent = (
                    abs(est_gradient - cluster.weight_gradients[i, j])
                    / max(1e-8, abs(cluster.weight_gradients[i, j]))
                    * 100
                )
                diff_percentages.append(diff_percent)

                if verbose:
                    print(
                        f"  weight[{i},{j}]: {cluster.weights[i, j]:7.3f} "
                        f"- gradient: {cluster.weight_gradients[i, j]:9.6f} "
                        f"- validation: {est_gradient:9.6f} "
                        f"- difference: {diff_percent:9.6f}%"
                    )

                # Restore the original weight! 😱
                cluster.weights[i, j] = orig_weight

    return diff_percentages
