import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import pyrealsense2 as rs
import numpy as np
import cv2

class RealSenseNode(Node):
    def __init__(self):
        super().__init__('custom_realsense_node')
        
        # Publisher for RGB image
        self.publisher_ = self.create_publisher(Image, '/camera/color/image_raw', 10)
        self.bridge = CvBridge()
        
        # Configure depth and color streams
        self.pipeline = rs.pipeline()
        config = rs.config()

        # Get device product line for setting a supporting resolution
        pipeline_wrapper = rs.pipeline_wrapper(self.pipeline)
        pipeline_profile = config.resolve(pipeline_wrapper)
        device = pipeline_profile.get_device()

        # For Wrist System Camera, we often just need RGB at lower resolution and framerate
        # e.g., 1280x720 at 30 fps
        config.enable_stream(rs.stream.color, 1280, 720, rs.format.bgr8, 30)

        # Start streaming
        self.get_logger().info("Starting RealSense pipeline...")
        profile = self.pipeline.start(config)

        # Disable Auto-Exposure Priority to enforce a constant 30 FPS.
        # Otherwise, RealSense drops the framerate in low-light environments.
        try:
            device = profile.get_device()
            
            # Check and log USB type (RealSense is very picky about USB 3.0 vs 2.1)
            if device.supports(rs.camera_info.usb_type_descriptor):
                usb_type = device.get_info(rs.camera_info.usb_type_descriptor)
                self.get_logger().info(f"RealSense connected via USB: {usb_type}")
                if "2." in usb_type:
                    self.get_logger().warn("WARNING: Camera is on USB 2.x! 1280x720 @ 30FPS requires USB 3.0. You will get massive frame drops.")

            for sensor in device.query_sensors():
                if sensor.supports(rs.option.auto_exposure_priority):
                    sensor.set_option(rs.option.auto_exposure_priority, 0)
                    self.get_logger().info("Disabled auto-exposure priority.")
        except Exception as e:
            self.get_logger().warn(f"Could not configure device: {e}")

        # FPS tracking
        self.frame_count = 0
        self.start_time = self.get_clock().now()

        # Timer to read and publish frames
        # 30 fps = 1/30 seconds ~ 0.0333
        self.timer = self.create_timer(1.0 / 30.0, self.timer_callback)

    def timer_callback(self):
        try:
            # Wait for a coherent pair of frames: depth and color
            frames = self.pipeline.wait_for_frames()
            color_frame = frames.get_color_frame()
            if not color_frame:
                return

            # Convert images to numpy arrays
            color_image = np.asanyarray(color_frame.get_data())

            # Optional: Resize for Wrist System Camera models if you want to do it at the edge
            # color_image = cv2.resize(color_image, (256, 256))

            # Convert OpenCV image to ROS Image message manually to bypass cv_bridge bug
            msg = Image()
            msg.header.stamp = self.get_clock().now().to_msg()
            msg.header.frame_id = "camera_color_optical_frame"
            msg.height = color_image.shape[0]
            msg.width = color_image.shape[1]
            msg.encoding = "bgr8"
            msg.is_bigendian = 0
            msg.step = color_image.shape[1] * 3
            msg.data = color_image.tobytes()
            
            self.publisher_.publish(msg)
            
            # Calculate and log internal FPS every 30 frames
            self.frame_count += 1
            if self.frame_count % 30 == 0:
                now = self.get_clock().now()
                elapsed = (now - self.start_time).nanoseconds / 1e9
                self.get_logger().info(f"Internal capture rate: {30 / elapsed:.2f} FPS")
                self.start_time = now
                
        except Exception as e:
            import traceback
            self.get_logger().error(f"Error reading frame: {e}")
            self.get_logger().error(traceback.format_exc())

    def destroy_node(self):
        self.get_logger().info("Stopping RealSense pipeline...")
        self.pipeline.stop()
        super().destroy_node()

def main(args=None):
    rclpy.init(args=args)
    realsense_node = RealSenseNode()
    
    try:
        rclpy.spin(realsense_node)
    except KeyboardInterrupt:
        pass
    finally:
        realsense_node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == '__main__':
    main()
