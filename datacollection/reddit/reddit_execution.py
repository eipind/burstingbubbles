import re
from datacollection.reddit import settings as rs
from datacollection import settings
import requests

from datacollection.reddit import reddit_query

class RedditExecution:
    _ENCODED_NEW_LINE = "\n".encode("utf-8")

    # Splits list by n
    @staticmethod
    def split_by_n(l, n):
        for i in range(0, len(l), n):
            yield l[i:i + n]

    def __init__(self):


        client_auth = requests.auth.HTTPBasicAuth(rs.client_id, rs.client_secret)
        post_data = {"grant_type": "client_credentials"}
        h = {"User-Agent": rs.user_agent}
        r_json = requests.post("https://www.reddit.com/api/v1/access_token", auth=client_auth, data=post_data, headers=h)
        r_json = r_json.json()
        self.OAUTH = dict(access_token=r_json['access_token'], token_type=r_json['token_type'],
                          expires_in=r_json['expires_in'], scope=r_json['scope'])
        self.headers = {"User-Agent": rs.user_agent, "Authorization": "bearer " + self.OAUTH['access_token']}

        self._prepare_requests()
        self.file = None

    def _collect_all_comments(self, fullname):
        # ID36 is the xxxxx bit: t2_xxxxx
        article_id36 = fullname.split('_')[1]

        subreddit_url_article = self._query.SUBREDDIT_URL + "comments/" + article_id36

        # 'context' is the number of previous comments you want displayed.
        args_article_query = {'article': article_id36, 'showedits': self._query.COMMENT_SHOW_EDITS,
                              'showmore': self._query.COMMENT_SHOW_MORE, 'sort': self._query.COMMENT_SORT,
                              'context': self._query.COMMENT_CONTEXT}

        r = self._get_request(subreddit_url_article, params=args_article_query)
        all_comments = r[1]['data']['children']
        list_of_more_children = self._traverse_all_comments(all_comments)

        list_of_list_mchild = list(self.split_by_n(list_of_more_children, 100))

        # make args_thread for morechildren api call
        for m_child_list in list_of_list_mchild:

            args_thread = {'children': m_child_list[0]}
            for m_child in m_child_list:
                args_thread['children'] = args_thread['children'] + "," + m_child
            args_thread['link_id'] = fullname
            args_thread['sort'] = self._query.COMMENT_SORT
            args_thread['api_type'] = "json"

            # This API call is used to retrieve the additional comments represented by those stubs, up to 100 at a time.
            r = self._post_request(url="https://oauth.reddit.com/api/morechildren", args=args_thread)
            things_list = r['json']['data']['things']
            self._traverse_more_children_loop(things_list, fullname)

    def _prepare_requests(self):
        self._session = requests.session()
        adapter = requests.adapters.HTTPAdapter(max_retries=10)
        self._session.mount('http://', adapter)

    def _check_response_code(self, status_code):
        if (status_code == 200):
            return
        else:
            message = ''

        if (status_code >= 500 and status_code < 600):
            message = "Something is wrong with Reddit right now."
        elif (status_code == 400):
            message = "Sorry, you've made a bad request!"
            print('Status code:', status_code)
        elif (status_code == 401):
            message = "Sorry, you've made an unauthorized request!"
        elif (status_code == 403):
            message = "Sorry, you've made a forbidden request!"
        elif (status_code == 404):
            message = "Sorry, you've made a request to a subreddit that can't be found!"
        elif (status_code >= 400 and status_code < 500):
            message = "Sorry, something's gone wrong on our end wrong and we don't know what!"
        elif (status_code != 200):
            message = "Sorry, something's gone wrong and we don't know what!"

        message += "\n\t\t\tStatus code: " + str(status_code)
        raise Exception(message)

    def _get_request(self, url, params=None):

        is_args = False
        if params is not None:
            assert type(params) is dict, "args_subreddit_query is not a dictionary."
            is_args = True

        if is_args:
            r_params = {}
            for key, value in params.items():
                r_params[key] = value
            response = self._session.get(url, params=r_params, headers=self.headers)

            self._check_response_code(response.status_code)

            return response.json()
        else:
            return self._session.get(url, headers=self.headers).json()

    def _post_request(self, url, args=None):
        is_args = False
        if args is not None:
            assert type(args) is dict, "args_subreddit_query is not a dictionary."
            is_args = True

        if is_args:
            data = {}
            for key, value in args.items():
                data[key] = value

            response = self._session.post(url, data=data, headers=self.headers)

            self._check_response_code(response.status_code)

            return response.json()
        else:
            return self._session.post(url, headers=self.headers).json()

    # traverse parent comment and all its replies
    # saves them to a collector file, one for each thread
    def _traverse_comment_and_replies(self, parent, m_list):
        if parent["kind"] == "t1":
            body = parent["data"]["body"]

            self._write_data(body)
            if parent["data"]["replies"]:
                for child in parent["data"]["replies"]["data"]["children"]:
                    self._traverse_comment_and_replies(child, m_list)

        elif parent["kind"] == "more":
            for more_child in parent["data"]["children"]:
                m_list.append(more_child)

    # calls methods to tranverse all comments in a submission and their replies
    def _traverse_all_comments(self, all_comments):
        clist = []
        for x in all_comments:
            self._traverse_comment_and_replies(x, clist)
        return clist

    # different method to traverse 'morechildren' as json response differs
    def _traverse_more_children(self, current_more_list, potential_more_list):
        for thing in current_more_list:
            if thing["kind"] == "t1":
                body = thing["data"]["body"]
                self._write_data(body)
            elif thing["kind"] == "more":
                for more_child in thing["data"]["children"]:
                    potential_more_list.append(more_child)

    # effectively a while loop
    # a 'morechildren' call may require more 'morechildren' calls because there may be nested
    # complete when 'potential_more_list' has no elements inside
    def _traverse_more_children_loop(self, current_more_list, fullname):
        potential_more_list = []
        self._traverse_more_children(current_more_list=current_more_list, potential_more_list=potential_more_list)
        while potential_more_list:
            current_more_list = potential_more_list
            clist = list(self.split_by_n(current_more_list, 20))

            things_list = []
            for m_child_list in clist:

                args_thread = {"children": m_child_list[0]}
                for m_child in m_child_list[1:]:
                    args_thread["children"] = args_thread["children"] + "," + m_child

                args_thread["link_id"] = fullname
                args_thread["sort"] = self._query.COMMENT_SORT
                args_thread["api_type"] = "json"
                r = self._post_request(url="https://oauth.reddit.com/api/morechildren", args=args_thread)
                args_thread.clear()
                things_list = r["json"]["data"]["things"]
            current_more_list = things_list
            potential_more_list = []
            self._traverse_more_children(current_more_list=current_more_list, potential_more_list=potential_more_list)

    def run(self, query):

        isinstance(query, reddit_query.RedditQuery)

        self._query = query

        args_subreddit_query = {"count": "10",
                                "include_facets": "false",
                                "limit": self._query.LIMIT,
                                "q": self._query.QUERY,
                                "restrict_sr": "on",
                                "sort": self._query.SUBMISSION_SORT,
                                "t": self._query.SEARCH_T}

        # subreddit_query = self._get_request(self._query.SUBREDDIT_URL + 'search', params=args_subreddit_query)
        subreddit_query = self._get_request(self._query.SUBREDDIT_URL + 'search', params=args_subreddit_query)
        args_subreddit_query.clear()
        r = subreddit_query['data']['children']
        metadata_submission_titles = []
        metadata_submission_permalinks = []
        metadata_submission_fullnames = []

        counter = 0
        print("... Starting to collect comments from submissions in /r/" + self._query.SUBREDDIT + " ...")
        for thing in r:
            title = thing["data"]["title"]
            fullname = thing["data"]["name"]

            metadata_submission_titles.append(title)
            metadata_submission_permalinks.append(thing["data"]["permalink"])
            metadata_submission_fullnames.append(fullname)

            print("Submission:", title +"("+fullname.split('_')[1]+")")
            self._open_writer(settings.OUTPUT_FILE_NAME_TEMPLATE, counter)
            self._collect_all_comments(fullname)
            self._close_writer()

            counter += 1

        if counter == 0:
            print("Unfortunately, no submissions were found! Please try changing your query.")
            exit(0)

        self._write_metadata(metadata_submission_titles, metadata_submission_permalinks, metadata_submission_fullnames)
        print("... Finished collecting comments from submissions ...")

    def runn(self):

        self._query = reddit_query.RedditQueryTest()

        args_subreddit_query = {"count": "10",
                                "include_facets": "false",
                                "limit": self._query.LIMIT,
                                "q": self._query.QUERY,
                                "restrict_sr": "on",
                                "sort": self._query.SUBMISSION_SORT,
                                "t": self._query.TIME_FILTER}

        # subreddit_query = self._get_request(self._query.SUBREDDIT_URL + 'search', params=args_subreddit_query)
        subreddit_query = self._get_request(self._query.SUBREDDIT_URL + 'search', params=args_subreddit_query)
        args_subreddit_query.clear()
        r = subreddit_query['data']['children']
        metadata_submission_titles = []
        metadata_submission_permalinks = []
        metadata_submission_fullnames = []

        counter = 0
        print("... Starting to collect comments from submissions in /r/" + self._query.SUBREDDIT + " ...")
        for thing in r:
            title = thing["data"]["title"]
            fullname = thing["data"]["name"]

            metadata_submission_titles.append(title)
            metadata_submission_permalinks.append(thing["data"]["permalink"])
            metadata_submission_fullnames.append(fullname)

            print("Submission:", title +"("+fullname.split('_')[1]+")")
            self._open_writer(settings.OUTPUT_FILE_NAME_TEMPLATE, counter)
            self._collect_all_comments(fullname)
            self._close_writer()

            counter += 1

        if counter == 0:
            print("Unfortunately, no submissions were found! Please try changing your query.")
            exit(0)

        self._write_metadata(metadata_submission_titles, metadata_submission_permalinks, metadata_submission_fullnames)
        print("... Finished collecting comments from submissions ...")

    def rruunn(self):
        self._query = reddit_query.RedditQueryTest()

        from datacollection.reddit.test import RedditCollection
        rc = RedditCollection()

        rc.run(self._query)


    def _write_data(self, line):
        line = line.replace('\n', '')
        line = line.replace('\t', '')
        line = line.strip()
        self.file.write(line.encode('utf-8'))
        self.file.write(self._ENCODED_NEW_LINE)

    def _write_metadata(self, titles, permalinks, fullnames):
        meta_file = open(settings.OUTPUT_METADATA_FILE_NAME, "w")
        meta_file.seek(0, 0)

        metadata = {"titles": titles, "permalinks": permalinks,
                    "fullnames": fullnames, "count": len(fullnames)}

        import json
        json.dump(metadata, meta_file)

    def _close_writer(self):
        self.file.close()

    def _open_writer(self, filename, number):
        new_filename = re.sub(r"(\.txt)$", str(number) + ".txt", filename)
        self.file = open(new_filename, "wb")
        self.file.seek(0, 0)

    def _open_writer_meta(self, filename):
        self.meta_file = open(filename, "w")
        self.meta_file.seek(0, 0)
