# Wrist System Camera camera streaming

This repository contains two different approaches to stream a RealSense camera in real-time in ROS 2, specifically optimized for Vision-Language-Action (Wrist System Camera) research. 

You can test both and see which one performs best on your Raspberry Pi 4.

## 1. Option 1: `wrist_system_camera_custom` (Custom Python Node)

This package uses a raw Python script (`pyrealsense2` and `cv_bridge`) to fetch the frames from the camera and publish them to a ROS 2 topic.

**Pros:** 
- Extremely easy to modify.
- You can resize, crop, or process the image with OpenCV inside the Python code *before* it's published to ROS, saving bandwidth.
- You can even integrate the Wrist System Camera inference model directly in this node later.

**How to run it:**
1. Install dependencies:
   ```bash
   pip3 install pyrealsense2 opencv-python
   ```
2. Build the package:
   ```bash
   cd ~/ros2_ws
   colcon build --packages-select wrist_system_camera_custom
   source install/setup.bash
   ```
3. Run the node:
   ```bash
   ros2 run wrist_system_camera_custom camera_node
   ```
This will publish the image to `/camera/color/image_raw`.

