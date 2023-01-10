# -*- coding: utf-8 -*-
"""Lane_Indian_Road_1.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1JBue57OwdjcfNmU5-aMGk62y55QXM197
"""

from google.colab import drive
drive.mount('/content/drive')

# Commented out IPython magic to ensure Python compatibility.
import matplotlib.pyplot as plt
import numpy as np
import cv2
# %matplotlib inline

# Reading the image.
img = cv2.imread('/content/drive/MyDrive/My_Data_Set/indian_lane_1.jpg')
img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
plt.figure(figsize = (15, 10))
plt.imshow(img);

# Convert to grayscale.
gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

gray.shape

# Use global threshold based on grayscale intensity.
threshold = cv2.inRange(gray, 180, 255)

img.shape

# Display images.
plt.figure(figsize = (20, 10))
plt.subplot(1,2,1); plt.imshow(gray, cmap = 'gray');      plt.title('Grayscale');
plt.subplot(1,2,2); plt.imshow(threshold, cmap = 'gray'); plt.title('Threshold');

threshold.shape

#  Region masking: Select vertices according to the input image.
roi_vertices = np.array([[[100, 339],
                          [601, 339],
                          [400, 180],
                          [260, 180]]])

# Defining a blank mask.
mask = np.zeros_like(threshold)    # create a black img with similar size of i/p img

type(mask)

mask.shape

plt.figure(figsize = (10, 10))
plt.imshow(mask, cmap='gray', vmin=0, vmax=255)

# Defining a 3 channel or 1 channel color to fill the mask.
if len(threshold.shape) > 2:
    channel_count = threshold.shape[2]  # 3 or 4 depending on the image.
    ignore_mask_color = (255,) * channel_count
else:
    ignore_mask_color = 255

# Filling pixels inside the polygon.
cv2.fillPoly(mask, roi_vertices, ignore_mask_color)

# Constructing the region of interest based on where mask pixels are nonzero.
roi = cv2.bitwise_and(threshold, mask)

# Display images.
plt.figure(figsize = (20, 10))
plt.subplot(1,3,1); plt.imshow(threshold, cmap = 'gray'); plt.title('Initial threshold')
plt.subplot(1,3,2); plt.imshow(mask, cmap = 'gray');      plt.title('Polyfill mask')
plt.subplot(1,3,3); plt.imshow(roi, cmap = 'gray');       plt.title('Isolated roi');

low_threshold = 40
high_threshold = 100
edges = cv2.Canny(roi, low_threshold, high_threshold)

kernel_size = 3
canny_blur = cv2.GaussianBlur(edges, (kernel_size, kernel_size), 0)

plt.figure(figsize = (20, 10))
plt.subplot(1,2,1); plt.imshow(edges, cmap = 'gray'); plt.title('Edge detection')
plt.subplot(1,2,2); plt.imshow(canny_blur, cmap = 'gray'); plt.title('Blurred edges');

def draw_lines(img, lines, color = [255, 0, 0], thickness = 2):
    """Utility for drawing lines."""
    if lines is not None:
        for line in lines:
            for x1,y1,x2,y2 in line:
                cv2.line(img, (x1, y1), (x2, y2), color, thickness)

# for line in lines:
#   print(line)
#   for x1,y1,x2,y2 in line:
#     # print(x1)

# Hough transform parameters set according to the input image.
rho = 1
theta = np.pi / 180
threshold = 50
min_line_len = 10
max_line_gap = 20

lines = cv2.HoughLinesP(canny_blur, rho, theta, threshold, minLineLength = min_line_len, maxLineGap = max_line_gap)

# lines

# Draw all lines found onto a new image.
hough = np.zeros((img.shape[0], img.shape[1], 3), dtype = np.uint8)

draw_lines(hough, lines)

# print("Found {} lines, including: {}".format(len(lines), lines[0]))
plt.figure(figsize = (15, 10));
plt.imshow(hough);

