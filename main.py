import ffmpeg
import os
import datetime

# Define input folder
input_folder = r''  # Current directory

# Define output folders
output_brighter_folder = os.path.join(input_folder, 'brighter')
output_dimmer_folder = os.path.join(input_folder, 'dimmer')
output_pepper_folder = os.path.join(input_folder, 'pepper')
output_salt_folder = os.path.join(input_folder, 'salt')

# List to check
folders_to_create = [
    output_brighter_folder, 
    output_dimmer_folder, 
    output_pepper_folder, 
    output_salt_folder
]

# Create the output folder if it doesn't exist
for folder in folders_to_create:
    if not os.path.exists(folder):
        os.makedirs(folder)
        print(f"Created: {folder}")
    else:
        print(f"Already exists: {folder}")

total_seconds = 0

# Calculating the total duration
print("Calculating total duration of all videos...")
for filename in os.listdir(input_folder):
    if filename.lower().endswith(".mp4"):
        path = os.path.join(input_folder, filename)
        try:
            probe = ffmpeg.probe(path)
            duration = float(probe['format']['duration'])
            total_seconds += duration
        except Exception:
            pass
        
# Convert seconds to H:M:S format
formatted_time = str(datetime.timedelta(seconds=int(total_seconds)))

print(f"Total duration of all source videos: {formatted_time}")

# Loop through all files in the input folder
for filename in os.listdir(input_folder):
    if filename.endswith(".mp4"):
        input_path = os.path.join(input_folder, filename)
        output_path = os.path.join(output_folder, filename)
        
        # Skip Existing Logic
        if os.path.exists(output_path):
            print(f"Skipping: {filename} (Already exists)")
            continue
        
        # Shows file being processed
        print(f"Processing: {filename}...")

        try:
            (
                ffmpeg
                .input(input_path)
                # vf for scale, an for audio, metadata for rotational thing
                .output(output_path, vf='scale=-1:480', an=None, metadata='s:v:0 rotate=0')
                .overwrite_output() # Overwrites if file exists
                .run(quiet=True)
            )
        except ffmpeg.Error as e:
            print(f"Error processing {filename}: {e.stderr}")

print("-" * 30)
print("All videos have been processed")
print(f"Total duration of all source videos: {formatted_time}")