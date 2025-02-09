from PIL import Image, ImageDraw, ImageFont
import os

def create_test_image():
    # Create directory if it doesn't exist
    os.makedirs('images', exist_ok=True)
    
    # Create a new image with a white background
    image = Image.new('RGB', (800, 400), 'white')
    draw = ImageDraw.Draw(image)
    
    # Add some text
    text = "Hello, this is a test image"
    draw.text((50, 150), text, fill='black')
    
    # Add some shapes
    draw.rectangle([300, 100, 500, 300], outline='blue', width=2)
    draw.ellipse([550, 100, 650, 200], outline='red', width=2)
    
    # Save the image
    image.save('images/test_image.jpg')
    print("Created test image at images/test_image.jpg")

if __name__ == "__main__":
    create_test_image()