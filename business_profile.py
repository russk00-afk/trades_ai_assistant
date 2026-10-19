import json
from pathlib import Path

from flask import Blueprint, render_template_string, request, redirect

profile_bp = Blueprint("profile", __name__)
PROFILE_FILE = Path("data/business_profile.json")

PROFILE_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Business Profile</title>
<style>
body {
    font-family: Arial, sans-serif;
    background: #f3f5f8;
    padding: 16px;
}
form {
    background: white;
    max-width: 600px;
    margin: auto;
    padding: 22px;
    border-radius: 12px;
}
input, textarea, select {
    display: block;
    width: 100%;
    box-sizing: border-box;
    padding: 12px;
    margin: 8px 0 18px;
    font-size: 16px;
}
button {
    background: #17365d;
    color: white;
    padding: 14px;
    border: none;
    border-radius: 8px;
    font-size: 16px;
}
</style>
</head>
<body>
<form method="post">
<h1>Business Profile</h1>
<p>These details will be used on your invoice drafts.</p>

<label>Business name</label>
<input name="business_name" required
value="{{ profile.get('business_name', '') }}">

<label>Business address</label>
<textarea name="address">{{ profile.get('address', '') }}</textarea>

<label>Email</label>
<input name="email" type="email"
value="{{ profile.get('email', '') }}">

<label>Telephone</label>
<input name="phone"
value="{{ profile.get('phone', '') }}">

<label>Country</label>
<input name="country" placeholder="e.g. Spain, UK"
value="{{ profile.get('country', '') }}">

<label>Currency</label>
<select name="currency">
{% for currency in ['EUR', 'GBP', 'USD'] %}
<option value="{{ currency }}"
{% if profile.get('currency', 'EUR') == currency %}selected{% endif %}>
{{ currency }}
</option>
{% endfor %}
</select>

<label>Tax identification number (if applicable)</label>
<input name="tax_id"
value="{{ profile.get('tax_id', '') }}">

<button type="submit">Save Business Profile</button>
<p><a href="/">Back to jobs</a></p>
</form>
</body>
</html>
"""


@profile_bp.route("/business-profile", methods=["GET", "POST"])
def business_profile():
    profile = {}

    if PROFILE_FILE.exists():
        profile = json.loads(
            PROFILE_FILE.read_text(encoding="utf-8")
        )

    if request.method == "POST":
        profile = {
            "business_name": request.form.get("business_name", "").strip(),
            "address": request.form.get("address", "").strip(),
            "email": request.form.get("email", "").strip(),
            "phone": request.form.get("phone", "").strip(),
            "country": request.form.get("country", "").strip(),
            "currency": request.form.get("currency", "EUR"),
            "tax_id": request.form.get("tax_id", "").strip()
        }

        if not profile["business_name"]:
            return "Business name is required", 400

        if profile["currency"] not in ("EUR", "GBP", "USD"):
            return "Invalid currency", 400

        PROFILE_FILE.parent.mkdir(parents=True, exist_ok=True)
        PROFILE_FILE.write_text(
            json.dumps(profile, indent=2),
            encoding="utf-8"
        )

        return redirect("/business-profile")

    return render_template_string(PROFILE_PAGE, profile=profile)
