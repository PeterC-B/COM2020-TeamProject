from app import create_app
from app.extensions import db
from app.models.missions_model import MissionsModel
from app.models.enums.MISSION_TIER import MissionTier
from csv import DictReader

app = create_app()
app.app_context().push()

tier_map = {
    "Easy": MissionTier.EASY,
    "Medium": MissionTier.MEDIUM,
    "Hard": MissionTier.HARD
}

def read_csv(csv_path : str = "data/processed/missions.csv") -> dict[str, str]:
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = DictReader(f)
        result = {}
        for idx, row in enumerate(reader):
            result[idx] = row
    return result

def execute():
    missions_csv = read_csv()
    entries = []

    for mission in missions_csv.values():
        m = MissionsModel(
            mission_name=mission['Mission Name'],
            tier=tier_map[mission['Tier']],
            question=mission['Question:'],
            possible_answers=mission['4 answers (comma seperated)'],
            answer=mission['Correct Answer']
        )
        entries.append(m)
        db.session.add(m)

    db.session.commit()

    print(f"Seeded {len(missions_csv.keys())} missions from CSV")