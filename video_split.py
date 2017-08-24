from glob import glob
import sys
import os
import subprocess
import Image
import math

def shannon_entropy(img):

	# calculate the shannon entropy for an image

	histogram = img.histogram()
	histogram_length = sum(histogram)

	samples_probability = [float(h) / histogram_length for h in histogram]

	return -sum([p * math.log(p, 2) for p in samples_probability if p != 0])



if not os.path.exists('scenes'):
    os.makedirs('scenes')
if not os.path.exists('metadata'):
    os.makedirs('metadata')
if not os.path.exists('quarantine'):
	os.makedirs('quarantine')


video_dir = str(sys.argv[1])

print "Processing videos in " + video_dir + "..."
videos = glob(video_dir + '/*.mp4')
videos.extend(glob(video_dir + '/*.mkv'))
videos.extend(glob(video_dir + '/*.webm'))
for video in videos[0:10]:
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

	# SECTION BELOW: This should really be ported to python...

	# Get a list of each keyframe image
	bash_makekeyframelist = 'ls -1 scenes/' + video_basename + '/' + video_basename + '~*.jpg | xargs -n 1 basename > metadata/' + video_basename + '_keyframe_thumbnails.txt'
	subprocess.call(bash_makekeyframelist, shell=True)

	# Glue the image list together with each timestamp
	bash_paste = 'paste metadata/' + video_basename + '_keyframe_thumbnails.txt metadata/' + video_basename + '_keyframe_timestamps.txt > metadata/' + video_basename + '_keyframes.txt'
	subprocess.call(bash_paste, shell=True)

	# Rename the keyframe image with its timestamp
	bash_timestamprename = 'while read -r thumbnail index; do newIndex=$(echo $index - 1 | bc); mv -- "scenes/' + video_basename + '/${thumbnail}" "scenes/' + video_basename + '/' + video_basename + '~${newIndex}.jpg"; done < metadata/' + video_basename + '_keyframes.txt'
	subprocess.call(bash_timestamprename, shell=True)

	# Edge case where the first frame gets assigned to negative one seconds. Fix by renaming to zero.
	bash_fixnegativetime = 'mv "scenes/' + video_basename + '/' + video_basename + '~-1.jpg"  "scenes/' + video_basename + '/' + video_basename + '~0.jpg"'
	subprocess.call(bash_fixnegativetime, shell=True)

	# Post-facto image processing of thumbnails

	# Test for low-energy images. Sad!
	for thumbnail in glob('scenes/' + video_basename + '/*.jpg'):
		image = Image.open(thumbnail)
		entropy_result = shannon_entropy(image)
		if entropy_result <= 2:
			if not os.path.exists('quarantine/' + video_basename):
				os.makedirs('quarantine/'  + video_basename)
			print thumbnail + ' is low energy: ' +  str(entropy_result) + ' to be precise. Sad! Quarantining...'
			thumbnail_basename = os.path.splitext(os.path.basename(thumbnail))[0]
			os.rename(thumbnail, "quarantine/" + video_basename + '/' + thumbnail_basename + '.jpg')
	# Remove baked-in letterboxes
	imagemagick_letterboxcrop = 'find "scenes/' + video_basename + '" -iname "*.jpg" | parallel --no-notice convert {} -gravity South -background white -splice 0x5 -background black -splice 0x5 -fuzz 5% -trim +repage -chop 0x5 -gravity North -background white -splice 0x5 -background black -splice 0x5 -fuzz 5% -trim +repage -chop 0x5 -shave 1x1 {}'
	print 'Now executing ' + imagemagick_letterboxcrop
	subprocess.call(imagemagick_letterboxcrop, shell=True)



