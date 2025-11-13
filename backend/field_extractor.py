import re
from datetime import datetime


def extract_fields(text, url=""):
    """Fast rule-based field extraction for regulatory text"""

    # Debug: check if we actually have content
    if not text or len(text) < 100:
        print(f"⚠️ Warning: Very short text ({len(text)} chars)")
        return create_empty_fields()

    fields = {}

    # 1. Bill Name / Citation
    cfr_match = re.search(r'(\d+)\s+CFR\s+(Part\s+)?(\d+)(?:\.(\d+))?', text, re.IGNORECASE)
    if cfr_match:
        bill_name = cfr_match.group(0)
    else:
        # Try to get from first heading or title
        lines = [l.strip() for l in text.split('\n') if len(l.strip()) > 10]
        bill_name = lines[0][:200] if lines else "Unknown"

    fields["billName"] = {
        "answer": bill_name,
        "confidence": 0.95 if cfr_match else 0.5
    }

    # 2. Docket Number
    docket_match = re.search(r'(EPA|FDA|OSHA)-\d{4}-[A-Z]-\d+', text, re.IGNORECASE)
    fields["docketNumber"] = {
        "answer": docket_match.group(0) if docket_match else "Not found",
        "confidence": 0.95 if docket_match else 0.0
    }

    # 3. Jurisdiction (detect from URL or text)
    if "epa.gov" in url.lower() or "epa" in text[:500].lower():
        jurisdiction = "EPA"
        confidence = 0.95
    elif "fda.gov" in url.lower() or "fda" in text[:500].lower():
        jurisdiction = "FDA"
        confidence = 0.95
    elif "osha.gov" in url.lower() or "osha" in text[:500].lower():
        jurisdiction = "OSHA"
        confidence = 0.95
    else:
        agency_match = re.search(r'\b(EPA|FDA|OSHA|Department of [A-Z][a-z]+)\b', text[:1000])
        jurisdiction = agency_match.group(0) if agency_match else "Federal"
        confidence = 0.7 if agency_match else 0.3

    fields["jurisdiction"] = {
        "answer": jurisdiction,
        "confidence": confidence
    }

    # 4. Overview (first substantial paragraph)
    paragraphs = [p.strip() for p in text.split('\n') if len(p.strip()) > 100]
    overview = paragraphs[0][:500] + "..." if paragraphs else "Not found"
    fields["overview"] = {
        "answer": overview,
        "confidence": 0.7 if paragraphs else 0.0
    }

    # 5. Requirements (look for "shall", "must", "required")
    requirement_pattern = r'[^.!?]*(?:shall|must|required to|is required)[^.!?]*[.!?]'
    requirements = re.findall(requirement_pattern, text, re.IGNORECASE)
    req_text = " ".join(requirements[:3]) if requirements else "Not found"
    fields["requirements"] = {
        "answer": req_text,
        "confidence": 0.8 if requirements else 0.0
    }

    # 6. Penalties
    penalty_pattern = r'[^.!?]*(?:penalty|penalties|fine|fines|violation|violator)[^.!?]*[.!?]'
    penalties = re.findall(penalty_pattern, text, re.IGNORECASE)
    fields["penalties"] = {
        "answer": " ".join(penalties[:2]) if penalties else "Not specified",
        "confidence": 0.8 if penalties else 0.0
    }

    # 7. Key Dates
    date_patterns = [
        r'\b\d{1,2}/\d{1,2}/\d{4}\b',
        r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b',
        r'\b\d{4}-\d{2}-\d{2}\b'
    ]
    dates = []
    for pattern in date_patterns:
        dates.extend(re.findall(pattern, text))
    fields["keyDates"] = {
        "answer": "; ".join(list(set(dates))[:5]) if dates else "Not specified",
        "confidence": 0.9 if dates else 0.0
    }

    # 8. Covered Products
    product_keywords = r'\b(?:chemical|substance|material|product|packaging|container|device|equipment)s?\b'
    product_sentences = re.findall(r'[^.!?]*' + product_keywords + r'[^.!?]*[.!?]', text[:5000], re.IGNORECASE)
    if product_sentences:
        covered = product_sentences[0][:300]
        confidence = 0.7
    else:
        covered = "Not specified"
        confidence = 0.0
    fields["coveredProducts"] = {
        "answer": covered,
        "confidence": confidence
    }

    # 9. Exemptions
    exemption_pattern = r'[^.!?]*(?:exempt|exemption|exception|excluded|does not apply)[^.!?]*[.!?]'
    exemptions = re.findall(exemption_pattern, text, re.IGNORECASE)
    fields["exemptions"] = {
        "answer": " ".join(exemptions[:2]) if exemptions else "None specified",
        "confidence": 0.8 if exemptions else 0.0
    }

    return fields


def create_empty_fields():
    """Return empty fields when no content available"""
    return {
        field: {"answer": "Not found", "confidence": 0.0}
        for field in ["billName", "docketNumber", "jurisdiction", "overview",
                      "requirements", "penalties", "keyDates", "coveredProducts", "exemptions"]
    }