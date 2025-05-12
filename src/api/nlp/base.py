from abc import ABC, abstractmethod


class NLPEngine(ABC):
    """
    Abstracte basisinterface voor NLP-engines in het systeem.
    Alle concrete NLP-engines (zoals SpaCy of Transformers) moeten deze interface implementeren.
    """
    @abstractmethod
    def analyze(self, text: str, entities: list = None, language: str = "nl") -> list:
        """Analyseer tekst en retourneer een lijst van gevonden entiteiten.

        Args:
            text (str): De te analyseren tekst.
            entities (list, optional): Optionele lijst van te detecteren entiteiten. Defaults to None.
            language (str, optional): Taalcode. Defaults to 'nl'.

        Returns:
            list: Lijst van entiteiten (dicts of Presidio RecognizerResult).
        """
        pass
