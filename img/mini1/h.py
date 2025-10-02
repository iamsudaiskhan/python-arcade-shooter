from PIL import Image
import os

def crop_images(input_folder, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in os.listdir(input_folder):
        if filename.lower().endswith(".png"):
            input_path = os.path.join(input_folder, filename)
            with Image.open(input_path) as img:
                width, height = img.size

                # Make sure the image is big enough
                # if height <= 59 or width <= (38 + 66):
                #     print(f"Skipping {filename}: image dimensions too small.")
                #     continue

                # Crop (left, upper, right, lower)
                left = 128-128    #(right-left)
                top = 128-80
                right = width - (128-128)
                bottom = height

                cropped_img = img.crop((left, top, right, bottom))
                output_path = os.path.join(output_folder, filename)
                cropped_img.save(output_path)
                print(f"Cropped and saved: {output_path}")

# Example usage:
input_folder = "Run"     # Folder with original PNG images
output_folder = "output_images"   # Folder to save cropped images
crop_images(input_folder, output_folder)
