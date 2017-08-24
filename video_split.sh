# Usage: video_split.sh video.mp4

# Get the video name without the file extension for later use.
filebasename=${1##*/}
videobasename=${filebasename%.*}

# Make directories to hold images and metadata
mkdir -p scenes/${videobasename}/
mkdir -p metadata

# Extract keyframes. Use tilde because both - and _ are present in Google ID's,
# so it can cause problems for simple splitting methods later on if either are used
# to separate GUID from frame number.
# Use up to four digits for frame namespace in case # of scenes is high.

ffmpeg -i $1  -vf "select=eq(pict_type\,I)" -vsync vfr -q:v 2 scenes/${videobasename}/${videobasename}~%04d.jpg  </dev/null
# Get the keyframe numbers
#ffprobe -select_streams v -show_frames -show_entries frame=pict_type -of csv $1 | grep -n I | cut -d ':' -f 1 > metadata/${videobasename}_keyframe_indices.txt
# Get the timestamp in seconds
ffprobe -select_streams v -show_frames -of csv $1 | grep -n I | cut -d ',' -f 6 | awk '{print int($1)}' > metadata/${videobasename}_keyframe_timestamps.txt



# Rename keyframes with their frame numbers
ls -1 scenes/${videobasename}/${videobasename}~*.jpg | xargs -n 1 basename > metadata/${videobasename}_keyframe_thumbnails.txt
paste metadata/${videobasename}_keyframe_thumbnails.txt metadata/${videobasename}_keyframe_timestamps.txt > metadata/${videobasename}_keyframes.txt
while read -r thumbnail index; do newIndex=$(echo $index - 1 | bc); mv -- "scenes/$videobasename/${thumbnail}" "scenes/$videobasename/${videobasename}~${newIndex}.jpg"; done < metadata/${videobasename}_keyframes.txt
# Edge case where the first frame gets assigned to negative one seconds. Fix by renaming to zero.
mv  "scenes/$videobasename/${videobasename}~-1.jpg"  "scenes/$videobasename/${videobasename}~0.jpg"
# 
# Cleanup
rm metadata/${videobasename}_keyframe_timestamps.txt
rm metadata/${videobasename}_keyframe_thumbnails.txt
rm metadata/${videobasename}_keyframes.txt
