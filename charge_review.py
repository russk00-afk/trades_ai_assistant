import json
from flask import Blueprint, request, redirect, abort
from pathlib import Path

charge_review_bp = Blueprint("charge_review", __name__)

@charge_review_bp.post("/review-charge/<int:job_number>/<int:charge_index>")
def review_charge(job_number, charge_index):
    jobs_file = Path("data/jobs.json")
    if not jobs_file.exists():
        abort(404)

    jobs = json.loads(jobs_file.read_text(encoding="utf-8"))
    if not 1 <= job_number <= len(jobs):
        abort(404)

    charges = jobs[job_number - 1].get("detected_charges", [])
    if not 0 <= charge_index < len(charges):
        abort(404)

    decision = request.form.get("decision")
    if decision not in ("approved", "rejected"):
        abort(400)

    charges[charge_index]["status"] = decision
    charges[charge_index]["reviewed"] = True

    jobs_file.write_text(json.dumps(jobs, indent=2), encoding="utf-8")
    return redirect("/")

@charge_review_bp.post("/review-extra/<int:job_number>/<int:extra_index>")
def review_extra(job_number, extra_index):
    jobs_file = Path("data/jobs.json")
    if not jobs_file.exists():
        abort(404)

    jobs = json.loads(jobs_file.read_text(encoding="utf-8"))
    if not 1 <= job_number <= len(jobs):
        abort(404)

    extras = jobs[job_number - 1].get("potential_extras", [])
    if not 0 <= extra_index < len(extras):
        abort(404)

    decision = request.form.get("decision")
    if decision not in ("approved", "rejected"):
        abort(400)

    extras[extra_index]["approved"] = decision == "approved"
    extras[extra_index]["status"] = decision
    extras[extra_index]["reviewed"] = True

    jobs_file.write_text(json.dumps(jobs, indent=2), encoding="utf-8")
    return redirect("/")
