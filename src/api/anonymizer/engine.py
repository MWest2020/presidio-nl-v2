import logging

from presidio_analyzer import AnalyzerEngine, RecognizerRegistry
from presidio_analyzer.nlp_engine import NlpEngineProvider

from src.api.anonymizer.recognizers.patterns import (
    DutchEmailRecognizer,
    DutchIBANRecognizer,
    DutchPhoneNumberRecognizer,
)
from src.api.nlp.loader import load_nlp_engine
from src.api.nlp.spacy_engine import SpacyEngine

DEFAULT_ENTITIES = [
    "PERSON",
    "LOCATION",
    "PHONE_NUMBER",
    "EMAIL",
    "ORGANIZATION",
    "IBAN",
    "ADDRESS",
]
DEFAULT_LANGUAGE = "nl"


class ModularTextAnalyzer:
    """Modulaire analyzer-klasse voor Nederlandse tekst."""

    def __init__(self) -> None:
        self.nlp_engine: SpacyEngine = load_nlp_engine(
            config_dict={"nlp_engine": "spacy"}
        )

        spacy_config = {
            "nlp_engine_name": "spacy",
            "models": [{"lang_code": "nl", "model_name": "nl_core_news_md"}],
        }

        spacy_provider = NlpEngineProvider(nlp_configuration=spacy_config)
        presidio_spacy_engine = spacy_provider.create_engine()

        registry = RecognizerRegistry()
        registry.supported_languages = ["nl"]

        recognizers_to_add = [
            DutchPhoneNumberRecognizer(),
            DutchIBANRecognizer(),
            DutchEmailRecognizer(),
        ]
        for recognizer in recognizers_to_add:
            registry.add_recognizer(recognizer=recognizer)

        # Initialiseer de AnalyzerEngine met SpaCy-engine voor pattern recognizers
        self.analyzer = AnalyzerEngine(
            nlp_engine=presidio_spacy_engine,
            registry=registry,
            supported_languages=["nl"],
        )
        logging.debug(
            f"ModularTextAnalyzer is initialized with {len(recognizers_to_add)} recognizers, {spacy_config=}"
        )

    def analyze_text(
        self,
        text: str,
        entities: list = DEFAULT_ENTITIES,
        language: str = DEFAULT_LANGUAGE,
    ) -> list:
        """Analyseer tekst met behulp van de NLP-engine en pattern recognizers.

        Args:
            text (str): de tekst om te analyseren.
            entities (list, optional): entities om te analyseren. Defaults to DEFAULT_ENTITIES.
            language (str, optional): taal om in te analyseren. Defaults to DEFAULT_LANGUAGE.

        Returns:
            list: lijst van gedetecteerde entiteiten met hun start- en eindposities, type en score.
        """
        logging.debug(f"Analyzing text with {entities=} and {language=}")
        nlp_results = self.nlp_engine.analyze(text, entities, language)

        # Gebruik de pattern recognizers via Presidio AnalyzerEngine
        pattern_results = self.analyzer.analyze(
            text=text, entities=entities, language=language
        )
        # Combineer resultaten (dedupliceer op start-end-entity_type)
        all_results = nlp_results + [
            {
                "entity_type": r.entity_type,
                "start": r.start,
                "end": r.end,
                "score": r.score,
                "text": text[r.start : r.end],
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

    def anonymize_text(
        self, text: str, entities: list = None, language: str = DEFAULT_LANGUAGE
    ) -> str:
        """Function to anonymize text by replacing detected entities with placeholders.

        Args:
            text (str): the text to anonymize.
            entities (list, optional): the entities to anonymize. Defaults to None.
            language (str, optional): the language to anonymize in. Defaults to DEFAULT_LANGUAGE.

        Returns:
            str: the anonymized text with placeholders for detected entities.
        """
        results = self.analyze_text(text, entities, language)

        # Sorteer op start, zodat vervangen van achter naar voren kan
        sorted_results = sorted(results, key=lambda x: x["start"], reverse=True)
        anonymized = text
        for ent in sorted_results:
            anonymized = (
                anonymized[: ent["start"]]
                + f"<{ent['entity_type']}>"
                + anonymized[ent["end"] :]
            )
        return anonymized
