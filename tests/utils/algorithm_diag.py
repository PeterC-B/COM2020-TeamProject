from tests.utils.algorithm_store import ALGO_DIAGNOSTICS

def log_algorithm_diagnostic(name, expected, actual):
    """
    Store a diagnostic entry for later visualisation
    expected and actual should be dicts with comparable fields
    """
    ALGO_DIAGNOSTICS.append({
        "name": name,
        "expected": expected,
        "actual": actual
    })
