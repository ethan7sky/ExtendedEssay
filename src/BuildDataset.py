import json
import pandas as pd
from tqdm import tqdm
from WebScraper import fetch_and_clean_one
from FeatureExtractor import extract_features

input_file = r"../data/data.jsonl"
with open(input_file, "r", encoding="utf-8") as f:
    problems = [json.loads(line) for line in f]
print(f"Loaded {len(problems)} problems.")

request_delay = 1.5
results = []

for idx, problem_meta in enumerate(tqdm(problems, desc="Processing problems")):
    problem_id = problem_meta["problem_id"]

    contest_id, index = problem_id.split("_")
    contest_id = str(int(contest_id))
    problem_id = f"{contest_id}_{index}" 

    try:
        cleaned_text = fetch_and_clean_one(problem_id, delay=request_delay)
        if not cleaned_text:
            print(f"[Skipped] Failed to fetch {problem_id}")
            continue

        features = extract_features(
            problem_id=problem_id,
            cleaned_text=cleaned_text,
            tags=problem_meta["tags"],
            complexity_counts=problem_meta["complexity_counts"]
        )

        features.update({
            "problem_id": problem_id,
            "tags": problem_meta["tags"],
            "total_examples": problem_meta["total_examples"],
            "complexity_counts": problem_meta["complexity_counts"]
        })

        results.append(features)

    except Exception as e:
        print(f"[Error] {problem_id}: {e}")

df = pd.DataFrame(results)
df.to_csv("final_dataset.csv", index=False)
df.to_parquet("final_dataset.parquet", index=False)

print(f"Saved {len(df)} problems to final_dataset.csv / final_dataset.parquet")
