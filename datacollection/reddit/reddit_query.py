# TODO: Add syntax field to RedditQuery class
LIMIT = "10"
COUNT = "0"
SUBMISSION_SHOW_MORE = "true"
SUBMISSION_SHOW_EDITS = "true"
COMMENT_SORT = "top"
COMMENT_SHOW_MORE = "true"
COMMENT_SHOW_EDITS = "true"
COMMENT_CONTEXT = "0"
SYNTAX = "lucene"

class RedditQuery():
    def __init__(self, QUERY, SUBREDDIT, SUBMISSION_SORT, TIME_FILTER, LIMIT="10"):
        self.QUERY = QUERY.strip().lower()
        self.SUBREDDIT = SUBREDDIT.strip().lower()
        self.SUBREDDIT_URL = "https://oauth.reddit.com/r/" + SUBREDDIT.strip().lower() + "/"

        self.LIMIT = LIMIT
        self.COUNT = COUNT

        self.TIME_FILTER = TIME_FILTER.lower()
        self.SUBMISSION_SORT = SUBMISSION_SORT.lower()
        self.SUBMISSION_SHOW_MORE = SUBMISSION_SHOW_MORE
        self.SUBMISSION_SHOW_EDITS = SUBMISSION_SHOW_EDITS

        self.COMMENT_SORT = COMMENT_SORT
        self.COMMENT_SHOW_MORE = COMMENT_SHOW_MORE
        self.COMMENT_SHOW_EDITS = COMMENT_SHOW_EDITS
        self.COMMENT_CONTEXT = COMMENT_CONTEXT

class RedditQueryTest(RedditQuery):
    def __init__(self):
        super(RedditQueryTest, self).__init__(QUERY="What show had you hooked right off the pilot episode?",
                                              SUBREDDIT="AskReddit".lower(),
                                              SUBMISSION_SORT="relevance",
                                              TIME_FILTER="all",
                                              LIMIT="3")