######################## ENVIRONMENT ########################
eval "$('/mnt/fast/nobackup/users/hl01486/miniconda3/bin/conda' 'shell.bash' 'hook' 2> /dev/null)"
conda activate avgen
which python

cd /mnt/fast/nobackup/scratch4weeks/hl01486/project/youtube-8m-videos-downloader

python3 /mnt/fast/nobackup/scratch4weeks/hl01486/project/youtube-8m-videos-downloader/segment_audio.py