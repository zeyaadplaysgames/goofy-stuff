import sys
from PIL import Image

def image_to_ascii(image_path, output_width=100, char_ratio=0.5):
    # Open the image
    img = Image.open(image_path)

    # Resize the image
    aspect_ratio = img.height / img.width
    output_height = int(output_width * aspect_ratio)
    img = img.resize((output_width, output_height))

    # Convert the image to grayscale
    img = img.convert('L')

    # Define ASCII characters based on intensity
    ascii_chars = "@%#*+=-:. "

    # Initialize ASCII art
    ascii_art = ""

    # Convert pixels to ASCII characters
    for pixel_value in img.getdata():
        char_index = int(pixel_value / 255 * (len(ascii_chars) - 1))
        ascii_art += ascii_chars[char_index]

    # Break lines to match the output width
    ascii_art = "\n".join([ascii_art[i:i+output_width] for i in range(0, le>

    print(ascii_art)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 asciiconv.py <image_path>")
    else:
        image_path = sys.argv[1]
        image_to_ascii(image_path)
