# Aberrant Event CSV Parser, Downloader, and Clipper

This tool was developed for the parsing, downloading,
and clipping of the Aberrant Event dataset.

# Installation and Execution

To use this tool, you must have youtube-dl and ffmpeg 
installed on your computer.

1.) Clone this repository via 'git clone https://github.com/alexmussa/clipDL.git'  

2.) Install ffmpy (https://pypi.org/project/ffmpy/) and youtube-dl (https://ytdl-org.github.io/youtube-dl/download.html) manually following the links provided. 

3.) Run the command: 

```bash
cd ~/path_to/clone_location/clip-dl
python clip_DL.py [-h] [-f CSV_FILENAME] [-o {1,2,3}] FLOC DEST
```

FROM HELP:

```bash
positional arguments:
  FLOC                  Full path to the location of the CSV file.
  DEST                  Full path to the destination where clips are to be stored.

optional arguments:
  -h, --help            show this help message and exit
  -f CSV_FILENAME, --CSV-filename CSV_FILENAME
                        Filename of the csv, including the extension.
                        Default: 'AE_dataset.csv'
  -o {1,2,3}, --operation-mode {1,2,3}
                        1: Download full videos into a folder, 'temp', and clip into a folder, 'clips' at DEST.
                        2: Does the same as operation mode 1, but DELETES the temp folder. 
                        NOTE: Re-execution without temp folder will require full dataset download or stream (opmode 3).
                        3: Generate clips from a stream of the videos and only saves the clips.
```
# Additional Information

## Filename Output

The file nameing of the output clips is as follows:
                    
'YouTubeID_StartMinute_StartSecond_EndMinute_EndSecond_Category.mp4'

## More on operation modes:

Operation Mode 1 -  Directly downloads full-length videos from youtube into a foldaer called 'temp'. Once all downloads of
                        every   unique YouTube ID in the first column of the CSV file is completed, FFMPEG is called to clip 
                        the files to their appropriate clip lengths, specified by the CSV file columns 2-5.
                        
Operation Mode 2 -  Same as Operation Mode 1, but clears the temp folder after completetion. If you plan to change the CSV 
                        clipping times, this method is not recommended as a full redownload will be neccesary.

Operation Mode 3 -  Starts by obtaining direct download link with youtube-dl and streams the video to FFMPEG for clipping.      
                        Does not download the full length videos to a local location. If you plan to change the CSV clipping 
                        times, this method is not recommended as restreaming will be neccesary.

## Version Notes:

Initial Release:    First commit.

1.0:                Added argparse for help menu support, fixed bug where yt-id starting with minus sign wouldnt download,  
                    added an error log to record if subprocess.check_call() generates an error, added 3 Operation modes, 
                    added option to specify filename.
