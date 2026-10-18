import json
from decimal import Decimal
from pathlib import Path

JOBS_FILE = Path("data/jobs.json")
OUTPUT_DIR = Path("drafts")


def money(value):
    return f"€{Decimal(str(value)):,.2f}"


def main():
    if not JOBS_FILE.exists():
        print("No saved jobs found.")
        return

    jobs = json.loads(JOBS_FILE.read_text(encoding="utf-8"))

    if not jobs:
        print("No saved jobs found.")
        return

    print("\n=== SELECT A SAVED JOB ===")
    for number, job in enumerate(jobs, 1):
        print(f"{number}. {job['customer']} - {job['job']}")

    choice = input("\nEnter job number: ").strip()

    if not choice.isdigit() or not 1 <= int(choice) <= len(jobs):
        print("Invalid job number.")
        return

    job = jobs[int(choice) - 1]
    quote = Decimal(job["original_quote"])
    extras = job.get("potential_extras", [])
    extras_total = sum(
        (Decimal(e["proposed_price"]) for e in extras),
        Decimal("0")
    )

    lines = [
        "INVOICE DRAFT - NOT APPROVED",
        "=" * 35,
        f"Customer: {job['customer']}",
        f"Job: {job['job']}",
        f"Original quote: {money(quote)}",
        "",
        "WORK NOTES:",
    ]

    lines.extend(f"- {note}" for note in job.get("notes", []))

    lines.append("")
    lines.append("POTENTIAL EXTRAS - APPROVAL REQUIRED:")

    for extra in extras:
        lines.append(
            f"- {extra['description']}: "
            f"{money(extra['proposed_price'])}"
        )

    lines.extend([
        "",
        f"Potential extras total: {money(extras_total)}",
        f"Proposed total for review: {money(quote + extras_total)}",
        "",
        "DRAFT ONLY. Verify work, prices, VAT and approval.",
        "Do not send as a final invoice."
    ])

    OUTPUT_DIR.mkdir(exist_ok=True)
    filename = OUTPUT_DIR / f"invoice_draft_{choice}.txt"
    filename.write_text("\n".join(lines), encoding="utf-8")

    print(f"\nDraft created: {filename}")
    print("\n" + "\n".join(lines))


if __name__ == "__main__":
    main()
