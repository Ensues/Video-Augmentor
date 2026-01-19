# LIBRARIES

import ffmpeg
import os
import datetime

# FOLDER PREPARATION

# Define input folder

input_folder = r''  # Current directory

# Get the parent directory (Thesis Stuff)

parent_folder = os.path.dirname(input_folder)

# Create the path for the main Augmented folder

augmented_main_folder = os.path.join(parent_folder, 'Augmented Dataset Videos')

# Define output folders

output_brighter_folder = os.path.join(augmented_main_folder, 'Brighter')
output_dimmer_folder = os.path.join(augmented_main_folder, 'Dimmer')
output_noise_folder = os.path.join(augmented_main_folder, 'Noise')
output_translation_folder = os.path.join(augmented_main_folder, 'Translation')
output_superpixel_folder = os.path.join(augmented_main_folder, 'Superpixel')
# List to check

folders_to_create = [
    output_brighter_folder, 
    output_dimmer_folder, 
    output_noise_folder,
    output_translation_folder,
    output_superpixel_folder
]
num_variants = len(folders_to_create)

# Create the output folder if it doesn't exist

os.makedirs(augmented_main_folder, exist_ok=True)
for folder in folders_to_create:
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

# Calculate expected total hours

expected_total_seconds = total_seconds * num_variants
        
# Convert seconds to H:M:S format, shows duration before augmenting

formatted_original_time = str(datetime.timedelta(seconds=int(total_seconds)))
formatted_expected_time = str(datetime.timedelta(seconds=int(expected_total_seconds)))

print(f"Original total duration: {formatted_original_time}")
print(f"Expected total duration across all 4 output folders: {formatted_expected_time}")

# DATA AUGMENTATION

# Limitations
limit_aug = 1  # Set to None to process all, or a number (e.g., 1) to limit
processed_count = 0

augmentations = [
    {'name': 'Brighter', 'folder': output_brighter_folder,         'vf': 'eq=brightness=0.3'},
    {'name': 'Dimmer',   'folder': output_dimmer_folder,           'vf': 'eq=brightness=-0.3'},
    # noise=Luminance=Strength:Function=Uniform
        # Luminance for the brightness
        # Strength for the intensity
        # Uniform to make the noise brighter or darker
    {'name': 'Noise',     'folder': output_noise_folder,            'vf': 'noise=c0s=50:c0f=t+u'},
    # pad=iw+5:ih+5:5:5: Adds 5 pixels of padding to the top and left
    # Tbh don't see much differences at a 5 pixel shift, not sure if its worth keeping
    {'name': 'Translation', 'folder': output_translation_folder,   'vf': 'setpts=PTS-STARTPTS,pad=iw+5:ih+5:5:5:black'},
    # pixelize=width=16:height=16: Tells FFmpeg to divide the image into 16×16 pixel blocks.
    # Not sure if I did it right
    {'name': 'Superpixel', 'folder': output_superpixel_folder,     'vf': 'pixelize=width=16:height=16'}
]

for filename in os.listdir(input_folder):
    if limit_aug is not None and processed_count >= limit_aug:
        print(f"Reached limit of {limit_aug} Stopping")
        break

    if filename.lower().endswith(".mp4"):
        input_path = os.path.join(input_folder, filename)
        processed_count += 1
        
        print(f"\nProcessing Video {processed_count}: {filename}")
        
        # Augmentation loop code
        
        for aug in augmentations:
            output_path = os.path.join(aug['folder'], filename)
            
            # Check if this specific augmentation already exists
            if os.path.exists(output_path):
                print(f"  > Skipping {aug['name']}: Already exists")
                continue
                
            try:
                # Logic: Only apply the specific augmentation filter
                (
                    ffmpeg
                    .input(input_path)
                    .output(output_path, vf=aug['vf']) 
                    .overwrite_output()
                    .run(quiet=True)
                )
                print(f"  > Done: {aug['name']}")
            except ffmpeg.Error as e:
                print(f"  ! Error on {aug['name']}: {e}")

# FINISHING TOUCHES

print("-" * 30)
print("All videos have been augmented")
print(f"Total duration of all source videos: {formatted_original_time}")
print(f"Total duration of augmented videos: {formatted_expected_time}")