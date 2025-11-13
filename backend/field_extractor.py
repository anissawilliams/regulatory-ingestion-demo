from transformers import pipeline

qa = pipeline("question-answering", model="deepset/roberta-large-squad2")

questions = {
    "billName": "What is the name or citation of this regulation or rule?",
    "docketNumber": "What is the docket number for this rule?",
    "jurisdiction": "Which agency or country issued this regulation?",
    "overview": "Summarize the purpose of this regulation in 2 sentences.",
    "requirements": "What are the reporting or compliance requirements for manufacturers?",
    "penalties": "What are the penalties for non-compliance?",
    "keyDates": "What are the key dates, including deadlines and effective dates?",
    "coveredProducts": "Which products or substances are covered by this regulation?",
    "exemptions": "What exemptions or exclusions are included in this regulation?"
}

def extract_fields(text):
    fields = {}
    for field, q in questions.items():
        result = qa(question=q, context=text)
        fields[field] = {
            "answer": result["answer"],
            "confidence": round(result["score"], 2)
        }
    return fields
