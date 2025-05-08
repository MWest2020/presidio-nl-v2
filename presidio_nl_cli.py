import sys
import os
import click

# Voeg ./app toe aan sys.path zodat anonymizer direct geïmporteerd kan worden
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "app"))

from anonymizer.engine import ModularTextAnalyzer

@click.group()
def cli():
    """Presidio-NL CLI: detecteer of anonimiseer PII in Nederlandse tekst."""
    pass

@cli.command()
@click.option('--text', prompt='Voer tekst in', help='De tekst om te analyseren op PII.')
@click.option('--config', default=None, help='Pad naar NLP-configuratiebestand (yaml).')
def analyze(text, config):
    """Detecteer PII in tekst."""
    analyzer = ModularTextAnalyzer(nlp_config_path=config)
    results = analyzer.analyze_text(text)
    click.echo("Gevonden entiteiten:")
    for ent in results:
        click.echo(f"{ent['entity_type']}: '{ent['text']}' (pos {ent['start']}-{ent['end']}, score {ent['score']:.2f})")

@cli.command()
@click.option('--text', prompt='Voer tekst in', help='De tekst om te anonimiseren.')
@click.option('--config', default=None, help='Pad naar NLP-configuratiebestand (yaml).')
def anonymize(text, config):
    """Anonimiseer PII in tekst (vervang door <ENTITY>)."""
    analyzer = ModularTextAnalyzer(nlp_config_path=config)
    results = analyzer.analyze_text(text)
    # Sorteer op start, zodat vervangen van achter naar voren kan
    sorted_results = sorted(results, key=lambda x: x['start'], reverse=True)
    anonymized = text
    for ent in sorted_results:
        anonymized = anonymized[:ent['start']] + f"<{ent['entity_type']}>" + anonymized[ent['end']:]
    click.echo(anonymized)

if __name__ == '__main__':
    cli() 