"""# 5. Separate Sides and Extrapolate

### <font style='color:rgb(50,120,230)'> 5.1 Function for separating left and right lines depending on the slope </font>

We need to look at all the lines and determine if they are contributing to the left or right lane lines. As y coordinates increase in value from top to bottom, a line with a positive slope is part of the right lane, and a negative slope means the left lane. Therefore, if `y1 > y2` we have left lane, and if `y1 < y2` we have right lane.
"""

def separate_left_right_lines(lines):
    """Separate left and right lines depending on the slope."""
    left_lines = []
    right_lines = []
    if lines is not None:
        for line in lines:
            for x1, y1, x2, y2 in line:
                if y1 > y2: # Negative slope = left lane.
                    left_lines.append([x1, y1, x2, y2])
                elif y1 < y2: # Positive slope = right lane.
                    right_lines.append([x1, y1, x2, y2])
    return left_lines, right_lines

"""### <font style='color:rgb(50,120,230)'> 5.2 Function to calculate average which will be used in extrapolating lines </font>"""

def cal_avg(values):
    """Calculate average value."""
    if not (type(values) == 'NoneType'):
        if len(values) > 0:
            n = len(values)
        else:
            n = 1
        return sum(values) / n

"""### <font style='color:rgb(50,120,230)'> 5.3 Function to extrapolate lines </font>

As some lane lines are only partially recognized. We should extrapolate the line to cover full lane line length.
We must keep in mind the lower and upper border intersections to find the full lane line length.
"""

def extrapolate_lines(lines, upper_border, lower_border):
    """Extrapolate lines keeping in mind the lower and upper border intersections."""
    slopes = []
    consts = []
    
    if lines is not None:
        for x1, y1, x2, y2 in lines:
            slope = (y1-y2) / (x1-x2)
            slopes.append(slope)
            c = y1 - slope * x1
            consts.append(c)
    avg_slope = cal_avg(slopes)
    avg_consts = cal_avg(consts)
    
    # Calculate average intersection at lower_border.
    x_lane_lower_point = int((lower_border - avg_consts) / avg_slope)
    
    # Calculate average intersection at upper_border.
    x_lane_upper_point = int((upper_border - avg_consts) / avg_slope)
    
    return [x_lane_lower_point, lower_border, x_lane_upper_point, upper_border]

""" ### <font style='color:rgb(50,120,230)'> 5.4 Extract extrapolated lanes and draw lane lines </font>"""

# Define bounds of the region of interest.
roi_upper_border = 190
roi_lower_border = 339

# Create a blank array to contain the (colorized) results.
lanes_img = np.zeros((img.shape[0], img.shape[1], 3), dtype = np.uint8)

# Use above defined function to identify lists of left-sided and right-sided lines.
lines_left, lines_right = separate_left_right_lines(lines)

# Use above defined function to extrapolate the lists of lines into recognized lanes.
lane_left = extrapolate_lines(lines_left, roi_upper_border, roi_lower_border)
lane_right = extrapolate_lines(lines_right, roi_upper_border, roi_lower_border)
draw_lines(lanes_img, [[lane_left]], thickness = 10)
draw_lines(lanes_img, [[lane_right]], thickness = 10)

# Display results.
fig = plt.figure(figsize = (20, 20))
ax = fig.add_subplot(1, 2, 1); plt.imshow(hough); ax.set_title('Before extrapolation')
ax = fig.add_subplot(1, 2, 2); plt.imshow(lanes_img); ax.set_title('After extrapolation');
plt.show()

alpha = 0.8
beta = 1.0
gamma = 0.0
image_annotated = cv2.addWeighted(img, alpha, lanes_img, beta, gamma)

# Display the results, and save image to file.
fig = plt.figure(figsize = (20, 20))
plt.imshow(image_annotated)

image_annotated = cv2.cvtColor(image_annotated, cv2.COLOR_BGR2RGB)
cv2.imwrite('./Lane1ee-image.jpg', image_annotated);