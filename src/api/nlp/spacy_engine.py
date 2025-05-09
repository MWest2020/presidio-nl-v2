import spacy

from src.api.nlp.base import NLPEngine


class SpacyEngine(NLPEngine):
    def __init__(self, model_name: str = "nl_core_news_md") -> None:
        self.model_name = model_name
        self.nlp = spacy.load(model_name)

    def analyze(self, text: str, entities: list = None, language: str = "nl") -> list:
        doc = self.nlp(text)
        results = []
        for ent in doc.ents:
            if entities is None or ent.label_ in entities:
                results.append(
                    {
                        "entity_type": ent.label_,
                        "start": ent.start_char,
                        "end": ent.end_char,
                        "score": 0.85,  # SpaCy geeft geen scores, default
                        "text": ent.text,
                    }
                )
        return results
