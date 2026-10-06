# VLA RealSense camera streaming

This repository contains two different approaches to stream a RealSense camera in real-time in ROS 2, specifically optimized for Vision-Language-Action (VLA) research. 

You can test both and see which one performs best on your Raspberry Pi 4.

## 1. Option 1: `vla_realsense_custom` (Custom Python Node)

This package uses a raw Python script (`pyrealsense2` and `cv_bridge`) to fetch the frames from the camera and publish them to a ROS 2 topic.

**Pros:** 
- Extremely easy to modify.
- You can resize, crop, or process the image with OpenCV inside the Python code *before* it's published to ROS, saving bandwidth.
- You can even integrate the VLA inference model directly in this node later.

**How to run it:**
1. Install dependencies:
   ```bash
   pip3 install pyrealsense2 opencv-python
   ```
2. Build the package:
   ```bash
   cd ~/ros2_ws
   colcon build --packages-select vla_realsense_custom
   source install/setup.bash
   ```
3. Run the node:
   ```bash
   ros2 run vla_realsense_custom camera_node
   ```
This will publish the image to `/camera/color/image_raw`.

---

## 2. Option 2: `vla_realsense_official` (Intel's Official Wrapper)

This package is a launcher wrapper around Intel's official C++ node (`realsense2_camera`). It launches the official driver but explicitly configures it for VLA by disabling the depth sensor (to save CPU) and fixing the RGB resolution to 640x480 at 30 fps.

**Pros:**
- Maximum performance since the heavy lifting is done in optimized C++.
- Less CPU usage on the Raspberry Pi 4.
- Zero frame drops.

**How to run it:**
1. Install the official RealSense ROS 2 package:
   ```bash
   sudo apt install ros-humble-realsense2-camera
   ```
2. Build our custom launcher package:
   ```bash
   cd ~/ros2_ws
   colcon build --packages-select vla_realsense_official
   source install/setup.bash
   ```
3. Run the node:
   ```bash
   ros2 launch vla_realsense_official official_camera.launch.py
   ```
This will also publish the image to `/camera/color/image_raw` (among other standard topics).
