import json
from decimal import Decimal
from pathlib import Path

JOBS_FILE = Path("data/jobs.json")


def money(value):
    return f"\u20ac{Decimal(str(value)):,.2f}"


def main():
    if not JOBS_FILE.exists():
        print("No saved jobs found.")
        return

    with JOBS_FILE.open(encoding="utf-8") as file:
        jobs = json.load(file)

    if not jobs:
        print("No saved jobs found.")
        return

    print("\n=== TRADES AI ASSISTANT: JOB REVIEW ===")

    for index, job in enumerate(jobs, start=1):
        print("\n" + "=" * 42)
        print(f"JOB {index}: {job.get('customer', 'Unknown')}")
        print(f"Description: {job.get('job', 'Not entered')}")
        print(f"Original quote: {money(job.get('original_quote', '0'))}")
        print(f"Status: {job.get('status', 'draft')}")

        print("\nWork notes:")
        notes = job.get("notes", [])
        if notes:
            for note in notes:
                print(f"- {note}")
        else:
            print("- No notes recorded")

        print("\nPotential extras — approval not confirmed:")
        extras = job.get("potential_extras", [])
        if extras:
            for extra in extras:
                print(
                    f"- {extra['description']}: "
                    f"{money(extra['proposed_price'])}"
                )
                print(f"  Approved: {extra.get('approved', False)}")
        else:
            print("- No potential extras recorded")

        extras_total = sum(
            (
                Decimal(extra["proposed_price"])
                for extra in extras
            ),
            Decimal("0")
        )
        print(f"\nPotential extras total: {money(extras_total)}")
        print(f"Proposed total for review: "
              f"{money(Decimal(job.get('original_quote', '0')) + extras_total)}")
        print("Reminder: verify the work, pricing, VAT and approval.")

    print("\nThis is a review aid, not an automatic invoice approval.")


if __name__ == "__main__":
    main()
