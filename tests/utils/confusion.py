from sklearn.metrics import confusion_matrix
from tests.utils.confusion_store import CONFUSION_MATRICES

def assert_confusion(actual, predicted, labels=None, name=None):
    """
    Compute a confusion matrix, identify correctness, and store it globally
    """
    cm = confusion_matrix(actual, predicted, labels=labels)

    # Store for later visualisation
    CONFUSION_MATRICES.append({
        "name": name or "Unnamed Test",
        "matrix": cm,
        "labels": labels
    })

    # Identify correctness
    if cm.trace() != cm.sum():
        raise AssertionError(f"Confusion matrix mismatch:\n{cm}")

    return cm
