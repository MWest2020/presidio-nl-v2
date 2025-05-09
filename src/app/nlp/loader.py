import yaml
from nlp.spacy_engine import SpacyEngine
from nlp.transformers_engine import TransformersEngine

def load_nlp_engine(config_path: str = None, config_dict: dict = None):
    if config_dict is None and config_path:
        with open(config_path) as f:
            config_dict = yaml.safe_load(f)
    if config_dict is None:
        # Default naar SpaCy
        return SpacyEngine()
    engine_type = config_dict.get("nlp_engine", "spacy")
    model_name = config_dict.get("model_name", "nl_core_news_md")
    if engine_type == "spacy":
        return SpacyEngine(model_name)
    elif engine_type == "transformers":
        return TransformersEngine(model_name)
    else:
        raise ValueError(f"Onbekende NLP engine: {engine_type}") 