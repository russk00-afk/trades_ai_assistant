from business_profile import profile_bp
import json
from decimal import Decimal
from pathlib import Path

from flask import Flask, render_template_string, request, redirect, url_for

app = Flask(__name__)
app.register_blueprint(profile_bp)
from charge_review import charge_review_bp
app.register_blueprint(charge_review_bp)
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
<p><a href="/new-job">+ Add New Job</a></p><p><a href="/business-profile">Business Profile</a></p>
<h2>Saved Jobs</h2>

{% for item in jobs %}
<div class="card">
<div class="customer">{{ item.customer }}</div><p><a href="/update-job/{{ loop.index }}">Update Job</a></p>
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

<h3>Charges to Review</h3>
<ul>
{% for charge in item.review_items %}
<li>
<strong>{{ charge.description }}</strong> — EUR {{ charge.amount }}
<br>Source: {{ 'Work note' if charge.source == 'detected' else 'Manual entry' }}
<br>Status: {{ charge.status | title }}
{% if charge.status == 'pending' %}
{% if charge.source == 'detected' %}
<form method="post" action="{{ url_for('charge_review.review_charge', job_number=item.job_number, charge_index=charge.index) }}">
{% else %}
<form method="post" action="{{ url_for('charge_review.review_extra', job_number=item.job_number, extra_index=charge.index) }}">
{% endif %}
<button type="submit" name="decision" value="approved">Approve</button>
<button type="submit" name="decision" value="rejected">Reject</button>
</form>
{% endif %}
</li>
{% else %}
<li>No charges recorded</li>
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



