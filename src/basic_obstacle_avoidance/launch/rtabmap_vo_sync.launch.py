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
   # ... (rgbd_sync remains the same)

    # 2. RTAB-Map Visual Odometry Node
    # rtabmap_vo = Node(
    #     package='rtabmap_odom',
    #     executable='rgbd_odometry',
    #     output='screen',
    #     parameters=[{
    #         'frame_id': 'base_footprint_link',
    #         'odom_frame_id': 'odom',
    #         'publish_tf': False, # Keep False because EKF will publish TF
    #         'wait_for_transform': 0.5,
    #         'subscribe_rgbd': True,
    #         'use_sim_time': True,
            
    #         # --- CORRIDOR STABILIZATION PARAMETERS ---
    #         'Odom/Strategy': '0',         # Frame-to-Map (more stable in repetitive environments)
    #         'Vis/MinInliers': '15',       # Increase from 8 (requires more matching points)
    #         'Vis/InlierDistance': '0.05',  # Tighter matching (lower = stricter)
    #         'Odom/FilteringStrategy': '1', # Particle Filter or Kalman filter for VO output
    #         'Odom/MaxInliers': '20',      # Max features used for odometry
            
    #         # REJECT JUMPS: If the VO suggests a move > 0.5m or 0.5rad between frames, ignore it
    #         'Odom/MaxEstimationDelay': '0.5',
    #         'Odom/GuessMotion': 'true',    # Use previous motion to predict next position
    #         'RGBD/OptimizeMaxError': '0.3', # If error is high (ambiguous aisles), reject it
            
    #         # Feature extraction
    #         'Vis/FeatureType': '8',       # GFTT/ORB (8 is usually GFTT)
    #         'Vis/MaxFeatures': '1000',     # Increase features to find unique details in shelves
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