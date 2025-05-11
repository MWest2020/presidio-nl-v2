# Changelog

## Deze week
- Refactor van de IBAN recognizer: ondersteunt nu IBANs uit alle landen in plaats van alleen Nederlandse IBANs.
- Opruimen van oude en dubbele bestanden in de codebase.
- Verbeteringen aan de structuur van de recognizers (o.a. phone, email).
- Testen toegevoegd voor directe functionaliteitscontrole zonder API of Docker.

## Vandaag
- IBAN recognizer generiek gemaakt en getest met verschillende landen.
- Testscript toegevoegd (`test_iban.py`) om de recognizer direct te kunnen testen.
- Voorbereiding voor nieuwe aanpak locatieherkenning. 