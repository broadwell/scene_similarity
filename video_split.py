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
	# Create a directory to hold the keyframe thumbnails
	if not os.path.exists('scenes/' + video_basename):
		os.makedirs('scenes/' + video_basename)
	# Construct the ffmpeg command to get keyframes
	ffmpeg_getiframes =  'ffmpeg -i ' + video + ' -vf "select=eq(pict_type\,I)" -vsync vfr -q:v 2 scenes/' + video_basename + '/' + video_basename + '~%04d.jpg < /dev/null'
	print 'Now executing: ' + ffmpeg_getiframes
	# Call ffmpeg
	subprocess.call(ffmpeg_getiframes, shell=True)

	# Construct the ffprobe command to get the timestamp of each keyframe in seconds
	ffprobe_gettimestamps = "ffprobe -select_streams v -show_frames -of csv " + video + " | grep -n I | cut -d ',' -f 6 | awk '{print int($1)}' > metadata/" + video_basename + "_keyframe_timestamps.txt"
	print 'Now executing: ' + ffprobe_gettimestamps
	# Call ffprobe
	subprocess.call(ffprobe_gettimestamps, shell=True)

