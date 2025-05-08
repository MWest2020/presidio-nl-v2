from presidio_analyzer import AnalyzerEngine, RecognizerRegistry
from presidio_analyzer.nlp_engine import NlpEngineProvider
from anonymizer.recognizers.patterns import (
    DutchPhoneNumberRecognizer, DutchIBANRecognizer, DutchEmailRecognizer
)
from nlp.loader import load_nlp_engine

class ModularTextAnalyzer:
    """Modulaire analyzer-klasse voor Nederlandse tekst."""
    def __init__(self, nlp_config_path=None, nlp_config_dict=None):
        # Laad de modulaire NLP-engine
        self.nlp_engine = load_nlp_engine(nlp_config_path, nlp_config_dict)

        # Voeg een minimale SpaCy-engine toe voor Presidio pattern recognizers
        spacy_config = {
            "nlp_engine_name": "spacy",
            "models": [{"lang_code": "nl", "model_name": "nl_core_news_md"}]
        }
        spacy_provider = NlpEngineProvider(nlp_configuration=spacy_config)
        presidio_spacy_engine = spacy_provider.create_engine()

        # Maak een registry aan en voeg custom recognizers toe
        registry = RecognizerRegistry()
        registry.supported_languages = ["nl"]
        registry.add_recognizer(DutchPhoneNumberRecognizer())
        registry.add_recognizer(DutchIBANRecognizer())
        registry.add_recognizer(DutchEmailRecognizer())

        # Initialiseer de AnalyzerEngine met SpaCy-engine voor pattern recognizers
        self.analyzer = AnalyzerEngine(
            nlp_engine=presidio_spacy_engine,
            registry=registry,
            supported_languages=["nl"]
        )

    def analyze_text(self, text: str, entities: list = None, language: str = "nl"):
        # Gebruik de modulaire NLP-engine voor NER
        nlp_results = self.nlp_engine.analyze(text, entities, language)
        # Gebruik de pattern recognizers via Presidio AnalyzerEngine
        pattern_results = self.analyzer.analyze(
            text=text,
            entities=entities,
            language=language
        )
        # Combineer resultaten (dedupliceer op start-end-entity_type)
        all_results = nlp_results + [
            {
                "entity_type": r.entity_type,
                "start": r.start,
                "end": r.end,
                "score": r.score,
                "text": text[r.start:r.end]
            }
            for r in pattern_results
        ]
        # Deduplicatie (optioneel: op basis van start, end, entity_type)
        seen = set()
        unique_results = []
        for r in all_results:
            key = (r["start"], r["end"], r["entity_type"])
            if key not in seen:
                unique_results.append(r)
                seen.add(key)
        return unique_results 