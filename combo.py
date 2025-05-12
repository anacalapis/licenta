import depthai as dai
import cv2
import numpy as np
import math
import threading 
import time
from datetime import datetime

lock = threading.Lock()

def write_distance_to_file(X, Y):
    with lock:
        with open("distanta.txt", "w") as file:
            dist = math.sqrt((round(X, 2) - 50)**2 + (round(Y, 2))**2) #coord inel (50,0)
            file.write(f'{round(dist,3)}')
            dist = f"{dist}"
            cv2.putText(rgbFrame, dist, (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 
                                0.7, (0, 255, 0), 2)

# Global variables for ROI selection
drawing = False
ix, iy = -1, -1
rx, ry, rw, rh = 0, 0, 0, 0
roi_selected = False
lowerLimit = None
upperLimit = None

def draw_rectangle(event, x, y, flags, param):
    global ix, iy, drawing, roi_selected, rx, ry, rw, rh, lowerLimit, upperLimit
    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        ix, iy = x, y
    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing:
            rx, ry = min(ix, x), min(iy, y)
            rw, rh = abs(ix - x), abs(iy - y)
    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        roi_selected = True
        # Compute color range for selected ROI
        roi = hsvFrame[ry:ry+rh, rx:rx+rw]
        
        # Compute average and standard deviation of HSV values in ROI
        h, s, v = cv2.split(roi)
        
        # Compute lower and upper limits with some tolerance
        lowerLimit = np.array([
            max(0, np.mean(h) - 10),   # Hue with some tolerance
            max(0, np.mean(s) - 30),    # Saturation tolerance
            max(0, np.mean(v) - 30)     # Value tolerance
        ]).astype(np.uint8)
        
        upperLimit = np.array([
            min(180, np.mean(h) + 10),  # Hue with some tolerance
            min(255, np.mean(s) + 30),  # Saturation tolerance
            min(255, np.mean(v) + 30)   # Value tolerance
        ]).astype(np.uint8)
        
        print(f"Selected Color Range - Lower: {lowerLimit}, Upper: {upperLimit}")

def draw_origin(img, origin_x, origin_y):
    # Draw crosshair at the origin
    cv2.drawMarker(img, (int(origin_x), int(origin_y)), (255, 255, 255), 
                  cv2.MARKER_CROSS, 20, 2)
    
    # Draw X axis (red)
    cv2.line(img, (int(origin_x), int(origin_y)), (int(origin_x + 50), int(origin_y)), (0, 0, 255), 2)
    cv2.putText(img, "X", (int(origin_x + 55), int(origin_y + 5)), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    
    # Draw Y axis (green)
    cv2.line(img, (int(origin_x), int(origin_y)), (int(origin_x), int(origin_y - 50)), (0, 255, 0), 2)
    cv2.putText(img, "Y", (int(origin_x - 15), int(origin_y - 55)), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    
    # Draw Z axis (blue) - coming out of the screen, shown as a circle that gets smaller
    cv2.circle(img, (int(origin_x), int(origin_y)), 5, (255, 0, 0), -1)
    cv2.putText(img, "Z", (int(origin_x + 15), int(origin_y + 25)), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
    
    # Label the origin
    cv2.putText(img, "(0,0,0)", (int(origin_x + 20), int(origin_y - 20)), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

# Camera resolution
width = 1280
height = 720

# Camera intrinsic parameters
fx = 800  # focal length in pixels
fy = 800
cx = width / 2  # principal point
cy = height / 2

# Create pipeline
pipeline = dai.Pipeline()

# RGB Camera setup
camRgb = pipeline.createColorCamera()
camRgb.setPreviewSize(width, height)
camRgb.setInterleaved(False)
camRgb.setFps(30)

# Stereo depth setup
stereo = pipeline.create(dai.node.StereoDepth)
stereo.setDefaultProfilePreset(dai.node.StereoDepth.PresetMode.DEFAULT)
stereo.setLeftRightCheck(True)
stereo.setExtendedDisparity(False)
stereo.setSubpixel(True)

# Configure mono cameras
monoLeft = pipeline.createMonoCamera()
monoRight = pipeline.createMonoCamera()
monoLeft.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)
monoRight.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)
monoLeft.setBoardSocket(dai.CameraBoardSocket.CAM_B)
monoRight.setBoardSocket(dai.CameraBoardSocket.CAM_C)

# Connect mono cameras to stereo
monoLeft.out.link(stereo.left)
monoRight.out.link(stereo.right)

# Create outputs
xoutRgb = pipeline.createXLinkOut()
xoutRgb.setStreamName("rgb")
camRgb.preview.link(xoutRgb.input)

xoutDepth = pipeline.createXLinkOut()
xoutDepth.setStreamName("depth")
stereo.depth.link(xoutDepth.input)

# Start the device
with dai.Device(pipeline) as device:
    # Get output queues
    qRgb = device.getOutputQueue(name="rgb", maxSize=4, blocking=False)
    qDepth = device.getOutputQueue(name="depth", maxSize=4, blocking=False)
    
    # Create window and set mouse callback
    cv2.namedWindow("Object Selection")
    cv2.setMouseCallback("Object Selection", draw_rectangle)
    
    # Processing loop
    while True:
        # Get frames
        inRgb = qRgb.get()
        inDepth = qDepth.get()
        
        # Convert to OpenCV format
        rgbFrame = inRgb.getCvFrame()
        depthFrame = inDepth.getFrame()
        
        # Convert to HSV for color tracking
        hsvFrame = cv2.cvtColor(rgbFrame, cv2.COLOR_BGR2HSV)
        
        # Draw the coordinate system origin
        draw_origin(rgbFrame, cx, cy)
        
        # Clone frame for drawing
        clone = rgbFrame.copy()
        
        # Draw ROI selection rectangle if in progress
        if not roi_selected and drawing:
            cv2.rectangle(clone, (rx, ry), (rx + rw, ry + rh), (0, 255, 0), 2)
        
        # If color range is set, do object tracking
        if lowerLimit is not None and upperLimit is not None:
            # Create color mask
            mask = cv2.inRange(hsvFrame, lowerLimit, upperLimit)
            
            # Clean up mask
            kernel = np.ones((5, 5), np.uint8)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
            cv2.imshow("mask", mask)
            
            # Find contours
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Process contours to find the object
            if contours:
                # Find the largest contour (should be the object)
                c = max(contours, key=cv2.contourArea)
                
                # Only proceed if contour is large enough
                if cv2.contourArea(c) > 100:
                    # Get the bounding circle
                    ((x, y), radius) = cv2.minEnclosingCircle(c)
                    x, y, radius = int(x), int(y), int(radius)
                    
                    # Draw circle around the object
                    cv2.circle(clone, (x, y), radius, (0, 255, 0), 2)
                    cv2.circle(clone, (x, y), 2, (0, 0, 255), -1)
                    
                    # Calculate corresponding point in depth map
                    depthX = int(x * depthFrame.shape[1] / rgbFrame.shape[1])
                    depthY = int(y * depthFrame.shape[0] / rgbFrame.shape[0])
                    
                    # Ensure coordinates are within bounds
                    depthX = max(0, min(depthX, depthFrame.shape[1] - 1))
                    depthY = max(0, min(depthY, depthFrame.shape[0] - 1))
                    
                    # Check depth around the point (5x5 region)
                    region_size = 5
                    xMin = max(0, depthX - region_size)
                    xMax = min(depthFrame.shape[1] - 1, depthX + region_size)
                    yMin = max(0, depthY - region_size)
                    yMax = min(depthFrame.shape[0] - 1, depthY + region_size)
                    
                    depthRegion = depthFrame[yMin:yMax, xMin:xMax]
                    
                    # Get non-zero depth values
                    nonZeroDepths = depthRegion[depthRegion > 0]
                    
                    if len(nonZeroDepths) > 0:
                        # Get median depth (more robust to outliers)
                        depth = np.median(nonZeroDepths)
                        
                        # Calculate 3D coordinates (in centimeters)
                        Z = depth / 10.0  # Convert to centimeters
                        X = (x - cx) * Z / fx
                        Y = (y - cy) * Z / fy
                        
                        # Display 3D position in centimeters
                        text = f"Position: X={X:.1f}cm, Y={Y:.1f}cm, Z={Z:.1f}cm"
                        write_distance_to_file(abs(X), abs(Y))
                        cv2.putText(clone, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                                    0.7, (0, 255, 0), 2)
                        
                        # Draw a line from origin to object position
                        cv2.line(clone, (int(cx), int(cy)), (x, y), (255, 165, 0), 2)
        
        # Show the frame
        cv2.imshow("Object Selection", clone)
        
        # Exit on 'q' or ESC key
        key = cv2.waitKey(1)
        if key == 27 or key == ord('q'):  # ESC or 'q'
            break
        elif key == ord('r'):  # 'r' to reset ROI selection
            roi_selected = False
            lowerLimit = None
            upperLimit = None
            print("Reset ROI selection. Select new object.")

cv2.destroyAllWindows()