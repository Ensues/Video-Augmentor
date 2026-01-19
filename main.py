# LIBRARIES

import ffmpeg
import os
import datetime
import random
import time

# FOLDER PREPARATION

# Define input folder

input_folder = r''  # Current directory

# Get the parent directory

parent_folder = os.path.dirname(input_folder)

# Create the path for the main Augmented folder

augmented_main_folder = os.path.join(parent_folder, 'Augmented Dataset Videos')

# Define output folders

output_1variant_folder = os.path.join(augmented_main_folder, '1Variant')
output_2variants_folder = os.path.join(augmented_main_folder, '2Variants')
output_final_folder = os.path.join(augmented_main_folder, 'Augmented Data')

# List to check

output_folders = [
    output_1variant_folder, 
    output_2variants_folder, 
    output_final_folder,
]

# Create the output folder if it doesn't exist

os.makedirs(augmented_main_folder, exist_ok=True)
for folder in output_folders:
    os.makedirs(folder, exist_ok=True)
    print(f"Verified folder: {folder}")

# Calculating the total duration

total_seconds = 0

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

# Convert seconds to H:M:S format, shows duration before augmenting

formatted_original_time = str(datetime.timedelta(seconds=int(total_seconds)))

print(f"Original total duration: {formatted_original_time}")

# DATA AUGMENTATION

# Limitations
processed_count = 0
total_augmented_seconds = 0

augmentations = [
    {'name': 'Brighter', 'vf': 'eq=brightness=0.3'},
    {'name': 'Dimmer', 'vf': 'eq=brightness=-0.3'},
    # noise=Luminance=Strength:Function=Uniform
        # Luminance for the brightness
        # Strength for the intensity
        # Uniform to make the noise brighter or darker
    {'name': 'Noise', 'vf': 'noise=c0s=50:c0f=t+u'},
    # pad=iw+5:ih+5:5:5: Adds 5 pixels of padding to the top and left
    # Tbh don't see much differences at a 5 pixel shift, not sure if its worth keeping
    {'name': 'Translation', 'vf': 'setpts=PTS-STARTPTS,pad=iw+5:ih+5:5:5:black'},
    # pixelize=width=16:height=16: Tells FFmpeg to divide the image into 16×16 pixel blocks.
    # Not sure if I did it right
    {'name': 'Superpixel', 'vf': 'pixelize=width=16:height=16'}
]

start = time.time()
for filename in os.listdir(input_folder):

    # A video has a 30% chance of undergoing augmentation
    if filename.lower().endswith(".mp4") and random.randrange(1, 100) <= 30:
        input_path = os.path.join(input_folder, filename)
        processed_count += 1
        
        # Calculate augmented video time
        try:
            probe = ffmpeg.probe(input_path)
            vid_duration = float(probe['format']['duration'])
            total_augmented_seconds += vid_duration # <--- Adding to final total
        except:
            vid_duration = 0
        
        print(f"\nProcessing Video {processed_count}: {filename}")
        variants = []
        
        # Three distinct augmentation occurs per video
        for i in range(len(output_folders)):
            aug = random.choice(augmentations)
            # Repeatedly chooses a variant if the generated variant is chosen previously
            while aug in variants:
                aug = random.choice(augmentations)
            variants.append(aug)

            current_var = variants[len(variants)-1]
            output_path = os.path.join(output_folders[i], filename)

            # Check if this specific augmentation already exists
            if os.path.exists(output_path):
                print(f"  > Skipping Augmentation {i - 1}: Already exists")
                continue
                
            try:
                # Logic: Only apply the specific augmentation filter
                (
                    ffmpeg
                    .input(input_path if i == 0 else os.path.join(output_folders[i-1], filename))
                    .output(output_path, vf=current_var['vf']) 
                    .overwrite_output()
                    .run(quiet=True)
                )
                print(f"  > Done: {current_var['name']}")
            except ffmpeg.Error as e:
                print(f"  ! Error on {current_var['name']}: {e}")

# FINISHING TOUCHES

end = time.time()
formatted_augmented_time = str(datetime.timedelta(seconds=int(total_augmented_seconds)))

print("-" * 30)
print("All videos have been augmented")
print(f"Processing time: {round(end-start, 2)} seconds")
print(f"Total duration of all source videos: {formatted_original_time}")
print(f"Total duration of augmented videos: {formatted_augmented_time}")
print("-" * 30)