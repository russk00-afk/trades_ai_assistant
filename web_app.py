import json
from decimal import Decimal
from pathlib import Path

from flask import Flask, render_template_string

app = Flask(__name__)
JOBS_FILE = Path("data/jobs.json")


def money(value):
    return f"{Decimal(str(value)):,.2f}"


PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Trades AI Assistant</title>
<style>
body {
    font-family: Arial, sans-serif;
    background: #f3f5f8;
    margin: 0;
    padding: 16px;
    color: #263445;
}
.container { max-width: 750px; margin: auto; }
h1 { color: #17365d; }
.card {
    background: white;
    padding: 20px;
    margin-bottom: 20px;
    border-radius: 12px;
    box-shadow: 0 2px 8px #ddd;
}
.customer { font-size: 22px; font-weight: bold; }
.status { color: #a36a00; }
.total {
    font-size: 20px;
    font-weight: bold;
    color: #17365d;
}
.warning {
    background: #fff3d6;
    padding: 12px;
    border-radius: 8px;
    font-size: 14px;
}
li { margin-bottom: 8px; }
</style>
</head>
<body>
<div class="container">
<h1>Trades AI Assistant</h1>
<p>Your jobs, quotes and paperwork in one place.</p>
<h2>Saved Jobs</h2>

{% for item in jobs %}
<div class="card">
<div class="customer">{{ item.customer }}</div>
<p>{{ item.description }}</p>
<p class="status">Status: Draft</p>

<h3>Original Quote</h3>
<p>EUR {{ item.quote }}</p>

<h3>Work Notes</h3>
<ul>
{% for note in item.notes %}
<li>{{ note }}</li>
{% else %}
<li>No notes recorded</li>
{% endfor %}
</ul>

<h3>Potential Extras</h3>
<ul>
{% for extra in item.extras %}
<li>{{ extra.description }}:
EUR {{ extra.price }} — Approval required</li>
{% else %}
<li>No extras recorded</li>
{% endfor %}
</ul>

<p>Potential extras total: EUR {{ item.extras_total }}</p>
<p class="total">Proposed total: EUR {{ item.total }}</p>


<p>
<a href="/download/{{ loop.index }}"
   style="display:inline-block;background:#17365d;
   color:white;padding:12px 18px;border-radius:8px;
   text-decoration:none;font-weight:bold;">
   Download Draft PDF
</a>
</p>

<div class="warning">
DRAFT ONLY. Verify work, pricing, tax and customer
approval before issuing an invoice.
</div>
</div>
{% else %}
<p>No jobs saved yet.</p>
{% endfor %}
</div>
</body>
</html>
"""


@app.route("/")
def home():
    saved_jobs = []
    if JOBS_FILE.exists():
        saved_jobs = json.loads(
            JOBS_FILE.read_text(encoding="utf-8")
        )

    jobs = []
    for job in saved_jobs:
        quote = Decimal(job["original_quote"])
        extras = job.get("potential_extras", [])
        extras_total = sum(
            (Decimal(e["proposed_price"]) for e in extras),
            Decimal("0")
        )

        jobs.append({
            "customer": job["customer"],
            "description": job["job"],
            "quote": money(quote),
            "notes": job.get("notes", []),
            "extras": [
                {
                    "description": e["description"],
                    "price": money(e["proposed_price"])
                }
                for e in extras
            ],
            "extras_total": money(extras_total),
            "total": money(quote + extras_total)
        })

    return render_template_string(PAGE, jobs=jobs)


@app.route("/download/<int:job_number>")
def download_pdf(job_number):
    from flask import abort, send_file

    jobs = json.loads(JOBS_FILE.read_text(encoding="utf-8"))
    if job_number < 1 or job_number > len(jobs):
        abort(404)

    from generate_pdf import main as generate_invoice_pdf
    generate_invoice_pdf(job_number)

    pdf = Path("drafts") / f"invoice_draft_{job_number}.pdf"
    if not pdf.is_file():
        abort(404, description="Draft PDF has not been generated yet.")

    return send_file(pdf.resolve(), as_attachment=True,
                     download_name=pdf.name)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
