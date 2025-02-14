import csv
import datetime
from pathlib import Path

csv_path = Path("../../../src/agt_server/server/results/lemonade/data.csv")
txt_path = Path("../../../../../www/leaderboard/boards/LemonadeArena.txt")

agents = []
with csv_path.open(mode="r", encoding="utf-8") as file:
    reader = csv.reader(file)
    next(reader, None)
    for row in reader:
        if len(row) < 4:
            continue
        agent_name = row[1]
        final_score = row[3]
        try:
            score = float(final_score)
            agents.append((agent_name, score))
        except ValueError:
            continue  


timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H%M")
formatted_result = f"{timestamp}\t" + "\t".join(f"{name}\t{score:.2f}" for name, score in agents)

with txt_path.open(mode="a", encoding="utf-8") as file:
    file.write(formatted_result + "\n")