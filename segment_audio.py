import os
from tqdm import tqdm
import random
import time
import numpy as np
import librosa
import soundfile as sf

# seed everything
# random.seed(42)
# np.random.seed(42)

folder = "/mnt/fast/nobackup/scratch4weeks/hl01486/project/youtube-8m-videos-downloader/data"
# recursively find how many files in this folder
def find_files(folder):
    count = 0
    for root, dirs, files in os.walk(folder):
        for file in files:
            count += 1
    return count

def segment_audio_rand(audio_path, target_path, length=10000):
    # Load the audio file without converting to mono
    audio, sr = librosa.load(audio_path, sr=None, mono=False)
    if len(audio.shape) == 1:
        audio = np.expand_dims(audio, axis=0)
    audio_duration_ms = audio.shape[-1] / sr * 1000

    # If padding is needed
    if audio_duration_ms < length:
        padding_length = int((length - audio_duration_ms) * sr / 1000)
        padding = np.zeros((audio.shape[0], padding_length))
        audio = np.concatenate((audio, padding), axis=1)

    retry_time = 5
    while retry_time > 0:
        # Random start time in milliseconds, convert to samples
        start_time_ms = random.randint(0, int(audio_duration_ms - length))
        start_sample = int(start_time_ms * sr / 1000)

        # Calculate the end sample
        end_sample = start_sample + int(length * sr / 1000)

        # Segment the audio
        segment = audio[:, start_sample:end_sample]

        # Update the target path
        target_path_updated = target_path.replace(".mp3", f"_{start_time_ms//1000}_{length//1000}.mp3")
        # Check if audio is silent (for one of the channels or the mean)
        if np.max(np.abs(segment)) < 0.05:
            retry_time -= 1
            if retry_time == 0:
                print("Silent audio file %s" % audio_path, np.max(np.abs(segment)))
                return False
            continue
        else:
            # Export the segment
            sf.write(target_path_updated, segment.T, sr, format='mp3')  # Transpose to write correctly
            break
    assert os.path.exists(target_path_updated) and os.path.getsize(target_path_updated) > 0
    return True

# Define your source and target directories
source_dir = 'data/yt8m_audios'
target_dir = 'data/yt8m_audios_segmented'

retry_times = 50

while retry_times > 0:
    retry_times -= 1
    # Walk through the source directory
    todo = list(os.walk(source_dir))
    np.random.shuffle(todo)
    for subdir, dirs, files in tqdm(todo):
        for file in files:
            # Construct the full file path
            file_path = os.path.join(subdir, file)
            
            # Construct the relative path to maintain the subfolder structure
            relative_path = os.path.relpath(subdir, source_dir)
            
            # Construct the target subdirectory and file paths
            target_subdir = os.path.join(target_dir, relative_path)
            target_file_path = os.path.join(target_subdir, os.path.splitext(file)[0] + ".mp3")
            
            # Create the target subdirectory if it doesn't exist
            os.makedirs(target_subdir, exist_ok=True)
            
            # Check if the file is an audio file (mp3, webm, or m4a)
            if file.lower().endswith(('.mp3', '.webm', '.m4a')):
                try:
                    finished = segment_audio_rand(file_path, target_file_path)
                    if finished:
                        print("remove file: {}".format(file_path))
                        os.remove(file_path)
                except Exception as e:
                    import traceback
                    traceback.print_exc()
                    print("Error segmenting file: {}".format(file_path))
                    continue
    time.sleep(3600)