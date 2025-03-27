
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
            #timestamp = datetime.now().strftime('%H:%M:%S.%f')
            file.write(f'{round(dist,3)}')
            dist = f"{dist}"
            cv2.putText(rgbFrame, dist, (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 
                                0.7, (0, 255, 0), 2)


# Camera resolution
width = 1280
height = 720

# HSV color range for orange ball
lowerLimit = np.array([5, 100, 20])
upperLimit = np.array([25, 255, 255])

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

# Function to draw coordinate system origin
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

# Start the device
with dai.Device(pipeline) as device:
    # Get output queues
    qRgb = device.getOutputQueue(name="rgb", maxSize=4, blocking=False)
    qDepth = device.getOutputQueue(name="depth", maxSize=4, blocking=False)
    
    # Processing loop
    while True:
        # Get frames
        inRgb = qRgb.get()
        inDepth = qDepth.get()
        
        # Convert to OpenCV format
        rgbFrame = inRgb.getCvFrame()
        depthFrame = inDepth.getFrame()
        
        # Draw the coordinate system origin
        draw_origin(rgbFrame, cx, cy)
        
        # Color detection
        hsvFrame = cv2.cvtColor(rgbFrame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsvFrame, lowerLimit, upperLimit)
        
        # Clean up mask
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        
        # Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Process contours to find the ball
        if contours:
            # Find the largest contour (should be the ball)
            c = max(contours, key=cv2.contourArea)
            
            # Only proceed if contour is large enough to be a ball
            if cv2.contourArea(c) > 100:
                # Get the bounding circle
                ((x, y), radius) = cv2.minEnclosingCircle(c)
                x, y, radius = int(x), int(y), int(radius)
                
                # Draw circle around the ball
                cv2.circle(rgbFrame, (x, y), radius, (0, 255, 0), 2)
                cv2.circle(rgbFrame, (x, y), 2, (0, 0, 255), -1)
                
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
                    cv2.putText(rgbFrame, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                                0.7, (0, 255, 0), 2)
                    
                    # Draw a line from origin to ball position
                    cv2.line(rgbFrame, (int(cx), int(cy)), (x, y), (255, 165, 0), 2)
                else:
                    # Try a wider scan for valid depth data
                    valid_depth = None
                    for scan_radius in [10, 20, 30]:
                        for dy in range(-scan_radius, scan_radius+1, 5):
                            for dx in range(-scan_radius, scan_radius+1, 5):
                                scan_x = depthX + dx
                                scan_y = depthY + dy
                                
                                if (0 <= scan_x < depthFrame.shape[1] and 
                                    0 <= scan_y < depthFrame.shape[0]):
                                    scan_depth = depthFrame[scan_y, scan_x]
                                    if scan_depth > 0:
                                        # Found valid depth
                                        valid_depth = scan_depth
                                        Z = valid_depth / 10.0  # Convert to centimeters
                                        X = (x - cx) * Z / fx
                                        Y = (y - cy) * Z / fy
                                        
                                        text = f"Position: X={X:.1f}cm, Y={Y:.1f}cm, Z={Z:.1f}cm"
                                        write_distance_to_file(abs(X), abs(Y))
                                        time.sleep(0.085)
                                        cv2.putText(rgbFrame, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                                                    0.7, (255, 165, 0), 2)  # Orange text for backup method
                                        
                                        # Draw a line from origin to ball position
                                        cv2.line(rgbFrame, (int(cx), int(cy)), (x, y), (255, 165, 0), 2)
                                        break
                            if valid_depth is not None:
                                break
                        if valid_depth is not None:
                            break
                    
                    if valid_depth is None:
                        cv2.putText(rgbFrame, "No depth data", (10, 30), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        # Show only the RGB frame with ball detection
        cv2.imshow("Ball Tracker", rgbFrame)
        
        # Exit on 'q' key
        if cv2.waitKey(1) == 27:
            break

cv2.destroyAllWindows()
