import os
import re
import requests
import argparse
import numpy as np
JS_FETCHER_BASE_URL = "https://storage.googleapis.com/data.yt8m.org/2/j/v/"
VIDEO_ID_FETCHER_BASE_URL = "https://storage.googleapis.com/data.yt8m.org/2/j/i/"
METADATA_CSV_FILE = "vocabulary.csv"

def make_get_request(url):
    try:
        resp = requests.get(url)
        resp.raise_for_status()
    except Exception as err:
        return True, err
    else:
        return False, resp.text


def get_knowledge_graph_id(category_names):
    id_mapping_dict = {}
    with open(METADATA_CSV_FILE, "r") as mtd:
        kg_data = mtd.read()

    kg_data = kg_data.split("\n")
    kg_data = [i.split(",") for i in kg_data]
    set_categories = set(category_names)

    for k in kg_data:
        if k[-1] in set_categories:
            id_mapping_dict[k[-1]] = k[-2]

    return id_mapping_dict

def download_video_using_youtube_dl(video_id, output_path):
    command = [
        "./yt-dlp_linux",
        "-x",
        "--audio-format", "mp3",
        "\"http://www.youtube.com/watch?v=%s\"" % str(video_id),
        "-o \"%s\"" % output_path
    ]
    print(" ".join(command))
    filenumber_before = len(os.listdir(args.output_dir))
    os.system(" ".join(command))
    filenumber_after = len(os.listdir(args.output_dir))
    if filenumber_after > filenumber_before:
        return False, ""
    else:
        return True, "Error: file not downloaded"

def run(args):

    if not os.path.exists(args.selected_categories):
        print("provided selected categories path '{}' does not exist.".format(args.selected_categories))
        return

    if not os.path.exists(args.output_dir):
        print("creating output directory: {}".format(args.output_dir))
        os.mkdir(args.output_dir)

    with open(args.selected_categories, "r") as sc_file:
        selected_categories = [line.strip('\n') for line in sc_file if line.strip('\n') != ""]

    if not selected_categories:
        print("no categories selected in input file.")
        return

    id_mapping_dict = get_knowledge_graph_id(selected_categories)
    items_todo = list(id_mapping_dict.items())
    np.random.shuffle(items_todo)
    for key, value in items_todo:
        print("Fetching videos for '{}' category".format(key))
        err1, js_data = make_get_request(JS_FETCHER_BASE_URL+value.split("/")[-1]+".js")
        if err1:
            print("Error: {}, with retrieving JS data for category '{}', skipping".format(str(js_data),key))
            return
        js_data = eval(js_data.lstrip('p("'+value.split("/")[-1]+'",').rstrip(');'))
        tf_records_ids = js_data[2:]
        tf_records_ids = tf_records_ids[:args.number_of_videos + 50] # keep more ids
        tf_records_ids_first_two_chars = [i[:2] for i in tf_records_ids]

        video_ids_list = []
        for ids, two_char_ids in zip(tf_records_ids, tf_records_ids_first_two_chars):
            url = VIDEO_ID_FETCHER_BASE_URL + two_char_ids + "/" + ids + ".js"
            err2, id_data = make_get_request(url)
            if err2:
                continue
            video_id = re.findall(r"[a-zA-Z0-9_-]{11}", id_data)[0]
            video_ids_list.append(video_id)

        limit = 0
        os.makedirs(args.output_dir + "/" + key.replace(" ","_"), exist_ok=True)
        np.random.shuffle(video_ids_list)
        for vid in video_ids_list:
            output_path = args.output_dir + "/" + key.replace(" ","_") + "/"  + "%(id)s.%(ext)s"
            output_path_placeholder = os.path.join(os.path.dirname(args.output_dir), "placeholder") + "/" + key.replace(" ","_") + "/"  + vid
            if os.path.exists(output_path_placeholder):
                continue
            else:
                with open(output_path_placeholder, "w") as f:
                    f.write("")
            err, _ = download_video_using_youtube_dl(vid, output_path)
            if not err:
                limit += 1
                print("Video id: {} downloaded successfully.".format(vid))
            else:
                print("Video id: {} download unsuccessful.".format(vid))
            if limit == args.number_of_videos:
                break

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download videos by category from YouTube-8M dataset")
    parser.add_argument("-sc", "--selected_categories", type=str, required=True, help="Input txt file containing categories seperated by new line.")
    parser.add_argument("-o", "--output_dir", type=str, default="data/yt8m_audios", help="Output directory to store videos")
    parser.add_argument("-n", "--number_of_videos", type=int, default=10, help="Number of videos to be downloaded from each category.")

    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    run(args)