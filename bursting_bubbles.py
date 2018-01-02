if __name__ == "__main__":
    from burstingbubblesio.input_window import Inputer
    from burstingbubblesio.outputer import Outputer
    from datacollection.reddit.reddit_query import RedditQuery
    from datacollection.reddit.reddit_execution import RedditExecution
    from nlp.nlp_core import NLPCore

    inputer = Inputer()
    bb_in_dict = inputer.get_query()

    query = RedditQuery(bb_in_dict["Query:"], bb_in_dict["Subreddit:"], bb_in_dict["Sorted by:"], bb_in_dict["Links from:"], bb_in_dict["Limit:"])
    redditexec = RedditExecution()
    redditexec.run(query)
    # redditexec.rruunn()

    nlpcore = NLPCore()
    nlpcore.run()

    sentiment_results = nlpcore.get_sentiment_results()

    outputer = Outputer(sentiment_results)
    outputer.show_output()



