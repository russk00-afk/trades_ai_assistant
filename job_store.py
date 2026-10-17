import json
from pathlib import Path

DATA_DIR = Path("data")
JOBS_FILE = DATA_DIR / "jobs.json"


def load_jobs():
    DATA_DIR.mkdir(exist_ok=True)
    if not JOBS_FILE.exists():
        return []
    with JOBS_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def save_job(job):
    jobs = load_jobs()
    jobs.append(job)
    DATA_DIR.mkdir(exist_ok=True)
    with JOBS_FILE.open("w", encoding="utf-8") as file:
        json.dump(jobs, file, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    example_job = {
        "customer": "Test Customer",
        "job": "Bathroom renovation",
        "original_quote": "2400.00",
        "notes": [
            "Replaced damaged pipe behind wall",
            "Customer informed about additional work"
        ],
        "potential_extras": [
            {
                "description": "Additional pipe fittings and labour",
                "proposed_price": "150.00",
                "approved": False
            }
        ]
    }

    save_job(example_job)
    print(f"Saved {len(load_jobs())} job record(s) to {JOBS_FILE}")
