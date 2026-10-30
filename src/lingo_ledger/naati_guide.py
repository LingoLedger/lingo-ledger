"""Step-by-step guide for a person searching the NAATI online directory by hand.

Builds instructions only. It makes no requests to NAATI's site, and it never
queries the directory or stores results. A person runs the search themselves.
"""

from __future__ import annotations

from lingo_ledger.brief import validate_brief

DIRECTORY_URL = "https://directory.naati.com.au/"

# Brief purpose -> NAATI "Domain" field value shown on the directory search form.
PURPOSE_TO_DOMAIN = {
    "immigration": "Immigration",
    "court": "Legal",
    "regulatory": "Legal",
    "medical": "Health",
    "other": None,
}

# Brief certification -> NAATI "Certification type" option.
NAATI_CERT_TYPES = {
    "NAATI": ["Certified", "Recognised", "Specialist Health or Legal"],
}


def naati_search_steps(brief: dict) -> dict:
    """Return the directory URL and ordered steps for a manual NAATI search."""
    check = validate_brief(brief)
    if not check.ok:
        raise ValueError("invalid brief: " + "; ".join(check.errors))

    if "NAATI" not in brief["certifications"]:
        raise ValueError("this brief does not accept NAATI certification")

    source = brief["source_lang"]
    target = brief["target_lang"]
    domain = PURPOSE_TO_DOMAIN.get(brief["purpose"])
    cert_types = NAATI_CERT_TYPES["NAATI"]

    steps = [
        f"Open {DIRECTORY_URL}.",
        "Choose Type: Translator (or Interpreter, if the job is interpreting).",
        f"Under Languages, choose translate from {source} and translate into {target} "
        f"(also check {target} to {source} if you want translators who work both ways).",
        "Under Certification type, tick: " + ", ".join(cert_types) + ".",
    ]
    if domain:
        steps.append(f"Under Domain, choose {domain}.")
    steps.append("Click Show Advanced Search if you need more filters, then Find results.")
    steps.append(
        "For each practitioner you want to contact, note the name and the details they "
        "chose to display, then contact them only after the customer approves the message."
    )
    return {"url": DIRECTORY_URL, "steps": steps}
