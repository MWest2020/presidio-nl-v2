from nlp.base import NLPEngine
from transformers import pipeline


class TransformersEngine(NLPEngine):
    def __init__(self, model_name: str = "GroNLP/bert-base-dutch-cased") -> None:
        """Initialiseer de Transformers-engine met een specifiek model.

        Args:
            model_name (str): Naam van het model dat gebruikt moet worden.
                Standaard is "GroNLP/bert-base-dutch-cased".
        """
        self.model_name = model_name
        self.ner_pipeline = pipeline(
            "ner", model=model_name, aggregation_strategy="simple"
        )

    def analyze(self, text: str, entities: list = None, language: str = "nl") -> list:
        results = []
        for ent in self.ner_pipeline(text):
            # Mapping van model-labels naar Presidio/standaard labels kan hier uitgebreid worden
            entity_type = ent.get("entity_group", ent.get("entity", ""))
            if entities is None or entity_type in entities:
                results.append(
                    {
                        "entity_type": entity_type,
                        "start": ent["start"],
                        "end": ent["end"],
                        "score": ent["score"],
                        "text": ent["word"]
                        if "word" in ent
                        else text[ent["start"] : ent["end"]],
                    }
                )
        return results
