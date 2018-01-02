import os

RESULTS_OUTPUT_PATH = os.path.join("results", "graphs")
RESULTS_OUTPUT_PATH_SENTIMENT = os.path.join(RESULTS_OUTPUT_PATH, "sentiment")
RESULTS_OUTPUT_PATH_TOPIC = os.path.join(RESULTS_OUTPUT_PATH, "topic")

os.makedirs(RESULTS_OUTPUT_PATH, exist_ok=True)
os.makedirs(RESULTS_OUTPUT_PATH_SENTIMENT, exist_ok=True)
os.makedirs(RESULTS_OUTPUT_PATH_TOPIC, exist_ok=True)

RESULTS_OUTPUT_PATH_SENTIMENT = os.path.join(RESULTS_OUTPUT_PATH_SENTIMENT, "donutgraph.png")
RESULTS_OUTPUT_PATH_TOPIC = os.path.join(RESULTS_OUTPUT_PATH_TOPIC, "lda.html")

NO_OF_TOPICS = 7
NO_OF_WORDS_TO_DISPLAY = 5
