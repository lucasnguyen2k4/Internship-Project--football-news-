import json
import csv
import os
from collections import defaultdict

json_path = "data/football.json-master/2024-25/uefa.el.json"
with open(json_path, "r", encoding="utf-8") as f:
    data = json.load(f)
league_name = data["name"].strip()
club_leagues = defaultdict(set)
CLUB_NORMALIZATION = {
    "Inter": "FC Internazionale Milano",
    "Roma": "AS Roma",
    "Lazio": "SS Lazio",
    "Feyenoord": "Feyenoord Rotterdam",
    "Ajax": "AFC Ajax",
    "Rangers": "Rangers FC",
    "Celtic": "Celtic FC",
    "Braga": "SC Braga",
    "Betis": "Real Betis Balompié",
}

for match in data.get("matches", []):
    for team_key in ["team1", "team2"]:
        team = match.get(team_key, "").strip()
        if not team:
            continue
        team = CLUB_NORMALIZATION.get(team, team)
        club_leagues[team].add(league_name)

csv_path = "european_clubs_in_leagues.csv"

existing = set()
if os.path.exists(csv_path):
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader, None) 
        for row in reader:
            if len(row) >= 2:
                existing.add((row[0], row[1]))
new_rows = []
for club, leagues in club_leagues.items():
    for league in leagues:
        if (club, league) not in existing:
            print(f"New club entry found: {club} in {league}")
            new_rows.append((club, league))
            existing.add((club, league))

write_header = not os.path.exists(csv_path)
with open(csv_path, "a", newline='', encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)
    if write_header:
        writer.writerow(["club_name", "league_name"])
    for row in new_rows:
        writer.writerow(row)

print(f"Added {len(new_rows)} new clubs from league: {league_name}")
