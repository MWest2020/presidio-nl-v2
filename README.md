# Modular Dutch PII Detection Service (Presidio-Based)

A modular **Personally Identifiable Information (PII)** detection service for the Dutch language, built with [Microsoft Presidio](https://github.com/microsoft/presidio) as the core detection framework. It runs in a Docker container with a FastAPI backend and allows easy swapping of the underlying Natural Language Processing (NLP) model (e.g., spaCy or Hugging Face transformer) without changing the API logic. This README provides an overview of the project, its architecture, usage, and guidance for customization.

## Project Goal and Context

Organizations often need to detect and anonymize PII in text to comply with privacy regulations like GDPR. However, many PII detection tools are geared towards English. This project addresses that gap by focusing on **Dutch-language PII detection**. It leverages Microsoft Presidio to identify sensitive data (names, phone numbers, emails, IDs, etc.) in Dutch text. By using Dutch NLP models, the system can recognize Dutch names and context that an English model might miss (e.g. detecting a Dutch phone number format or national ID).

**Why Presidio?** Microsoft Presidio is an open-source framework specialized in PII detection and anonymization. It provides a robust Analyzer engine that combines multiple techniques – *regex patterns, checksums, named entity recognition (NER), and context words* – to find PII. Presidio supports extending to multiple languages and NLP frameworks (spaCy, Stanza, transformers), making it an ideal choice for building a Dutch PII detector. By default Presidio's models/recognizers target English, so this project configures Presidio for Dutch, using language-specific models and recognizers.

**Key Objectives:**

* **Dutch PII Detection:** Accurately detect PII in Dutch text (e.g. person names, phone numbers, email addresses, Dutch national IDs) using language-appropriate models and context.
* **Modularity:** Allow easy swapping of the NLP model (e.g. using spaCy's `nl_core_news_lg` vs. a Dutch BERT model) via configuration or Docker image selection. The API and overall logic remain unchanged regardless of the model used.
* **Containerized Service:** Provide a self-contained FastAPI application running in Docker for easy deployment. A team can clone the repo, build an image for their model of choice, and immediately have a REST API for PII detection.
* **Extensibility:** Make it straightforward to extend with new models or PII types (via config or custom recognizers) so the system can evolve (for example, adding a custom recognizer for the Dutch BSN number or IBAN bank account patterns).

## Architecture

**Overview:** The system follows a microservice-style architecture: a FastAPI web application handles HTTP requests and uses Presidio's Analyzer engine under the hood to perform PII detection. Everything runs within a Docker container for consistency. The main components are:

* **FastAPI Application:** Exposes REST endpoints (e.g. `/analyze`) to accept text input and return detected PII. FastAPI is chosen for its performance and easy integration with Python async frameworks.
* **Presidio Analyzer Engine:** The core library that processes text to identify PII entities. It utilizes a set of **recognizers** (both built-in and custom) to detect sensitive entities. Recognizers can use regex rules, dictionary lookups, and **NLP model-based NER** to find entities, with a context mechanism to improve confidence.
* **NLP Model (Modular):** The underlying NLP engine providing language processing and NER. This can be **spaCy** (with Dutch model `nl_core_news_lg`) or a **Hugging Face transformers** model (e.g. `GroNLP/bert-base-dutch-cased` fine-tuned for NER). The Presidio Analyzer delegates tokenization and entity recognition to this NLP layer. The model is loaded at startup based on configuration.
* **Docker Container:** The Docker image packages the FastAPI app, Presidio, and the chosen NLP model. Each variant of the image is built with a specific model, so that all dependencies (like spaCy model data or transformer weights) are included. Docker ensures the same environment for development and deployment.

*Architecture Overview – The Presidio Analyzer uses a variety of recognizers (built-in regex/checksum, contextual rules, and NER from NLP models) to identify PII in text. In our service, this analyzer is wrapped in a FastAPI app and packaged in Docker. The underlying NLP model (spaCy or transformers) can be swapped without altering the Analyzer or API.*

**Request Flow:**

1. A client sends a POST request to the FastAPI endpoint (for example, `/analyze`) with a JSON payload containing the text (and optionally language code, which defaults to `"nl"` for Dutch).
2. The FastAPI handler passes the text to Presidio's `AnalyzerEngine.analyze()` method, specifying the language as Dutch (`"nl"`). The AnalyzerEngine is initialized at app startup with the configured Dutch NLP engine and a registry of recognizers for PII.
3. The Presidio Analyzer processes the text through its pipeline:

   * It first uses the **NLP engine** to tokenize and perform NER on the text (identifying candidate entities like PERSON, LOCATION, etc. in Dutch).
   * Built-in **pattern recognizers** then run (for things like phone numbers, emails, credit card numbers, etc.). For example, a regex pattern can catch a phone number or IBAN format.
   * Each recognizer (pattern-based or NER-based) returns findings with a confidence score. Presidio uses context words (e.g., words like "telefoon" near a number increase confidence it's a phone) to adjust scores.
   * All findings above a confidence threshold are aggregated as the detected PII entities.
4. The FastAPI app returns a JSON response with the detected entities (each typically has a type, the text snippet, and its position in the input, plus a score).

**Presidio Recognizers for Dutch:** We leverage Presidio's flexibility to support Dutch. Some default recognizers (like `EmailRecognizer`, `PhoneRecognizer`, `CreditCardRecognizer`) are language-agnostic or have been updated with Dutch context. For example, we ensure the phone number recognizer knows Dutch words like "telefoon" or uses Dutch phone formats. For NER-based detection (names, locations, etc.), the Dutch model provides those entities. We can also add **custom recognizers** for Dutch-specific PII (e.g., BSN – Burger Service Number – using a regex pattern and context words like "burgerservicenummer") as needed.

**Anonymization (optional):** While this project's focus is PII *detection*, Presidio also includes an Anonymizer engine to redact or replace PII. The architecture can be extended to anonymize detected PII in the response if required – e.g., returning text with `<PERSON>` in place of actual names. For now, we return raw detection results, but integrating the `AnonymizerEngine` would be straightforward using the detection output.

## Model Modularity

One of the core features of this project is the ability to **swap out the NLP model** without altering the API or detection logic. We achieve this through configuration and containerization:

* **Configurable NLP Engine:** Presidio's NLP engine is configured at startup using a configuration (YAML or dictionary) that specifies which model to load for a given language. For instance, to use spaCy, we set:

  ```python
  {"nlp_engine_name": "spacy", "models": [{"lang_code": "nl", "model_name": "nl_core_news_lg"}]}
  ```

  To use a Hugging Face transformers model for NER, we set:

  ```python
  {"nlp_engine_name": "transformers", "models": [{"lang_code": "nl", "model_name": {
      "spacy": "nl_core_news_sm", 
      "transformers": "GroNLP/bert-base-dutch-cased"
  }}], ...}
  ```

  In the transformers case, Presidio can combine a spaCy small model for basic tokenization with a transformers model for NER. The model-to-entity mapping (e.g., mapping transformer's labels like `PER` to Presidio's `PERSON`) is defined in the config as well.

* **Factory/Provider Pattern:** We use Presidio's `NlpEngineProvider` or a factory function in code to create the NLP engine based on a config file or environment variable. The FastAPI app doesn't hard-code any model – it reads a config (e.g., `conf/nl_spacy.yaml` vs `conf/nl_bert.yaml`) and initializes the AnalyzerEngine accordingly. This means **no changes to the API code** are needed to switch models; just supply a different config. For example, switching from spaCy to the BERT model is as simple as changing an environment variable or using a different Docker image tag.

* **Multiple Docker Images:** To encapsulate different models, the project supports building separate Docker images for each model variant. For instance, you might build one image tagged `pii-detector:nl-spacy` that includes the spaCy Dutch model, and another tagged `pii-detector:nl-bert` that includes the HuggingFace model. The FastAPI application code is the same; only the model and config bundled in the image differ. This separation ensures that each image is optimized (the spaCy image doesn't need large transformer libraries, and the transformer image doesn't need spaCy's large model, unless used for tokenization). You can choose the appropriate image for your use case, or even run both in parallel behind different endpoints if comparing performance.

* **Entrypoint Configuration:** At container startup, an environment variable (like `MODEL_TYPE` or a config path) can instruct which model config to use. For example, the Docker entrypoint script could read `$MODEL_TYPE` and copy the corresponding config file into Presidio's default config location before launching the app. In practice, however, building separate images (each baked with the desired config and model) is simpler and avoids runtime overhead.

* **No API Change:** Regardless of the chosen model, the API exposed by FastAPI remains consistent. A request to detect PII will have the same format and output structure. This is possible because Presidio abstracts the model details behind its Analyzer interface. As long as the recognizers are properly set up for that language/model, the rest of the system doesn't need to know if it's spaCy or BERT doing the NER under the hood.

In summary, model modularity is achieved by externalizing model selection to configuration and the container build process. The code uses a **single, unified interface** to the NLP engine, so swapping engines is plug-and-play. This modular design allows experimenting with different NLP backends (for accuracy or performance) without touching the service code.

## Instructions for Use

Follow these steps to build and run the PII detection service with your chosen NLP model. We assume you have Docker installed on your system.

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/dutch-pii-detector.git
cd dutch-pii-detector
```

Inside the repository, you'll find the FastAPI app code, configuration files, and Dockerfiles for different models.

### 2. Build the Docker Image (Choose a Model)

You can build one or more variants of the Docker image depending on the NLP model you want:

* **Using spaCy's Dutch model** (`nl_core_news_lg`):

  ```bash
  docker build -f Dockerfile.spacy -t pii-detector:nl-spacy .
  ```

  This will install the spaCy model for Dutch during the build. (The Dockerfile might use a command like `python -m spacy download nl_core_news_lg` or Presidio's auto-install mechanism.)

* **Using Hugging Face BERT model** (`GroNLP/bert-base-dutch-cased` for NER):

  ```bash
  docker build -f Dockerfile.bert -t pii-detector:nl-bert .
  ```

  This will install required Hugging Face transformers libraries and download the Dutch BERT model. The build might leverage Presidio's transformers config or download the model on first run if not included.

> **Note:** The repository may alternatively provide a single Dockerfile with build arguments (e.g. `--build-arg MODEL_TYPE=spacy`) instead of multiple files. Use the method documented in the repo. The result should be an image that contains the specified model and the proper configuration for it.

### 3. Run the Container

Once built, run the Docker container. For example, to run the spaCy-based image:

```bash
docker run -d -p 8000:8000 --name pii_nl_spacy pii-detector:nl-spacy
```

This starts the FastAPI server inside the container, listening on port 8000 (mapped to host port 8000). If the app starts correctly, you should see logs indicating the model was loaded (e.g., spaCy model load or transformer model load) and that Uvicorn (the ASGI server) is running.

* To run the BERT-based container, use the corresponding tag:

  ```bash
  docker run -d -p 8000:8000 --name pii_nl_bert pii-detector:nl-bert
  ```

*(If you run both simultaneously on the same host, use different host ports, e.g., `-p 8001:8000` for one of them.)*

### 4. Test the API

Once the container is running, you can test the PII detection API. The FastAPI app provides interactive documentation at **`/docs`** (Swagger UI) – open `http://localhost:8000/docs` in your browser to see available endpoints and try them out.

Typically, the service will have an endpoint such as **`POST /analyze`** (or `/detect` or similar – see the documentation in the app). To call it, send a JSON payload with the text to analyze. For example:

**Request:**

```bash
curl -X POST "http://localhost:8000/analyze" \
  -H "Content-Type: application/json" \
  -d '{ "text": "Hallo, mijn naam is Mark Rutte en mijn telefoonnummer is 06-12345678.", "language": "nl" }'
```

Here we send a Dutch sentence introducing a name and phone number. The `"language": "nl"` field tells Presidio to use the Dutch pipeline (the service might default to nl if not provided, but we include it for clarity).

**Response:**

```json
{
  "entities": [
    {
      "entity_type": "PERSON",
      "start": 18,
      "end": 28,
      "score": 0.85,
      "text": "Mark Rutte"
    },
    {
      "entity_type": "PHONE_NUMBER",
      "start": 56,
      "end": 67,
      "score": 0.90,
      "text": "06-12345678"
    }
  ]
}
```

The response JSON contains a list of detected PII entities in the input text. In this example, it found a person name and a phone number:

* **PERSON** – "Mark Rutte" (the Prime Minister's name was recognized by the Dutch NER model).
* **PHONE_NUMBER** – "06-12345678" (matched by a phone pattern recognizer, treated as a Dutch mobile number).

Each entity entry includes the character offsets in the input string, a confidence score, and the text that was matched. The exact schema may vary (for instance, Presidio might also include a `analysis_explanation` or other fields if configured).

You can test other inputs by modifying the JSON. For example:

* **Email:** `"Stuur me een email op jan.jansen@example.nl"` should return an entity of type `EMAIL_ADDRESS`.
* **Credit Card:** `"Mijn creditcardnummer is 4111 1111 1111 1111"` should return `CREDIT_CARD` (assuming built-in recognizer for credit card patterns).
* **BSN (Dutch SSN):** `"mijn burgerservicenummer is 123456782"` – If a BSN recognizer is configured, it would return a `SSN` or `BSN` entity for the 9-digit number. (By default, Presidio's US SSN recognizer wouldn't catch this as Dutch SSN without customization.)

### 5. Integration

You can integrate this API into your applications or data pipelines. For instance, you might call the API from a data processing script to scan documents for PII and then mask them. Because it's a standard REST service, any language or tool that can make HTTP requests can use it.

For development and debugging, you can also run the FastAPI app outside Docker (e.g., `uvicorn app:app --reload`) if you have the proper Python environment with dependencies. This might ease development of new features or custom recognizers. Just ensure to set the environment or config for the desired model in that case as well.

## Configuration Details

Configuration is key to making this system flexible. There are a few ways the configuration is managed:

* **Presidio NLP Configuration:** We use Presidio's configuration file mechanism to specify the NLP engine and model. For example, the repo includes a file like `conf/nl_spacy.yaml` for the spaCy model which contains:

  ```yaml
  nlp_engine_name: spacy
  models:
    - lang_code: nl
      model_name: nl_core_news_lg
  ```

  and another `conf/nl_transformers.yaml` for the transformers model:

  ```yaml
  nlp_engine_name: transformers
  models:
    - lang_code: nl
      model_name:
        spacy: nl_core_news_sm        # tokenization model
        transformers: GroNLP/bert-base-dutch-cased  # NER model
  ```

  The FastAPI app loads the appropriate config at startup via `NlpEngineProvider`. You can find these config files in the repository and modify them if you want to experiment with different models or languages.

* **Environment Variables:** Alternatively, the service can accept an environment variable (e.g., `PRESIDIO_NLP_CONFIG_PATH`) to point to the desired config file. During Docker build or run, you might set `NLP_CONF_FILE=conf/nl_spacy.yaml` (as done in similar projects) to ensure the container uses the spaCy config. The Docker build process in our project is configured to copy and use the specified config – this means at build time the model can even be downloaded automatically. Ensure the environment variable or build arg is consistent with the model you intend to use.

* **Default Settings:** If no explicit configuration is provided, the application might default to one of the models (e.g., default to spaCy for Dutch). We explicitly list supported models in the README and encourage setting it explicitly to avoid confusion.

* **Adding New Models:** If you want to add another model (say a different HuggingFace model fine-tuned for Dutch NER), you can create a new config YAML for it and either build a new image with that config or mount the config into the container. The pattern to follow is similar: if it's a transformers model, include a spaCy model for tokenization (or use Presidio's native tokenizer if available) and map the entity labels. Presidio's docs on [customizing the NLP model](https://microsoft.github.io/presidio/analyzer/) provide guidance for adding new models or languages.

* **Recognizer Configuration:** Beyond the NLP model, some recognizers have **context word lists** and regex patterns that are language-specific. We have tuned some of these for Dutch (e.g., adding `"telefoon"` and `"mobiel"` to Phone number recognizer's context). These configurations are in the code or in recognizer files. If you find that a certain PII (like a Dutch passport number, license plate, etc.) is not recognized, you can either adjust an existing recognizer's patterns/context or implement a new custom recognizer class and register it in the AnalyzerEngine. The configuration for recognizers can be done via code or YAML (Presidio supports loading recognizers from YAML as well).

In summary, you choose the model via config file or env var, and the Docker build/run picks that up. The repository includes sane defaults for Dutch with both spaCy and a transformer. It's recommended to start with those and only change if needed.

## Example Input and Output

Below are some example inputs (in Dutch) and the expected PII detection outputs to illustrate how the system works:

* **Example 1: Personal info in a sentence**

  **Input:** `Hallo, ik ben Jan de Vries en mijn email is jan.devries@gmail.com.`
  **Detection Output:**

  * `PERSON`: "Jan de Vries" (a Dutch person name)
  * `EMAIL_ADDRESS`: "[jan.devries@gmail.com](mailto:jan.devries@gmail.com)"

  The name is detected by the NER model (spaCy or BERT), and the email by Presidio's built-in email recognizer (regex pattern for emails). The JSON response would look like:

  ```json
  [
    {"entity_type": "PERSON", "text": "Jan de Vries", "start": 12, "end": 24, "score": 0.99},
    {"entity_type": "EMAIL_ADDRESS", "text": "jan.devries@gmail.com", "start": 40, "end": 62, "score": 0.95}
  ]
  ```

  (Positions and scores are illustrative.)

* **Example 2: Multiple PII types**

  **Input:** `Klant: Maria van den Berg, Telefoon: 06 12345678, Creditcard: 4111111111111111`
  **Detection Output:**

  * `PERSON`: "Maria van den Berg"
  * `PHONE_NUMBER`: "06 12345678"
  * `CREDIT_CARD`: "4111111111111111"

  Here we see the model find the name, while regex-based recognizers identify the phone number and credit card. The credit card is a 16-digit number which matches the Presidio credit card pattern and passes Luhn checksum validation (a built-in check).

* **Example 3: Dutch specific entities**

  **Input:** `BSN: 123456782 behoort tot dhr. Jansen.`
  **Detection Output:**

  * `PERSON`: "dhr. Jansen" (assuming the model recognizes "dhr." as honorific and identifies the surname)
  * `SSN` (or custom `BSN` type): "123456782"

  In this case, detecting the BSN (a Dutch national ID format) might require a custom recognizer. We include a simple pattern recognizer for 9-digit numbers as BSN for demonstration. If configured, Presidio would tag the 9-digit sequence as `SSN` or `BSN` with a certain confidence. (If not configured, the 9-digit might be incorrectly seen as a US SSN with low confidence or not at all.)

These examples show the versatility of the system in identifying different PII types in Dutch text. You can experiment by sending your own examples to the running service. The detection quality will depend on the model's NER performance for names/locations and the completeness of regex patterns for other entities. In our testing with Dutch texts, spaCy's large model performs well on person names and locations, while the built-in recognizers handle structured data like emails and numbers. If the HuggingFace BERT model is used, it may have different strengths (possibly better generalization for names, at the cost of speed).

## Future Extensions and Ideas

This project is designed with extensibility in mind. Here are several ideas for future development or enhancements that could be valuable:

* **Custom Model Training:** To improve accuracy, you could fine-tune the chosen NLP model on Dutch-specific PII data. For example, fine-tuning the BERT model on a Dutch NER dataset that includes person names, locations, etc., or training spaCy on new data. Microsoft has released **Presidio Research** tools to help generate and evaluate PII data and models, which could be used to create synthetic training data (e.g., fake Dutch names, addresses) and evaluate model performance. A custom-trained model could then be plugged into the system via the same config mechanism.

* **Additional PII Entities:** Extend the recognizers to cover more Dutch-specific PII. For instance, recognizers for Dutch vehicle license plates, Dutch passport numbers, IBAN bank account numbers (if not already covered; IBAN regex can be added), or Dutch addresses (which might require NLP and regex hybrid approaches). The modular design allows adding a new recognizer class and registering it without affecting existing ones. These could be configured via YAML or Python code. The README can be updated to document new entity types as they are added.

* **Anonymization Pipeline or UI:** Build a user interface or tool to **anonymize text using this detector**. One idea is deploying a small web app (Streamlit or Gradio) on **Hugging Face Spaces** that uses the API to detect PII and then displays the text with PII masked or replaced. This would provide a visual demo where a user can input Dutch text and see which parts get highlighted as PII and perhaps anonymized. It would be a great way to showcase the system to non-developers. Hugging Face Spaces can easily host Gradio apps – the app would simply call the FastAPI endpoints in the background. Alternatively, the FastAPI app itself could serve an HTML front-end for demo purposes (though keeping concerns separate is cleaner).

* **Dynamic Model Selection via API:** Currently, the model is chosen per deployment (one container = one model). In the future, one could allow **runtime model selection**. For example, an API parameter `?model=bert` vs `?model=spacy` could route the request to different AnalyzerEngine instances. This might involve loading multiple models into the app and choosing between them per request. While more resource-intensive, it could be useful for comparison or if the service needs to handle multiple languages or model versions in one instance. Another approach is to have a lightweight orchestrator that forwards requests to different containers based on a parameter. Either way, exposing model choice to the API would make the service even more flexible (at the cost of complexity).

* **Performance Tuning and Scaling:** For production use, consider scaling the service (e.g., running multiple replicas behind a load balancer) and monitoring performance. A future enhancement could be an **autoscaling setup with Docker Compose or Kubernetes**, where each model variant runs in its own service. Also, optimizing the startup time by pre-loading models, and possibly using ONNX or quantized models for faster inference, could be explored if the use-case requires high throughput.

* **Multi-language Support:** While focused on Dutch, the architecture can naturally extend to other languages. A future roadmap item might be to incorporate other languages (e.g., English or German) using the same modular approach. This could mean multiple model configs and perhaps a language detection step in front. Given Presidio's design, it can support multiple languages if the recognizers are set up accordingly. The project could be renamed or refactored to a general multi-language PII detector, with Dutch as one configuration example.

* **Integration with Privacy Workflows:** Beyond being a standalone service, this detector could integrate with data pipelines. Future work could include connectors or examples for using it in ETL jobs, or as an AWS Lambda function, etc. Also, integrating with `presidio-image-redactor` for detecting PII in images (like scans of Dutch IDs) could be an extension for a more comprehensive solution.

We encourage the community to contribute by testing the detector on real-world Dutch data, reporting false negatives/positives, and suggesting improvements. With its modular design and the power of Presidio under the hood, this project can serve as a strong foundation for privacy-proofing Dutch text data in various applications.

## Conclusion

This README has provided a detailed overview of the **Modular Presidio-based PII Detection System for Dutch**. The project's modularity, powered by configuration-driven model selection and containerization, allows developers to easily adapt it to their needs – whether that's swapping in a new NLP model or extending the types of PII detected. By focusing on the Dutch language, we leverage language-specific models and context to achieve high-quality PII detection, helping organizations comply with privacy regulations in the Netherlands and beyond.

**Getting Started:** Clone the repo, choose a model, build the Docker image, and you have a running service that can identify sensitive information in your Dutch texts. The examples and instructions above should help you verify the setup. From there, you can integrate it into larger systems or enhance it as needed.

We hope this tool proves useful for your data anonymization and privacy efforts. Feel free to submit issues or pull requests on GitHub if you encounter problems or have improvements – whether it's better regex for Dutch data or integration of a new state-of-the-art Dutch NLP model. Happy anonymizing!

**References:** This project builds upon Microsoft Presidio and its documentation for multi-language support. Insights from community examples (e.g., ANWB's Dutch Presidio usage) informed our Dutch configuration. Please refer to the official Presidio docs for deeper understanding of the underlying framework and to **Presidio Research** for advanced customization and model training tools.

## API testen via localhost

Installeer lokal de dependencies en run met `uv`:

```bash
uv venv
uv sync
uv run api.py
```

kun je de interactieve documentatie openen in je browser:

```url
http://localhost:8000/docs
```

Hier kun je direct het `/analyze` en `/anonymize` endpoint proberen.

### Voorbeeld: curl-request naar /analyze

```bash
curl -X POST "http://localhost:8000/analyze" -H "Content-Type: application/json" -d '{
  "text": "Ik ben Mark Westerweel en ik werk aan Presidio, onderweg naar Amsterdam. Mijn telefoon is 06-12345678 en mijn email is mark@example.com en mijn IBAN is NL91ABNA0417164300.",
  "entities": ["PERSON", "LOCATION", "PHONE_NUMBER", "EMAIL", "IBAN"],
  "language": "nl"
}'
```

### Voorbeeldresponse

```json
{
  "text": "Ik ben Mark Westerweel en ik werk aan Presidio, onderweg naar Amsterdam. Mijn telefoon is 06-12345678 en mijn email is mark@example.com en mijn IBAN is NL91ABNA0417164300.",
  "entities_found": [
    {"entity_type": "PERSON", "text": "Mark Westerweel", "start": 7, "end": 22, "score": 0.85},
    {"entity_type": "PHONE_NUMBER", "text": "06-12345678", "start": 87, "end": 99, "score": 0.6},
    {"entity_type": "EMAIL", "text": "mark@example.com", "start": 120, "end": 136, "score": 0.6},
    {"entity_type": "IBAN", "text": "NL91ABNA0417164300", "start": 154, "end": 172, "score": 0.6}
  ]
}
```

### Let op
- Gebruik `/docs` voor snelle interactie en testen.
