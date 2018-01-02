from nltk.classify import ClassifierI

from nlp import nlp_utils
from nlp import nlp_preprocessing


def preprocess_document(filename):
    with open(filename, 'rb') as f:
        lines = f.readlines()
    new_lines = [line.decode("utf-8") for line in lines]
    new_lines = nlp_preprocessing.clean_document(new_lines)
    new_lines = [line for line in new_lines if line]

    return new_lines

class Vader(ClassifierI):
    def __init__(self):
        from nltk.sentiment.vader import SentimentIntensityAnalyzer as sia
        from nltk.sentiment.vader import normalize as norm
        self._sia = sia()
        self._norm = norm

    # sentiment based on averaging sentences
    def _average_on_sentence(self, line):
        from nltk.tokenize import sent_tokenize
        sentences = sent_tokenize(line)
        line_scores = [0, 0, 0]
        for sentence in sentences:
            ss = self._sia.polarity_scores(sentence)
            pos_score = self._norm(ss['pos'])
            neg_score = self._norm(ss['neg'])
            neu_score = self._norm(ss['neu'])
            sentence_scores = [pos_score, neg_score, neu_score]
            for x in range(3):
                line_scores[x] += sentence_scores[x]
        avg_line_scores = [round(score / len(sentences), 4) for score in line_scores]
        pos_score = avg_line_scores[0]
        neg_score = avg_line_scores[1]
        self._scores = avg_line_scores
        if (pos_score > neg_score):
            return 'pos'
        elif neg_score > pos_score:
            return 'neg'
        else:
            return 'neu'

    def classify(self, line):
        result = self._average_on_sentence(line)
        return result

    def scores(self):
        return self._scores

class NLPSentiment:
    def __init__(self):
        self._vader = Vader()
        self._verdicts = None

    def results(self):
        return self._verdicts

    def run(self):
        self._verdicts = []
        filenames = nlp_utils.get_filenames()
        for filename in filenames:
            file_contents = preprocess_document(filename)

            scores = [0, 0, 0]

            for line in file_contents:
                if len(line.split()) > 0:
                    self._vader.classify(line)
                    line_scores = self._vader.scores()
                    scores = [scores[0] + line_scores[0], scores[1] + line_scores[1], scores[2] + line_scores[2]]

            pos_points = scores[0]
            neg_points = scores[1]

            if pos_points >= neg_points:
                verdict = 'pos'
            else:
                verdict = 'neg'
            self._verdicts.append((verdict, scores))
