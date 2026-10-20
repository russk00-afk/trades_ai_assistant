import re
from decimal import Decimal, InvalidOperation

def detect_charges(note):
    pattern = (
        r'(?:€\s*(\d+(?:[.,]\d{1,2})?)'
        r'|(?<![\d.,])(\d+(?:[.,]\d{1,2})?)\s*(?:euros?|EUR)\b)'
    )

    amounts = []

    for match in re.finditer(pattern, note, re.IGNORECASE):
        value = (match.group(1) or match.group(2)).replace(",", ".")
        try:
            amount = Decimal(value)
            if amount > 0:
                amounts.append({
                    "amount": str(amount.quantize(Decimal("0.01"))),
                    "currency": "EUR",
                    "approved": False
                })
        except InvalidOperation:
            continue

    return amounts

def classify_charges(note):
    """Identify likely costs and charges without changing invoices."""
    results = detect_charges(note)
    text = note.lower()

    for item in results:
        amount = item["amount"]
        number = amount.rstrip("0").rstrip(".")
        item["type"] = "needs_review"

        # Find the text immediately before this amount.
        matches = list(re.finditer(
            rf"(?:€\s*|\b){re.escape(number)}(?:\s*euros?|\s*EUR)?",
            text,
            re.IGNORECASE
        ))

        if not matches:
            continue

        context = text[max(0, matches[0].start() - 65):matches[0].start()]

        # Use the most recent phrase to help classify the amount.
        context = re.split(r"\band\b|[.;]", context)[-1]

        if re.search(r"\b(spent|paid|bought|purchased)\b", context):
            item["type"] = "material_or_job_cost"
        elif re.search(r"\b(quoted|charged|charge|price|extra cost)\b", context):
            item["type"] = "proposed_customer_charge"

    return results

def normalize_spoken_amounts(note):
    """Convert simple spoken euro amounts into digits."""
    from word2number import w2n

    number_words = (
        r"(?:zero|one|two|three|four|five|six|seven|eight|nine|"
        r"ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|"
        r"seventeen|eighteen|nineteen|twenty|thirty|forty|fifty|"
        r"sixty|seventy|eighty|ninety|hundred|thousand|million|and)"
    )

    pattern = re.compile(
        rf"\b((?:{number_words})(?:[\s-]+{number_words})*)"
        rf"\s+(euros?|EUR)\b",
        re.IGNORECASE
    )

    def convert(match):
        try:
            amount = w2n.word_to_num(match.group(1))
            return f"{amount} {match.group(2)}"
        except ValueError:
            return match.group(0)

    return pattern.sub(convert, note)
