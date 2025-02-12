# Image Background Removal and Transformation

This project provides a Python script to remove the background from images and transform them into a desired format. It supports both single-image processing and batch processing for directories of images.

![Image Background Removal](https://github.com/Priyal-0911/Image-Background-Removal-and-Transformation/blob/d8e442cf6ca585790e9d85681001cdd12baa02b7/display.jpg)

## Features

- Remove the background from images using the `rembg` library.
- Save the output as `.png` (with transparent background) and transform it to `.jpg`.
- Handle single image processing or batch process all images in a directory.
- Supports common image formats such as `.png`, `.jpg`, `.jpeg`, `.bmp`, and `.gif`.

## Installation

### 1. Clone the repository:

```bash
git clone https://github.com/Priyal-0911/Image-Background-Removal-and-Transformation.git
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

Note: If rembg is not included in requirements.txt, you can install it manually:

```bash
pip install rembg
```

## Usage

The script supports two modes of operation:

Single Image Processing:

To process a single image, run the following command:

```bash

python remove_bg.py -i /path/to/your/image.jpg
```

This will remove the background from the specified image and save it as a .png file, followed by transforming it to a .jpg file.

Directory Processing:

To process all images in a directory, run:

```bash
python remove_bg.py -d /path/to/your/images/directory/
```

The script will process all images in the given directory, removing backgrounds and transforming them as described above.

### Parameters

-i, --image: Specify the path to a single image file.
-d, --directory: Specify the path to a directory containing image files.

### Example

```bash
python remove_bg.py -i /path/to/image.jpg
```

Directory example:

```bash
python remove_bg.py -d /path/to/images/
```

## How It Works

- The script loads the image.
- The background is removed using the rembg library.
- The image is saved as a .png file with a transparent background.
- The image is then transformed into a .jpg file, where the transparent areas are filled with a white background.

## Error Handling

- If a file is not found or cannot be opened as an image, an error message will be displayed.
- If background removal fails, the script will skip the transformation for that image.

## Requirements

Python 3.6+
Pillow library
rembg library
numpy library

To install the dependencies, you can use:

```bash
pip install -r requirements.txt
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Feel free to open issues or submit pull requests. Contributions are always welcome!

