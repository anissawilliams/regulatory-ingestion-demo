from regulation_scraper import scrape_url
from field_extractor import extract_fields
from auto_tagger import tag_text
import json

url = "https://www.epa.gov/assessing-and-managing-chemicals-under-tsca/tsca-section-8a7-reporting-and-recordkeeping"
reg = scrape_url(url, source="EPA")
fields = extract_fields(reg["full_text"])
tags = tag_text(reg["full_text"])

regulation = {
    "id": fields["billName"]["answer"].lower().replace(" ", "-").replace("/", "-"),
    "jurisdiction": fields["jurisdiction"]["answer"],
    "bill": fields["billName"]["answer"],
    "docket": fields["docketNumber"]["answer"],
    "status": "final",
    "confidence": round(sum(f["confidence"] for f in fields.values()) / len(fields), 2),
    "lastUpdated": "2025-11-13",
    "sourceUrls": [url],
    "fields": fields,
    "tags": tags
}

with open("../frontend/public/regulations.json", "w") as f:
    json.dump([regulation], f, indent=2)
