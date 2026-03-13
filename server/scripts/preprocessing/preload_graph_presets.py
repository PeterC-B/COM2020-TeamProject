import sys
from pathlib import Path

SERVER_ROOT = Path(__file__).resolve().parents[2]
if str(SERVER_ROOT) not in sys.path:
    sys.path.insert(0, str(SERVER_ROOT))

from app import create_app
from app.extensions import db
from app.repositories.graph_data_repository import GraphDataRepository
from app.unit_of_work.sqlalchemy_uow import SqlAlchemyUnitOfWork
from app.use_cases.graph.get_graph_data_for_coords import FetchDataForCoordinates


def main():
    app = create_app()
    with app.app_context():
        session = db.session
        graph_repo = GraphDataRepository(session)
        graph_repo.ensure_default_presets()

        fetch_graph_data = FetchDataForCoordinates(
            SqlAlchemyUnitOfWork(session),
            graph_repo,
        )

        presets = graph_repo.list_graph_presets()

        for preset in presets:
            code = preset["code"]
            name = preset["name"]
            lat = preset["lat"]
            lon = preset["lon"]

            print(f"Loading {name} ({code})")
            snapshot = fetch_graph_data.execute((lat, lon))
            graph_repo.upsert_graph_preset_snapshot(code, snapshot)
            print(f"Saved {code}")

        print("Done")


if __name__ == "__main__":
    main()
