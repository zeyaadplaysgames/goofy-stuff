import sys
import os
import shutil
from PIL import Image

# Function to get terminal size
def get_terminal_size():
    size = shutil.get_terminal_size((80, 20))
    return size.columns, size.lines

# Function to convert image to ASCII art
def image_to_ascii(image_path, char_ratio=0.55):
    # Get terminal size
    term_width, term_height = get_terminal_size()

    # Calculate output width and height based on terminal size
    output_width = term_width - 10  # Adjust for margin
    output_height = int((term_height - 5) / char_ratio)

    # Open the image and convert it to RGB
    img = Image.open(image_path).convert('RGB')

    # Resize the image while maintaining the aspect ratio
    aspect_ratio = img.height / img.width
    if int(output_width * aspect_ratio) > output_height:
        new_height = output_height
        new_width = int(new_height / aspect_ratio)
    else:
        new_width = output_width
        new_height = int(new_width * aspect_ratio)

    img = img.resize((new_width, new_height))

    # Define ASCII characters based on intensity
    ascii_chars = "@%#*+=-:. "

    # Initialize ASCII art
    ascii_art = []

    # Convert pixels to ASCII characters
    pixels = list(img.getdata())
    for y in range(new_height):
        line = ""
        for x in range(new_width):
            r, g, b = pixels[y * new_width + x]
            pixel_value = int(0.3 * r + 0.59 * g + 0.11 * b)
            char_index = int(pixel_value / 255 * (len(ascii_chars) - 1))
            ascii_char = ascii_chars[char_index]
            line += f"\033[38;2;{r};{g};{b}m{ascii_char}\033[0m"
        ascii_art.append(line)

    # Print the ASCII art
    print("\n".join(ascii_art))

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 asciiconv.py [image_path]")
    else:
        image_path = sys.argv[1]
        image_to_ascii(image_path)
