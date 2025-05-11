from app.anonymizer.recognizers.patterns import IBANRecognizer


def test_iban_recognizer():
    # Initialize the recognizer
    recognizer = IBANRecognizer()

    # Test cases
    test_cases = [
        "NL91ABNA0417164300",  # Dutch IBAN
        "DE89370400440532013000",  # German IBAN
        "FR7630006000011234567890189",  # French IBAN
        "BE68539007547034",  # Belgian IBAN
        "This is not an IBAN",  # Should not match
        "NL91ABNA0417164300 and another NL91ABNA0417164300",  # Multiple matches
    ]

    print("Testing IBAN Recognizer:")
    print("-" * 50)

    for text in test_cases:
        results = recognizer.analyze(text, entities=["IBAN"])
        print(f"\nText: {text}")
        if results:
            for result in results:
                print(f"Found IBAN: {text[result.start : result.end]}")
                print(f"Confidence: {result.score}")
                print(f"Position: {result.start}-{result.end}")
        else:
            print("No IBAN found")


if __name__ == "__main__":
    test_iban_recognizer()
