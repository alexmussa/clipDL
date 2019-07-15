# Code written by Alex Mussa (amussa@gatech.edu) for the Georgia Institute of Technology.

from ffmpy import FFmpeg
from subprocess import PIPE, CalledProcessError, check_call, Popen, check_output
from argparse import RawTextHelpFormatter
import csv
import sys
import os
import subprocess
import youtube_dl
import argparse
import time
import datetime
import shutil

parser = argparse.ArgumentParser(description='Parse the CSV,' \
 +'Download the YouTube videos, and Clip them to specified duration.', \
 formatter_class=RawTextHelpFormatter)

parser.add_argument('CSV_location', action="store", help = 'Full path to the '+ \
'location of the CSV file.', metavar = 'FLOC')

parser.add_argument('-f','--CSV-filename', action="store", \
default = 'AE_dataset.csv', help = 'Filename of the csv, including the extension.'+ \
'\nDefault: \'AE_dataset.csv\'')

parser.add_argument('CLIP_destination', action = "store", metavar='DEST', help = \
'Full path to the destination where clips are to be stored.')

parser.add_argument('-o','--operation-mode', type=int, \
default = '1', choices=range(1,4), help='1: Download full videos into a folder,'+ \
' \'temp\', and clip into a folder, \'clips\' at DEST.\n2: Does the same as '+ \
'operation mode 1, but DELETES the temp folder. \nNOTE: Re-execution without temp folder '+ \
'will require full dataset download or stream (opmode 3).\n3: Generate clips from a stream of the '+ \
'videos and only saves the clips.')


#Class used for the return list of clip data from the function csv_parse.
class VideoClip(object):
  def __init__(self,
               file_name,
               yt_id,
               startmin,
               startsec,
               stopmin,
               stopsec,
               cat):
    self.file_name = file_name
    self.yt_id     = yt_id
    self.startmin  = startmin
    self.startsec  = startsec
    self.stopmin   = stopmin
    self.stopsec   = stopsec
    self.cat       = cat

def main():
    global args
    args = parser.parse_args()

    clips_info_list = csv_parse(args.CSV_location,args.CSV_filename)
    if args.operation_mode == 1 or args.operation_mode == 2:
        downloader(clips_info_list,args.CLIP_destination)
    clipper(clips_info_list,args.CLIP_destination,args.operation_mode)
    if args.operation_mode == 2:
        shutil.rmtree(args.CLIP_destination+'/temp/', ignore_errors=True)

#Parse the CSV file into a list containing VideoClip class entries.
def csv_parse(CSV_location,CSV_filename):
     # Error message if AE_dataset.csv not found at CSV_loc.
    if not os.path.exists(CSV_location+'/'+CSV_filename):
      print ('ERROR: CSV File '+CSV_location[:-1]+'/'+CSV_filename+' not found.'+ \
    '\nExiting...\n')
      sys.exit(0)

    # Parse csv data.
    vid_data = []
  
    with open((CSV_location+'/'+CSV_filename), 'rt') as fil:
        reader = csv.reader(fil)
        vid_data = list(reader)
        clips = []  

        for index, vid in enumerate(vid_data,0): 
            yt_id    = vid[0]
            startmin = vid[1] 
            startsec = vid[2] 
            stopmin  = vid[3] 
            stopsec  = vid[4] 
            cat      = vid[5] 
            
            file_name = yt_id+'_'+startmin+'_'+startsec+'_'+stopmin+ \
            '_'+stopsec+'_'+cat
            
            clips.append(VideoClip(file_name,yt_id,startmin,startsec, \
            stopmin,stopsec,cat))

    return clips

