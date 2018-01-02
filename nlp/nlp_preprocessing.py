import nlp.nlp_utils as utils
import re, string
__reddit_min_words = 5
__stopwords = utils.load_stoplist()


def findWholeWord(w, features):
    if re.compile(r'\b({0})\b'.format(w), flags=re.IGNORECASE).search(features) is None:
        return False
    else:
        return True

def clean(line):
    # get rid of formatted links and keep the comment/title of the link
    pattern = r'''\[(.*?)\]\(.*?\)'''
    repl = r'\1'
    new_line = re.sub(pattern, repl, line)
    # get rid of [deleted] comments
    pattern = r'''\[deleted\]'''
    repl = r''
    new_line = re.sub(pattern, repl, new_line)
    # get rid of links
    pattern = r'''(?i)\b((?:(https|http|ftp|steam|irc|news|mumble|ssh)?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([
                  ^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’]))'''
    new_line = re.sub(pattern, '', new_line)
    # get rid of formatting
    # characters
    pattern = r'''\\\^|\\\*|(:|;){1}(\^){0,1}(\)|\(|\\|\/|s)|&gt;|&lt;'''
    repl = r''''''
    new_line = re.sub(pattern, repl, new_line)
    # italics
    pattern = r'''\*\*(.*)\*\*'''
    repl = r'''\1'''
    new_line = re.sub(pattern, repl, new_line)
    # strikethrough
    pattern = r'''~~(.*)~~'''
    repl = r'''\1'''
    new_line = re.sub(pattern, repl, new_line)
    # superscript
    pattern = r'''\^+(.*)'''
    repl = r'''\1'''
    new_line = re.sub(pattern, repl, new_line)
    # inline code
    pattern = r'''`(.*)`'''
    repl = r''''''
    new_line = re.sub(pattern, repl, new_line)
    # bold
    pattern = r'''\*(.*)\*'''
    repl = r'''\1'''
    new_line = re.sub(pattern, repl, new_line)
    # get rid of unnecessary whitespace
    new_line = " ".join(new_line.split())
    return new_line

def clean_document(lines, reddit=False):
        cleanlines = []
        for line in lines:
            cleanline = clean(line)
            if reddit and len(cleanline.split()) >= __reddit_min_words:
                cleanlines.append(cleanline)
            elif not reddit:
                cleanlines.append(cleanline)
        return cleanlines

def remove_stopwords_line(line):
        newline = line
        for sw in __stopwords:
            stopwordInLine = findWholeWord(sw, line)

            if stopwordInLine is True:
                newline = re.sub(r'\b({0})\b'.format(sw), '', newline)

        newline = re.sub(r'\s+', ' ', newline)
        return newline

def remove_punctuation_line(line):
    new_line = line.maketrans("", "", string.punctuation)
    return new_line

def remove_isolated_punctuation_document(document):
    punctuation_set = set(string.punctuation)
    new_document = []
    for line in document:
        newline = ' '.join(token for token in line.split() if token not in punctuation_set)
        new_document.append(newline)
    return new_document

def remove_trailing_punctuation_document(document):
    new_document = []
    for line in document:
        new_line = ""
        for token in line.split():
            new_token = token.strip(string.punctuation)
            new_line = new_line + " " + new_token
        new_document.append(new_line)
    return new_document

def remove_all_punctuation_document(document):
    punctuation_set = set(string.punctuation)
    new_document = []
    for line in document:
        newline = ' '.join(token for token in line.split() if token not in punctuation_set)
        new_document.append(newline)
    return new_document

def lowercase_document(document):
    new_document = []
    for line in document:
        newline = line.lower()
        new_document.append(newline)
    return new_document

def remove_stopwords_document(lines, reddit=False):
        newlines = []
        for line in lines:
            newline = remove_stopwords_line(line)
            if reddit and len(line.split()) >= __reddit_min_words:
                newlines.append(newline)
            elif not reddit:
                newlines.append(newline)

        return newlines