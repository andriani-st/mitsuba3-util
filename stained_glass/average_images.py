import cv2
import numpy as np

# List of file paths to the resulting images
image_paths = ['result.png', 'result1.png', 'result2.png', 'result3.png', 'result4.png', 'result5.png']  # Add paths to your result images

# Initialize an empty list to store image arrays
images = []

# Load each image and convert it to a numpy array
for path in image_paths:
    img = cv2.imread(path)
    images.append(img)

# Convert the list of image arrays to a numpy array
images = np.array(images)

# Calculate the average of the image arrays along the first axis (averaging across images)
average_image = np.mean(images, axis=0)

# Convert the resulting average image array back to uint8 format
average_image = average_image.astype(np.uint8)

# Save or display the resulting average image
cv2.imwrite('average_result.png', average_image)  # Save the average image
cv2.imshow('Average Result', average_image)  # Display the average image
cv2.waitKey(0)  # Wait for a key press to close the window
cv2.destroyAllWindows()  # Close all OpenCV windows
