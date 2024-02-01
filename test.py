# import library
import os
import random

folder = "/mnt/fast/nobackup/scratch4weeks/hl01486/project/youtube-8m-videos-downloader/data"

# recursively find how many files in this folder
def find_files(folder):
    count = 0
    for root, dirs, files in os.walk(folder):
        for file in files:
            count += 1
    return count

# call this in main
if __name__ == "__main__":
    find_files(folder)