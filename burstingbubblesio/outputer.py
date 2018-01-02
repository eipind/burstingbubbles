import matplotlib.pyplot as plt
from nlp import settings as nlp_settings
from datacollection import settings as datacollection_settings
import json
import re
import os


class Outputer:

    def __init__(self, sentimentresults):

        with open(datacollection_settings.OUTPUT_METADATA_FILE_NAME, 'r') as json_data:
            metadata = json.load(json_data)
        topic_contents = []
        link_template1 = '''<h><a href="https://www.reddit.com'''
        link_template2 = '''" target="_blank">'''
        link_template3 = '''</a></h>'''

        sentiment_link_template1 = '''<img src="..\\..\\'''
        sentiment_link_template2 = '''" alt="'''
        sentiment_link_template3 = '''" style="width:'''
        sentiment_link_template4 = '''px;height:'''
        sentiment_link_template5 = '''px;">'''

        self._starting_topic_page()
        self._starting_sentiment_page()
        # amount of sentiment results should be the same as the topic modelling results
        for counter in range(0,len(sentimentresults)):

            title = metadata['titles'][counter]
            permalink = metadata['permalinks'][counter]
            html_link = link_template1 + permalink + link_template2 + title + link_template3

            self._topic_loop(counter, html_link)
            self._sentiment_loop(counter, sentimentresults, title, html_link, sentiment_link_template1,
                                 sentiment_link_template2, sentiment_link_template3,sentiment_link_template4,
                                 sentiment_link_template5)

        self._end_pages()

    def _sentiment_loop(self, counter, sent_results, title, html_link, l1, l2, l3, l4, l5):
        sentiment_filename = re.sub(r"(\.png)$", str(counter) + ".png", nlp_settings.RESULTS_OUTPUT_PATH_SENTIMENT)
        self.create_sentiment_donut(sent_results[counter][1], sentiment_filename)
        width = 340
        height = 12
        img = l1 + sentiment_filename + l2 + title + '''">'''

        self._sentiment_file.write('<div>')
        self._sentiment_file.write(html_link)
        self._sentiment_file.write('</div>')
        self._sentiment_file.write('<div>')
        self._sentiment_file.write(img)
        self._sentiment_file.write('</div>')

    def _topic_loop(self, counter, html_link):
        topic_filename = re.sub(r"(\.html)$", str(counter) + ".html", nlp_settings.RESULTS_OUTPUT_PATH_TOPIC)
        topic_file = open(topic_filename, 'r')
        topic_contents = topic_file.readlines()

        self._topic_file.write('<div>')
        self._topic_file.write(html_link)
        self._topic_file.writelines(topic_contents)
        self._topic_file.write('</div>')

    def show_output(self):
        import webbrowser
        webbrowser.open(self._topic_filename, new=1)
        webbrowser.open(self._sentiment_filename, new=2)

    def _starting_sentiment_page(self):
        self._sentiment_filename = os.path.join("results", "webpage")
        self._sentiment_filename = os.path.join(self._sentiment_filename, "senitmentwebpage.html")
        self._sentiment_file = self._start_page(self._sentiment_filename, "Bursting Bubbles: Sentiment Analysis")

    @staticmethod
    def _start_page(filepath, title):
        dir = os.path.dirname(filepath)
        os.makedirs(dir, exist_ok=True)
        file_obj = open(filepath, 'w')
        file_obj.seek(0, 0)
        start_string = '''<!DOCTYPE html>
                                    <html>
                                        <head>
                                        <style type="text/css">
                                            a {font-family:"Impact", Charcoal, sans-serif;font-size:25pt;cursor: auto}
                                            a:link {color:blue;}
                                            a:visited {color: #660066;}
                                            a:hover {text-decoration: none; color: #ff9900; font-weight:bold;}
                                            a:active {color: #ff0000;text-decoration: none}
                                            title {font-family:"Impact", Charcoal, sans-serif;font-size:40pt}
                                        </style>
                                    </head>
                                <body>
                                <title>''' + title + '''</title>
                                '''

        file_obj.write(start_string)
        return file_obj

    def _starting_topic_page(self):
        self._topic_filename = os.path.join("results", "webpage")
        self._topic_filename = os.path.join(self._topic_filename,"topicwebpage.html")
        self._topic_file = self._start_page(self._topic_filename, "Bursting Bubbles: Topic Modelling")


    def _end_pages(self):
        end_string = '''</body>
                    </html>'''

        self._topic_file.write(end_string)
        self._sentiment_file.write(end_string)

    # The slices will be ordered and plotted counter-clockwise.
    def create_sentiment_donut(self, sizes, filename):
        labels = 'Positive', 'Negative', 'Neutral'
        # sizes = [1, 1, 12]
        colors = ['#90F500', '#CC0000', '#004080']
        explode = (0, 0, 0)  # explode a slice if required

        plt.pie(sizes, explode=explode, labels=labels, colors=colors,
                autopct='%1.1f%%', shadow=False, startangle=90)

        # draw a circle at the center of pie to make it look like a donut
        centre_circle = plt.Circle((0, 0), 0.75, color='black', fc='white', linewidth=0)
        fig = plt.gcf()
        fig.gca().add_artist(centre_circle)

        # Set aspect ratio to be equal so that pie is drawn as a circle.
        plt.axis('equal')
        plt.savefig(filename, bbox_inches='tight')
        plt.close()