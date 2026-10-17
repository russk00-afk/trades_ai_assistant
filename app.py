import json
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from uuid import uuid4

DATA_DIR = Path("data")
JOBS_FILE = DATA_DIR / "jobs.json"


def money(amount):
    return f"\u20ac{amount:,.2f}"


def read_price(prompt):
    while True:
        try:
            price = Decimal(input(prompt).strip().replace(",", "."))
            if price.is_finite() and price >= 0:
                return price
        except InvalidOperation:
            pass
        print("Enter a valid amount, such as 2400 or 25.50.")


def load_jobs():
    DATA_DIR.mkdir(exist_ok=True)
    if not JOBS_FILE.exists():
        return []
    with JOBS_FILE.open(encoding="utf-8") as file:
        return json.load(file)


def main():
    print("\n=== TRADES AI ASSISTANT ===")
    print("Create and save a job record\n")

    customer = input("Customer name: ").strip()
    description = input("Job description: ").strip()
    quote = read_price("Original quote in euros: ")

    notes = []
    print("\nEnter job notes. Blank line finishes.")
    while True:
        note = input("Job note: ").strip()
        if not note:
            break
        notes.append(note)

    extras = []
    print("\nEnter each EXTRA job separately, with its own price. Do NOT enter the new total here. Blank description finishes.")
    while True:
        item = input("Extra work description: ").strip()
        if not item:
            break
        price = read_price("Proposed extra price in euros: ")
        extras.append({
            "description": item,
            "proposed_price": str(price),
            "approved": False
        })

    extras_total = sum(
        (Decimal(extra["proposed_price"]) for extra in extras),
        Decimal("0")
    )
    proposed_total = quote + extras_total

    job_record = {
        "id": str(uuid4()),
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "customer": customer,
        "job": description,
        "original_quote": str(quote),
        "notes": notes,
        "potential_extras": extras,
        "status": "draft"
    }

    jobs = load_jobs()
    jobs.append(job_record)

    with JOBS_FILE.open("w", encoding="utf-8") as file:
        json.dump(jobs, file, indent=2, ensure_ascii=False)

    print("\n=== INVOICE DRAFT ===")
    print(f"Customer: {customer}")
    print(f"Job: {description}")
    print(f"Original quote: {money(quote)}")

    print("\nJob notes:")
    for note in notes:
        print(f"- {note}")
    if not notes:
        print("- None entered")

    print("\nPotential extras — review required:")
    for extra in extras:
        print(f"- {extra['description']}: "
              f"{money(Decimal(extra['proposed_price']))}")
    if not extras:
        print("- None entered")

    print(f"\nPotential extras total: {money(extras_total)}")
    print(f"Proposed total: {money(proposed_total)}")
    print("\nDraft only. Check VAT and customer approval.")
    print(f"Job saved with ID: {job_record['id']}")
    print(f"Total stored job records: {len(jobs)}")
    print(f"Records saved in: {JOBS_FILE}")


if __name__ == "__main__":
    main()
