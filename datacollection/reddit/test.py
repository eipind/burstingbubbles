import praw
from datacollection.reddit import settings as rs
from datacollection import settings as dcs
from prawcore import NotFound
from datacollection.reddit.reddit_query import RedditQuery
import re

class RedditCollection:

    _ENCODED_NEW_LINE = "\n".encode("utf-8")

    def __init__(self):
        self._reddit = praw.Reddit(client_id=rs.client_id, client_secret=rs.client_secret, user_agent=rs.user_agent)

    def is_subreddit(self, sub):
        exists = True
        try:
            self._reddit.subreddits.search_by_name(sub, exact=True)
        except NotFound:
            exists = False
        return exists

    def run(self, query):
        assert isinstance(query, RedditQuery), "query is not of type RedditQuery"

        self._meta_file = open(dcs.OUTPUT_METADATA_FILE_NAME, "w")
        self._meta_file.seek(0, 0)
        self._query = query

        submission_list = self._get_submissions()

        metadata = {'titles':[], 'permalinks':[], 'fullnames':[], 'count':None}
        counter = 0
        for submission in submission_list:

            if counter == 0:
                print("... Starting to collect comments from submissions in /r/" + self._query.SUBREDDIT + " ...")

            sub_metadata = self._get_metadata(submission)
            metadata.get('titles').append(sub_metadata.get('title'))
            metadata.get('permalinks').append(sub_metadata.get('permalink'))
            metadata.get('fullnames').append(sub_metadata.get('fullname'))

            comments = self._get_comments(submission, self._query.COMMENT_SORT)

            #TODO: appropriate line below
            print("Submission #", (counter+1), ":", sub_metadata.get("title"), " (", sub_metadata.get("fullname"), ")", sep="")
            writer = self._open_writer(dcs.OUTPUT_FILE_NAME_TEMPLATE, counter)
            for comment in comments:
                self._write_data(writer, comment)
            writer.close()

            counter += 1

        if counter == 0:
            print("Unfortunately, no submissions were found! Please try changing your query.")
            exit(0)
        else:
            print("... Finished collecting comments from submissions ...")
            metadata['count'] = counter
            self._write_metadata(metadata)

    @staticmethod
    def _remove_whitespace(line):
        line = line.replace('\n', '')
        line = line.replace('\t', '')
        line = line.strip()
        return line

    def _write_data(self, file, line):
        file.write(line.encode('utf-8'))
        file.write(self._ENCODED_NEW_LINE)

    def _open_writer(self, filename, number):
        new_filename = re.sub(r"(\.txt)$", str(number) + ".txt", filename)
        file = open(new_filename, "wb")
        file.seek(0, 0)
        return file

    def _get_submissions(self):
        subreddit = self._query.SUBREDDIT
        query = self._query.QUERY
        limit = self._query.LIMIT
        time_filter = self._query.TIME_FILTER
        submission_sort = self._query.SUBMISSION_SORT
        syntax = "lucene"

        subreddit = self._reddit.subreddit(subreddit)

        submission_list = list(
            subreddit.search(query=query, sort=submission_sort, syntax=syntax, time_filter=time_filter, limit=int(limit)))
        return submission_list

    def _get_metadata(self, submission):
        fullname = submission.fullname
        title = submission.title
        permalink = submission.permalink
        return locals()

    def _get_comments(self, submission, comment_sort):
        # TODO: assert submission and comment_sort

        submission.comments.replace_more(limit=0)
        submission.comment_sort = comment_sort
        comments = submission.comments.list()
        stripped_comments = []

        for comment in comments:
            stripped_comment = self._remove_whitespace(comment.body)
            stripped_comments.append(stripped_comment)

        return stripped_comments

    def _write_metadata(self, metadata):
        from json import dump
        dump(metadata, self._meta_file)