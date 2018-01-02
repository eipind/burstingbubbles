import re
import string
import os

STOPLIST_FILENAME = os.path.join(os.getcwd(),"nlp")
STOPLIST_FILENAME = os.path.join(STOPLIST_FILENAME,"pickles")
STOPLIST_FILENAME = os.path.join(STOPLIST_FILENAME, "stoplist.pickle")

def lowercase_remove_punctuation(document):
    translation = str.maketrans("", "", string.punctuation)
    return document.translate(translation).lower()

def save_obj(obj, obj_filename):
    import pickle
    with open(obj_filename, "wb") as obj_saver:
        pickle.dump(obj, obj_saver)

def load_obj(obj_name):
    import pickle
    with open(obj_name, "rb") as obj_f:
        obj = pickle.load(obj_f)
    return obj

def create_stoplist():
    import pickle
    from nltk.corpus import stopwords
    STOPLIST0 = ["le", "theyll", "tfw", "imo", "youd", "youll", "dont", "like", "im", "shouldnt", "aint", "couldnt",
                 "didnt", "doesnt", "hadnt", "hasnt", "havent", "mightnt", "neednt", "shant",
                 "shouldnt",
                 "wasnt", "werent", "wont", "wouldnt", "would", "should", "could", "must", "was"]
    STOPLIST = [lowercase_remove_punctuation(word) for word in stopwords.words("English")]
    STOPLIST.extend(STOPLIST0)
    STOPLIST = set(STOPLIST)

    os.makedirs(os.path.dirname(STOPLIST_FILENAME),exist_ok=True)

    with open(STOPLIST_FILENAME, "wb") as f:
        pickle.dump(STOPLIST, f)

    save_obj(STOPLIST, STOPLIST_FILENAME)

def load_stoplist():
    STOPLIST = load_obj(STOPLIST_FILENAME)
    return STOPLIST

def check_stoplist():
    return os.path.exists(STOPLIST_FILENAME)

def get_filenames():
    import json, re
    from datacollection import settings
    metadata_file = open(settings.OUTPUT_METADATA_FILE_NAME)
    metadata_json = json.load(metadata_file)
    metadata_file.close()
    count = metadata_json["count"]
    return [re.sub(r"(\.txt)$", str(counter) + ".txt", settings.OUTPUT_FILE_NAME_TEMPLATE) for counter in
            range(count)]