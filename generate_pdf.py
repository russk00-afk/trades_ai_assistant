import json
from decimal import Decimal
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
)

JOBS_FILE = Path("data/jobs.json")
OUTPUT_DIR = Path("drafts")


def money(value):
    return f"EUR {Decimal(str(value)):,.2f}"


def safe(value):
    return escape(str(value))


def main(job_number=None):
    jobs = json.loads(JOBS_FILE.read_text(encoding="utf-8"))

    print("\n=== SELECT JOB FOR PDF ===")
    for i, job in enumerate(jobs, 1):
        print(f"{i}. {job['customer']}")

    choice = str(job_number) if job_number is not None else input("Enter job number: ").strip()
    if not choice.isdigit() or not 1 <= int(choice) <= len(jobs):
        print("Invalid job number.")
        return

    job = jobs[int(choice) - 1]
    OUTPUT_DIR.mkdir(exist_ok=True)
    filename = OUTPUT_DIR / f"invoice_draft_{choice}.pdf"

    styles = getSampleStyleSheet()
    styles["Title"].alignment = TA_CENTER

    doc = SimpleDocTemplate(str(filename), pagesize=A4)
    story = []

    story.append(Paragraph("INVOICE DRAFT", styles["Title"]))
    story.append(Paragraph(
        "NOT APPROVED - NOT FOR SENDING", styles["Heading2"]
    ))
    story.append(Spacer(1, 20))

    story.append(Paragraph(
        f"<b>Customer:</b> {safe(job['customer'])}",
        styles["Normal"]
    ))
    story.append(Paragraph(
        f"<b>Job:</b> {safe(job['job'])}",
        styles["Normal"]
    ))
    story.append(Spacer(1, 20))

    story.append(Paragraph("Work Notes", styles["Heading2"]))
    for note in job.get("notes", []):
        story.append(Paragraph(
            f"- {safe(note)}", styles["Normal"]
        ))

    story.append(Spacer(1, 20))
    story.append(Paragraph("Cost Breakdown", styles["Heading2"]))

    quote = Decimal(job["original_quote"])
    extras = job.get("potential_extras", [])

    rows = [
        ["Description", "Amount"],
        ["Original quote", money(quote)]
    ]

    extras_total = Decimal("0")
    for extra in extras:
        price = Decimal(extra["proposed_price"])
        extras_total += price
        rows.append([
            Paragraph(safe(extra["description"]), styles["Normal"]),
            money(price)
        ])

    rows.append(["Potential extras", money(extras_total)])
    rows.append(["Proposed total", money(quote + extras_total)])

    table = Table(rows, colWidths=[330, 130], repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BACKGROUND", (0, -1), (-1, -1), colors.whitesmoke),
    ]))
    story.append(table)

    story.append(Spacer(1, 25))
    story.append(Paragraph(
        "<b>IMPORTANT:</b> Potential extras are not confirmed "
        "as approved. Verify work, prices, VAT and customer "
        "approval before issuing a final invoice.",
        styles["Normal"]
    ))

    doc.build(story)
    print(f"\nPDF created: {filename}")


if __name__ == "__main__":
    main()
