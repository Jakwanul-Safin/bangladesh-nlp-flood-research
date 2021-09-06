from json import load
import sys
from tagtogLoader import TagtogLoader

if __name__ == "__main__":
    if len(sys.argv) < 3 or len(sys.argv) > 4:
        raise Exception("python loadTagTogSamples.py [ANNOTATIONS_FOLDER] [OUTPUT_FILE] [Optional: PRELABELLED_SAMPLE_CSV]")
    
    loader = TagtogLoader(sys.argv[1])
    
    loader.load_annotations()
    loader.load_text()
    loader.attach_content_from_file()

    if len(sys.argv) == 4:
        loader.attach_matching_csv(sys.argv[3])
    loader.dataframe().to_csv(sys.argv[2])