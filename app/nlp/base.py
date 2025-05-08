from abc import ABC, abstractmethod

class NlpEngine(ABC):
    @abstractmethod
    def analyze(self, text: str, entities: list = None, language: str = "nl"):
        """
        Analyseer tekst en retourneer een lijst van gevonden entiteiten.
        :param text: De te analyseren tekst
        :param entities: Optionele lijst van te detecteren entiteiten
        :param language: Taalcode (default: 'nl')
        :return: Lijst van entiteiten (dicts of Presidio RecognizerResult)
        """
        pass 