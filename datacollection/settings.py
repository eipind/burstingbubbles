import os

dir_path = os.path.join("tmp", "input")
os.makedirs(dir_path, exist_ok=True)

OUTPUT_FILE_NAME_TEMPLATE = os.path.join(dir_path ,"collector.txt")
OUTPUT_METADATA_FILE_NAME = os.path.join(dir_path, "collector_metadata.json")
