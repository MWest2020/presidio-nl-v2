from time import time

from flair.data import Sentence
from flair.models import SequenceTagger

# load tagger
tagger = SequenceTagger.load("flair/ner-dutch")

# make example sentence
t1 = time()
sentence = Sentence("Ruben van der Linden ging naar de Lindenlaan in Amsterdam.")
tagger.predict(sentence, embedding_storage_mode="gpu")
t2 = time()
print(f"Time taken to predict: {t2 - t1:.4f} seconds")


# print sentence
print(sentence)

# print predicted NER spans
print("The following NER tags are found:")
# iterate over entities and print
for entity in sentence.get_spans("ner"):
    print(entity)
