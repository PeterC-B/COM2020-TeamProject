import os
import pytest
import networkx as nx
import geopandas as gpd
import pandas as pd
from shapely.geometry import LineString
import matplotlib.pyplot as plt
import numpy as np
import textwrap

from tests.utils.confusion_store import CONFUSION_MATRICES
from tests.utils.algorithm_store import ALGO_DIAGNOSTICS

# Fixtures
@pytest.fixture
def small_edges_gdf():
    data = {
        "length": [10.0, 20.0],
        "lit": [None, "yes"],
        "highway": ["residential", "path"],
        "surface": [None, "asphalt"],
        "geometry": [
            LineString([(0, 0), (1, 1)]),
            LineString([(1, 1), (2, 2)])
        ],
    }
    index = pd.MultiIndex.from_tuples(
        [(1, 2, 0), (2, 3, 0)],
        names=["u", "v", "key"]
    )
    return gpd.GeoDataFrame(data, index=index, crs="EPSG:4326")


@pytest.fixture
def small_graph():
    G = nx.MultiDiGraph()
    G.add_node(1, x=0, y=0)
    G.add_node(2, x=1, y=1)
    G.add_node(3, x=2, y=2)

    G.add_edge(1, 2, key=0, length=10.0, lit=None,
               highway="residential", surface=None)
    G.add_edge(2, 3, key=0, length=20.0, lit="yes",
               highway="path", surface="asphalt")

    return G

# Formatting helper
def _format_value_for_table(value, max_width=30):
    """
    Convert lists/dicts/paths into readable, wrapped, truncated strings
    suitable for matplotlib table cells
    """
    if isinstance(value, list):
        if all(isinstance(x, list) for x in value):
            formatted_paths = []
            for path in value:
                s = "→".join(str(n) for n in path)
                if len(s) > max_width:
                    s = s[:max_width] + "…"
                formatted_paths.append(s)
            text = "\n".join(formatted_paths)
        else:
            text = "→".join(str(n) for n in value)
            if len(text) > max_width:
                text = text[:max_width] + "…"
    else:
        text = str(value)

    return textwrap.fill(text, width=max_width)

# Combined Test Reporting
def pytest_sessionfinish(session, exitstatus):
    """
    After all tests finish, generate:
      - confusion_matrices.png
      - algorithm_diagnostics.png
    """
    os.makedirs("test_reports", exist_ok=True)

    # Confusion Matrix report builder
    if CONFUSION_MATRICES:
        n = len(CONFUSION_MATRICES)
        cols = 2
        rows = (n + 1) // cols

        fig, axes = plt.subplots(rows, cols, figsize=(10, 5 * rows))
        axes = axes.flatten()

        for ax, entry in zip(axes, CONFUSION_MATRICES):
            cm = entry["matrix"]
            labels = entry["labels"]
            name = entry["name"]

            im = ax.imshow(cm, cmap="Blues")
            ax.set_title(name)

            if labels:
                ax.set_xticks(np.arange(len(labels)))
                ax.set_yticks(np.arange(len(labels)))
                ax.set_xticklabels(labels)
                ax.set_yticklabels(labels)

            ax.set_xlabel("Predicted")
            ax.set_ylabel("Actual")

            for i in range(cm.shape[0]):
                for j in range(cm.shape[1]):
                    ax.text(j, i, cm[i, j], ha="center", va="center")

        for ax in axes[n:]:
            ax.axis("off")

        fig.tight_layout()
        fig.savefig("test_reports/confusion_matrices.png")
        plt.close(fig)

    # Algorithm Diagnostic report builder
    if ALGO_DIAGNOSTICS:
        n = len(ALGO_DIAGNOSTICS)
        cols = 2
        rows = (n + 1) // cols

        fig, axes = plt.subplots(rows, cols, figsize=(14, 5 * rows))
        axes = axes.flatten()

        for ax, entry in zip(axes, ALGO_DIAGNOSTICS):
            name = entry["name"]
            expected = entry["expected"]
            actual = entry["actual"]

            rows_data = []
            for key in expected:
                exp = _format_value_for_table(expected[key])
                act = _format_value_for_table(actual.get(key))
                match = "✓" if expected[key] == actual.get(key) else "✗"
                rows_data.append([key, exp, act, match])

            table = ax.table(
                cellText=rows_data,
                colLabels=["Field", "Expected", "Actual", "Match"],
                loc="center",
                cellLoc="left"
            )

            table.auto_set_font_size(False)
            table.set_fontsize(9)
            table.scale(1, 1.6)

            ax.set_title(name)
            ax.axis("off")

        for ax in axes[n:]:
            ax.axis("off")

        fig.tight_layout()
        fig.savefig("test_reports/algorithm_diagnostics.png")
        plt.close(fig)