def downloader(CLIP_list, CLIP_dest):
    
    dir_dest = CLIP_dest

    if not os.path.exists(dir_dest):
        print ('ERROR: Clip destination ',CLIP_dest,' not found. \nExiting...\n')
        sys.exit(0)
    
    #Make a temp folder in CLIP_dest for download to be stored for clipping,
    #if non-existent
    if os.path.isdir(CLIP_dest+'temp') != True:
        os.mkdir(CLIP_dest+'temp')
    else:
        print('Temp directory already exists at location:', CLIP_dest)
    
    #Establish previous clip in case video with multiple clips to prevent multi download.
    previous_video = ''
    #Open the logfile for appending
    logfile = open("log.txt", "a")

    # Use youtube_dl to download the videos
    for index, clip in enumerate(CLIP_list,0):
        #Check if file already exists at location or if its the same as previous.
        if (os.path.exists(dir_dest+'/temp/'+clip.yt_id+'.mp4') is True) or \
            (previous_video == clip.yt_id):
            print('Video file',dir_dest,'/temp/',clip.yt_id,'.mp4 already exists!' \
            ' Skipping download.')
            continue
        #Check if file is partially downloaded due to previous abort or failure.
        if os.path.exists(dir_dest+'/temp/'+clip.yt_id+'.mp4.part') is True:
            print('File',dir_dest,'/temp/',clip.yt_id,'.mp4 was partially', \
            'downloaded. Deleting and redownloading...')
            os.remove(dir_dest+'/temp/'+clip.yt_id+'.mp4.part')
        previous_video = clip.yt_id

        #Addresses issue where yt_id starts with a minus sign.
        if clip.yt_id[:1] == '-':
            try:
                check_call(['youtube-dl','-i', \
                '-f','best[ext=mp4]', \
                #'--skip-unavailable-fragments', \
                '-o',dir_dest+'/temp/'+clip.yt_id+'.mp4', \
                '--',clip.yt_id], stderr=logfile) #output error to logfile.
            except CalledProcessError as e:
                continue
        else:
            try:    
                check_call(['youtube-dl','-i', \
                '-f','best[ext=mp4]', \
                #'--skip-unavailable-fragments', \
                '-o',dir_dest+'/temp/'+clip.yt_id+'.mp4', \
                clip.yt_id], stderr = logfile)
            except CalledProcessError as e:
                continue
    #Write timestamp to the logfile
    ts = time.time()
    logfile.write('The above errors occurred while downloading on '+ \
    datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S'))
    logfile.close()
    
    return print('Temp files were successfully downloaded into destination', \
    'location at:', dir_dest,'/temp.')
          
def clipper(CLIP_list, CLIP_dest, OPMODE):
    op_mode=OPMODE
    dir_dest = CLIP_dest
    current_dir = os.getcwd()

    #Make a folder in CLIP_dest for clips to be stored.
    if os.path.isdir(CLIP_dest+'clips') != True:
        os.mkdir(CLIP_dest+'clips')
    else:
        print('Clips directory already exists at location:', CLIP_dest)

    #Open the logfile for appending
    logfile = open("log.txt", "a")

    for index, clip in enumerate(CLIP_list,0):
        #Check if clip already exists at location or if its the same as previous.
        if os.path.exists(dir_dest+'/clips/'+clip.file_name+'.mp4') is True:
            print('Video clip',dir_dest,'/',clip.file_name,'.mp4 already exists!' \
            ' Skipping download.')
            continue
        #Skip missing downloads from temp.
        if op_mode == 1 or op_mode == 2:
            if os.path.exists(dir_dest+'/temp/'+clip.yt_id+'.mp4') is False:
                print('Downloaded video at ',dir_dest+'/temp/'+clip.yt_id+'.mp4 is' \
                'missing. Skipping this clip.')
                continue
        #Check if file is partially downloaded due to previous abort or failure.
        if os.path.exists(dir_dest+'/'+clip.file_name+'.mp4.part') is True:
            print('Video clip',dir_dest,'/',clip.file_name,'.mp4 was partially', \
            'finished. Deleting and reclipping...')
            os.remove(dir_dest+'/'+clip.file_name+'.mp4.part')
        if op_mode == 1 or op_mode == 2:
            try:
                check_call(['ffmpeg', \
                '-i','file:'+dir_dest+'/temp/'+clip.yt_id+'.mp4', \
                '-ss',str((int(clip.startmin)*60 + int(clip.startsec))), \
                '-t',str(((int(clip.stopmin)*60-int(clip.startmin)*60)+(int(clip.stopsec)-int(clip.startsec)))), \
                '-strict','-2', clip.file_name+'.mp4'])
                os.rename(current_dir+'/'+clip.file_name+'.mp4',CLIP_dest+'/clips/'+clip.file_name+'.mp4')
                print('Finished clipping: '+clip.file_name+'.mp4')
            except CalledProcessError as e:
                logfile.write('An error occurred during temp clipping for the clip '+clip.yt_id+'.')
                continue
        if op_mode == 3:
            url = subprocess.check_output('youtube-dl -f 22 --get-url http://www.youtube.com/watch?v='+\
            clip.yt_id, shell = True).decode("utf-8")
            try:
                check_call(['ffmpeg', \
                '-ss',str((int(clip.startmin)*60 + int(clip.startsec))), \
                '-i', url[:-1], \
                '-t',str(((int(clip.stopmin)*60-int(clip.startmin)*60)+(int(clip.stopsec)-int(clip.startsec)))), \
                '-c:a','copy', clip.file_name+'.mp4'], shell = False)
                os.rename(current_dir+'/'+clip.file_name+'.mp4',CLIP_dest+'/clips/'+clip.file_name+'.mp4')
            except CalledProcessError as e:
                logfile.write('An error occurred during stream clipping for the clip '+clip.yt_id+'.')
                continue
    #Write timestamp to the logfile
    ts = time.time()
    logfile.write('The above errors occurred while clipping on '+ \
    datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S'))
    logfile.close()

if __name__ == '__main__':
    main()