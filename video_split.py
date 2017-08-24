from glob import glob
import sys
import os
import subprocess

if not os.path.exists('scenes'):
    os.makedirs('scenes')
if not os.path.exists('metadata'):
    os.makedirs('metadata')


video_dir = str(sys.argv[1])

print "Processing videos in " + video_dir + "..."
videos = glob(video_dir + '/*.mp4')
videos.extend(glob(video_dir + '/*.mkv'))
videos.extend(glob(video_dir + '/*.webm'))
for video in videos[0:3]:
	# Get the basename of the video
	video_basename = os.path.splitext(os.path.basename(video))[0]
	print "Now analyzing " + video
	# Create a directory to hold the scene thumbnails
	if not os.path.exists('scenes/' + video_basename):
		os.makedirs('scenes/' + video_basename)
	ffmpeg_firstcommand =  'ffmpeg -i ' + video + ' -vf "select=eq(pict_type\,I)" -vsync vfr -q:v 2 scenes/' + video_basename + '/' + video_basename + '~%04d.jpg < /dev/null'
	print ffmpeg_firstcommand
	subprocess.call(ffmpeg_firstcommand, shell=True)
