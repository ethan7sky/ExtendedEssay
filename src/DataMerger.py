import json
from collections import defaultdict, Counter

def aggregate_datasets(java_file, python_file, output_file):
    problems = {}

    def process_line(line):
        data = json.loads(line)
        pid = data["problem"]
        tags = data["tags"]
        complexity = data.get("complexity")

        if pid not in problems:
            problems[pid] = {
                "problem_id": pid,
                "tags": tags,
                "total_examples": 0,
                "complexity_counts": Counter()
            }

        problems[pid]["total_examples"] += 1
        if complexity:
            problems[pid]["complexity_counts"][complexity] += 1

    for filename in [java_file, python_file]:
        with open(filename, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    process_line(line)

    with open(output_file, "w", encoding="utf-8") as out:
        for pid, pdata in problems.items():
            pdata["complexity_counts"] = dict(pdata["complexity_counts"])
            out.write(json.dumps(pdata) + "\n")


if __name__ == "__main__":
    aggregate_datasets(r"../data/java_data.jsonl", r"../data/python_data.jsonl", r"../data/data.jsonl")
    print("Merged dataset written to data.jsonl")