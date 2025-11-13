def tag_text(text):
    tags = []
    keywords = {
        "pfas": "regulated_substance",
        "textile": "product_type",
        "exemption": "compliance",
        "penalty": "enforcement",
        "reporting": "requirement"
    }
    for word, category in keywords.items():
        if word in text.lower():
            tags.append((word, category))
    return tags
