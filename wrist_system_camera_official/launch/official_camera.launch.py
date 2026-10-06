import os
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    # We include the official rs_launch.py from realsense2_camera package
    realsense_share_dir = get_package_share_directory('realsense2_camera')
    
    realsense_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(realsense_share_dir, 'launch', 'rs_launch.py')
        ),
        launch_arguments={
            # Disable depth if only RGB is needed for Wrist System Camera, saves compute
            'enable_depth': 'false',
            'enable_infra1': 'false',
            'enable_infra2': 'false',
            
            # Configure RGB camera for Wrist System Camera
            'rgb_camera.profile': '1280x720x30',
            
            # Align depth to color if you eventually enable depth
            'align_depth.enable': 'false',
        }.items()
    )

    return LaunchDescription([
        realsense_launch
    ])
