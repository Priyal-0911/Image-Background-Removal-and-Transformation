
import os
from PIL import Image, UnidentifiedImageError
import numpy as np
from rembg import remove
import argparse

class preprcessInput:

    def __init__(self):
        self.o_width = None
        self.o_height = None
        self.o_image = None

        self.t_width = None
        self.t_height = None
        self.t_image = None
        self.save_path = None

    def remove_bg(self, file_path: str):
        self.save_path = file_path[:-3]+'.png'
        try:
            pic = Image.open(file_path)
            self.o_width = np.asarray(pic).shape[1]
            self.o_height = np.asarray(pic).shape[0]
            try:
                self.o_channels = np.asarray(pic).shape[2]
            except Exception as e:
                print("Single channel image and error", e)
            #os.remove(file_path) #remove this line as we don't want to delete the original image
            self.o_image = remove(pic)
            self.o_image.save(self.save_path)
            #os.remove(self.save_path) # Remove this line.  We need this file for the next step
            return np.asarray(self.o_image)

        except FileNotFoundError:
            print(f"Error: File not found: {file_path}")
            return None  # Or raise the exception if you want the program to stop

        except UnidentifiedImageError as e:
            print(f"Error: Could not open {file_path} as an image: {e}")
            return None # Or raise

        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return None


    def transform(self, width=768, height=1024):
        #newsize = (width, height) #No longer needed
        self.t_height = self.o_height # Use original height
        self.t_width = self.o_width # Use original width

        pic = self.o_image
        #img = pic.resize(newsize) #No longer resizing

        self.t_image = pic # Assign original image since no resize
        background = Image.new("RGBA", (self.o_width, self.o_height), (255, 255, 255, 255)) # Use original dimensions for the background
        background.paste(pic, mask=pic.split()[3])  # 3 is the alpha channel
        self.save_path = self.save_path[:-3] + '.jpg'
        background.convert('RGB').save(self.save_path, 'JPEG')
        return np.asarray(background.convert('RGB'))



def process_image(image_path, preprocess):
    """Processes a single image: removes background and transforms."""

    try:
        # Check if file exists and is a valid image before processing
        try:
            img = Image.open(image_path)
            img.close()  # close the image to free up the file after checking validity

        except UnidentifiedImageError as e:
            print(f"Error: Could not open {image_path} as an image: {e}")
            return  # Exit function, image is invalid
        except FileNotFoundError:
            print(f"Error: File not found: {image_path}")
            return

        # Process the image
        image_no_bg_arr = preprocess.remove_bg(image_path)
        if image_no_bg_arr is not None:  # Check if remove_bg was successful
            preprocess.transform()  # remove the width and height params so default height and width is not called
            print(f"Successfully processed: {image_path}")
        else:
            print(f"Skipping transform for {image_path} because background removal failed.")

    except Exception as e:
        print(f"An error occurred while processing {image_path}: {e}")


def process_directory(directory_path):
    """Processes all images in a directory."""
    preprocess = preprcessInput()
    for filename in os.listdir(directory_path):
        image_path = os.path.join(directory_path, filename)
        if os.path.isfile(image_path) and image_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):  # Basic image file check
            process_image(image_path, preprocess)


def main():
    """Main function to handle command-line arguments and processing."""
    parser = argparse.ArgumentParser(description="Remove background from images, single image or directory.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-i", "--image", help="Path to a single image file.")
    group.add_argument("-d", "--directory", help="Path to a directory containing image files.")

    args = parser.parse_args()

    if args.image:
        preprocess = preprcessInput()
        process_image(args.image, preprocess)
    elif args.directory:
        process_directory(args.directory)


if __name__ == "__main__":
    main()
