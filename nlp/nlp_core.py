import nlp.nlp_sentiment as nlps
import nlp.nlp_topic as nlpt
import nlp.nlp_utils as nlputils

class NLPCore:
    def __init__(self):
        #create list of stopwords if there isn't one yet
        if not nlputils.check_stoplist():
            nlputils.create_stoplist()

        self._topic_modelling = nlpt.NLPTopic()
        self._sentiment_analysis = nlps.NLPSentiment()

    def run(self):
      self._topic_modelling.run()
      self._sentiment_analysis.run()

    def get_sentiment_results(self):
        return self._sentiment_analysis.results()

    def get_topic_results(self):
        return self._topic_modelling.results()