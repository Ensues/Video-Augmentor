# LIBRARIES

import ffmpeg
import os
import datetime

# FOLDER PREPARATION

# Define input folder

input_folder = r'C:\Users\ejans\OneDrive\Documents\Thesis Stuff\Thesis Eric Datasets Cleaned'  # Current directory

# Get the parent directory (Thesis Stuff)

parent_folder = os.path.dirname(input_folder)

# Create the path for the main Augmented folder

augmented_main_folder = os.path.join(parent_folder, 'Augmented Dataset Videos')

# Define output folders

output_brighter_folder = os.path.join(augmented_main_folder, 'Brighter')
output_dimmer_folder = os.path.join(augmented_main_folder, 'Dimmer')
output_noise_folder = os.path.join(augmented_main_folder, 'Noise')

# List to check

folders_to_create = [
    output_brighter_folder, 
    output_dimmer_folder, 
    output_noise_folder
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
    {'name': 'Brighter', 'folder': output_brighter_folder, 'vf': 'eq=brightness=0.3'},
    {'name': 'Dimmer',   'folder': output_dimmer_folder,   'vf': 'eq=brightness=-0.3'},
    # noise=Luminance=Strength:Function=Uniform
        # Luminance for the brightness
        # Stremgth for the intensity
        # Uniform to make the noise brighter or darker
    {'name': 'Salt',     'folder': output_noise_folder,     'vf': 'noise=c0s=50:c0f=t+u'} # White/Static noise
]

for filename in os.listdir(input_folder):
    if limit_aug is not None and processed_count >= limit_aug:
        print(f"Reached limit of {limit_aug}. Stopping.")
        break

    if filename.lower().endswith(".mp4"):
        input_path = os.path.join(input_folder, filename)
        processed_count += 1
        
        print(f"\nProcessing Video {processed_count}: {filename}")
        
        for aug in augmentations:
            output_path = os.path.join(aug['folder'], filename)
            
            if os.path.exists(output_path):
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