FORM_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Add New Job</title>
<style>
body { font-family: Arial; background: #f3f5f8; padding: 20px; }
form { background: white; padding: 22px; border-radius: 12px; max-width: 550px; margin: auto; }
input, textarea { width: 100%; box-sizing: border-box; padding: 12px; margin: 8px 0 20px; font-size: 16px; }
button { background: #17365d; color: white; padding: 14px; border: 0; border-radius: 8px; font-size: 16px; }
</style>
</head>
<body>
<form method="post">
<h1>Add New Job</h1>
<label>Customer name</label>
<input name="customer" required maxlength="150">
<label>Job description</label>
<textarea name="job" required maxlength="2000"></textarea>
<label>Original quote (EUR)</label>
<input name="original_quote" type="number" step="0.01" min="0" required>
<button type="submit">Save Job</button>
<p><a href="/">Back to jobs</a></p>
</form>
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
    for job_number, job in enumerate(saved_jobs, start=1):
        quote = Decimal(job["original_quote"])
        extras = job.get("potential_extras", [])
        extras_total = sum(
            (Decimal(e["proposed_price"]) for e in extras if e.get("approved") is True),
            Decimal("0")
        )

        approved_charges_total = sum(
            (
                Decimal(str(c["amount"]))
                for c in job.get("detected_charges", [])
                if c.get("status") == "approved"
                and c.get("type") == "proposed_customer_charge"
            ),
            Decimal("0")
        )

        jobs.append({
            "job_number": job_number,
            "customer": job["customer"],
            "description": job["job"],
            "quote": money(quote),
            "notes": job.get("notes", []),
            "review_items": (
                [
                    {"source": "detected", "index": i, "amount": str(c.get("amount", "0")), "description": c.get("type", "Detected charge").replace("_", " ").title(), "status": c.get("status", "pending")}
                    for i, c in enumerate(job.get("detected_charges", []))
                ]
                +
                [
                    {"source": "manual", "index": i, "amount": str(e.get("proposed_price", "0")), "description": e.get("description", "Manual charge"), "status": e.get("status", "approved" if e.get("approved") else "pending")}
                    for i, e in enumerate(job.get("potential_extras", []))
                ]
            ),
            "detected_charges": job.get("detected_charges", []),
            "extras": [
                {
                    "description": e["description"],
                    "price": money(e["proposed_price"]), "status": e.get("status", "approved" if e.get("approved") else "pending")
                }
                for e in extras
            ],
            "extras_total": money(extras_total),
            "total": money(quote + extras_total + approved_charges_total)
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


@app.route("/new-job", methods=["GET", "POST"])
def new_job():
    if request.method == "POST":
        customer = request.form.get("customer", "").strip()
        description = request.form.get("job", "").strip()
        try:
            quote = Decimal(request.form.get("original_quote", ""))
        except Exception:
            return "Invalid quote", 400

        if not customer or not description or not quote.is_finite() or quote < 0:
            return "Invalid job details", 400

        jobs = []
        if JOBS_FILE.exists():
            jobs = json.loads(JOBS_FILE.read_text(encoding="utf-8"))

        jobs.append({
            "customer": customer,
            "job": description,
            "original_quote": str(quote.quantize(Decimal("0.01"))),
            "notes": [],
            "potential_extras": []
        })

        JOBS_FILE.parent.mkdir(parents=True, exist_ok=True)
        JOBS_FILE.write_text(json.dumps(jobs, indent=2), encoding="utf-8")
        return redirect(url_for("home"))

    return render_template_string(FORM_PAGE)


UPDATE_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Update Job</title>
<style>
body { font-family: Arial; background: #f3f5f8; padding: 16px; }
form { background: white; max-width: 550px; margin: auto;
padding: 20px; border-radius: 12px; }
input, textarea { width: 100%; box-sizing: border-box;
padding: 12px; margin: 8px 0 20px; font-size: 16px; }
button { background: #17365d; color: white; border: 0;
padding: 14px; border-radius: 8px; font-size: 16px; }
</style>
</head>
<body>
<form method="post">
<h1>Update Job</h1>
<h2>{{ job.customer }}</h2>
<p>{{ job.job }}</p>

<label>New work note</label>
<textarea name="note" placeholder="What happened on the job?"></textarea>

<label>Extra work description</label>
<textarea name="extra" placeholder="Describe additional work"></textarea>

<label>Proposed extra charge (EUR)</label>
<input name="price" type="number" min="0" step="0.01">

<button type="submit">Save Update</button>
<p><a href="/">Back to jobs</a></p>
</form>
</body>
</html>
"""

@app.route("/update-job/<int:job_number>", methods=["GET", "POST"])
def update_job(job_number):
    from flask import abort

    if not JOBS_FILE.exists():
        abort(404)

    jobs = json.loads(JOBS_FILE.read_text(encoding="utf-8"))

    if job_number < 1 or job_number > len(jobs):
        abort(404)

    job = jobs[job_number - 1]

    if request.method == "POST":
        note = request.form.get("note", "").strip()
        extra = request.form.get("extra", "").strip()
        price_text = request.form.get("price", "").strip()

        if not note and not extra and not price_text:
            return "Enter a note or extra work", 400

        if extra or price_text:
            if not extra or not price_text:
                return "Extra work requires a description and price", 400
            try:
                price = Decimal(price_text)
            except Exception:
                return "Invalid extra charge", 400

            if not price.is_finite() or price < 0:
                return "Invalid extra charge", 400

            price = price.quantize(Decimal("0.01"))

            job.setdefault("potential_extras", []).append({
                "description": extra,
                "proposed_price": str(price),
                "approved": False
            })

        if note:
            existing_notes = job.setdefault("notes", [])
            if any(n.strip().casefold() == note.casefold() for n in existing_notes):
                return "This work note has already been saved for this job.", 409
            existing_notes.append(note)

            # Detect possible charges without changing invoice totals.
            from charge_detector import classify_charges, normalize_spoken_amounts
            normalized_note = normalize_spoken_amounts(note)
            detected = classify_charges(normalized_note)

            if detected:
                for item in detected:
                    item["source_note"] = note
                    item["cost_amount"] = item["amount"] if item.get("type") == "material_or_job_cost" else None
                    item["customer_charge_amount"] = item["amount"] if item.get("type") == "proposed_customer_charge" else None
                    item["billing_decision"] = "unconfirmed"
                    item["reviewed"] = False

                job.setdefault("detected_charges", []).extend(detected)

        JOBS_FILE.write_text(
            json.dumps(jobs, indent=2), encoding="utf-8"
        )
        return redirect(url_for("home"))

    return render_template_string(UPDATE_PAGE, job=job)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
