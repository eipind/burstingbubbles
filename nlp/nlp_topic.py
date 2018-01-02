# comment/unoomment to enable/disable logging
# import logging
# logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

from datacollection import settings as dc_settings
import json
import os
import re
from nlp import nlp_utils, nlp_preprocessing, settings as nlp_settings
from gensim import corpora, models
from collections import defaultdict

def preprocess_document(document, reddit):
    min_word_freq = 5

    new_document = [line.decode('utf-8') for line in document]
    new_document = nlp_preprocessing.clean_document(new_document, reddit=reddit)
    new_document = nlp_preprocessing.remove_stopwords_document(new_document, reddit=reddit)
    new_document = nlp_preprocessing.remove_isolated_punctuation_document(new_document)
    new_document = nlp_preprocessing.remove_trailing_punctuation_document(new_document)
    new_document = nlp_preprocessing.lowercase_document(new_document)
    new_document = [[token for token in line.split()]for line in new_document]

    frequency = defaultdict(int)

    for line in new_document:
        for token in line:
            frequency[token] += 1

    new_document = [[token for token in line if frequency[token] > min_word_freq]
             for line in new_document]

    new_document = [line for line in new_document if line]


    return new_document

class NLPTopic:
    class _MyCorpus:

        def __init__(self, filename, reddit=False):
            self._filename = filename

            with open(filename, 'rb') as f:
                document = f.readlines()

            self._document = preprocess_document(document, reddit=reddit)
            self._dictionary = corpora.Dictionary(self._document)

        def __iter__(self):
            for line in self._document:
                yield self._dictionary.doc2bow(line)

        def get_dictionary(self):
            return self._dictionary

    def __init__(self):
        self._STOPLIST = nlp_utils.load_stoplist()

        metadata_file = open(dc_settings.OUTPUT_METADATA_FILE_NAME)
        self._metadata_json = json.load(metadata_file)
        metadata_file.close()

    def get_filenames(self):
        count = self._metadata_json['count']
        return [re.sub(r'(\.txt)$', str(counter) + '.txt', dc_settings.OUTPUT_FILE_NAME_TEMPLATE) for counter in
                range(count)]

    def run(self, reddit=True):
        filenames = self.get_filenames()
        self._submission_topics = []

        counter = 0
        for filename in filenames:
            corpus_obj = self._MyCorpus(filename, reddit)
            corpus_dictionary = corpus_obj.get_dictionary()
            corpus = [vector for vector in corpus_obj]
            model = models.LdaModel(corpus, id2word=corpus_dictionary, num_topics=nlp_settings.NO_OF_TOPICS)
            try:
                submission_topic = model.show_topics(num_words=nlp_settings.NO_OF_WORDS_TO_DISPLAY, num_topics=nlp_settings.NO_OF_TOPICS, formatted=False)
            except:
                raise ValueError("One or more of the submissions collected were empty!")
            self._submission_topics.append(submission_topic)
            self.gensim_output_save(model, corpus, corpus_dictionary, counter)
            counter += 1

    @staticmethod
    def gensim_output_save(model, corpus, dictionary, counter):
        # Interactive visualisation
        import pyLDAvis.gensim, pyLDAvis
        vis = pyLDAvis.gensim.prepare(model, corpus, dictionary)
        filename = re.sub(r"(\.html)$", str(counter) + ".html", nlp_settings.RESULTS_OUTPUT_PATH_TOPIC)
        dir = os.path.dirname(filename)
        os.makedirs(dir, exist_ok=True)
        file = open(filename, 'w')
        pyLDAvis.save_html(vis, file)

    def results(self):
        return self._submission_topics
