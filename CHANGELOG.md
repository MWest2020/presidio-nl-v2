# Changelog

Alle belangrijke wijzigingen in dit project worden in dit bestand gedocumenteerd.

De opmaak is gebaseerd op [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) en dit project maakt gebruik van [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## 09-05-2025 0.0.1

###
- Herziening van de Presidio-Nl api v1
- Projectafspraken en opbouw Python
- Testsuite
- PII-detectie voor:
    * naam
    * e-mailadressen
    * telefoonnummers
    * beperkte lokatienamen (staat in planning via flair of db)

## Vandaag
- IBAN recognizer generiek gemaakt en getest met verschillende landen.
- Testscript toegevoegd (`test_iban.py`) om de recognizer direct te kunnen testen.
- Voorbereiding voor nieuwe aanpak locatieherkenning. 