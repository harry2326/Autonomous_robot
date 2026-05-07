import os
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    
    # 1. RGBD Sync Node
    rgbd_sync = Node(
        package='rtabmap_sync',
        executable='rgbd_sync',
        output='screen',
        parameters=[{
            'approx_sync': True,
            'approx_sync_max_interval': 0.01,
            'queue_size': 10,
            'depth_scale': 1.0,  # Adjust if depth is not in meters
            'use_sim_time': True
        }],
        remappings=[
            ('rgb/image', '/rgbd_camera/image'),
            ('depth/image', '/rgbd_camera/depth_image'),
            ('rgb/camera_info', '/rgbd_camera/camera_info'),
            ('rgbd_image', '/rgbd_image')  # Output synchronized image
        ]
    )
    
    # 2. RTAB-Map Visual Odometry Node
    # rtabmap_vo = Node(
    #     package='rtabmap_odom',
    #     executable='rgbd_odometry',
    #     output='screen',
    #     arguments=['--ros-args', '--log-level', 'warn'],
    #     parameters=[{
    #         'frame_id': 'base_footprint_link',
    #         'odom_frame_id': 'odom',
    #         'publish_tf': False,
    #         # 'Odom/AlignWithGround': 'true',       # Forces VO to stay at Z=0
    #         # 'guess_frame_id': 'odom',             # Uses your EKF/Wheel odom to "guess" height
    #         # 'Odom/ResetCountdown': '1',
            
    #         # Subscribe to pre-synchronized rgbd_image
            
        
    #     # THE FIX: Wait for TF to find the height offset
    #         'wait_for_transform': 0.5,
    #         'subscribe_rgbd': True,
    #         'rgbd_cameras': 1,
    #         'queue_size': 10,
            
    #         # Visual odometry parameters
    #         'Odom/Strategy': '0',
    #         'Odom/ResetCountdown': '1',
    #         'Vis/MinInliers': '8',
    #         'Vis/InlierDistance': '0.1',
    #         'OdomF2M/MaxSize': '1000',
    #         'Vis/FeatureType': '8',
    #         'Vis/MaxFeatures': '500',
            
    #         'use_sim_time': True
    #     }],
    #     remappings=[
    #         ('rgbd_image0', '/rgbd_image'),
    #         ('odom', '/vo/odometry')
    #     ]
    # )
    
    return LaunchDescription([
        rgbd_sync,
        # rtabmap_vo
    ])