import os
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    
    # === ICP ODOMETRY NODE ===
    # Uses point cloud + IMU for robust odometry
    icp_odometry = Node(
        package='rtabmap_odom',
        executable='icp_odometry',  # ← Changed from rgbd_odometry
        output='screen',
        parameters=[{
            # --- FRAMES ---
            'frame_id': 'base_footprint_link',
            'odom_frame_id': 'odom',
            'publish_tf': False,  # EKF publishes final TF
            'wait_for_transform': 0.5,
            
            # --- IMU INTEGRATION ---
            # 'wait_imu_to_init': True,  # Wait for IMU before starting
            # 'imu_topic': '/imu',  # Your IMU topic
            
            # --- POINT CLOUD SUBSCRIPTION ---
            'subscribe_scan_cloud': True,  # Use point cloud
            'scan_cloud_max_points': 0,    # 0 = use all points
            
            # --- POINT CLOUD PROCESSING ---
            # Voxel filtering (downsample for performance)
            'scan_voxel_size': 0.05,  # 5cm voxels (adjust based on environment)
            
            # Range filtering (ignore far/close points)
            'scan_range_min': 0.3,    # Ignore points < 30cm (robot body)
            'scan_range_max': 8.0,    # Ignore points > 8m (too far)
            
            # Normal estimation (improves ICP matching)
            'scan_normal_k': 0,           # K-nearest neighbors for normal
            'scan_normal_radius': 0.0,     # 0 = use K instead of radius
            
            # Downsampling (optional, for speed)
            'scan_downsampling_step': 1,   # 1 = no downsampling, 2 = every 2nd point
            
            # --- ICP PARAMETERS ---
            'Odom/Strategy': '0',          # 0=Frame-to-Map (better for corridors)
            'Odom/ResetCountdown': '1',
            
            # ICP registration parameters
            'Icp/MaxTranslation': '0.5',     # Max movement between frames (meters)
            'Icp/MaxRotation': '0.5',        # Max rotation between frames (radians)
            'Icp/VoxelSize': '0.05',         # Match resolution
            'Icp/MaxCorrespondenceDistance': '0.1',  # Max point-to-point distance
            'Icp/Iterations': '30',          # ICP iterations
            'Icp/Epsilon': '0.001',          # Convergence threshold
            'Icp/CorrespondenceRatio': '0.4', # Min % of points that must match
            
            # Outlier filtering (reject bad matches)
            'Icp/OutlierRatio': '0.85',      # Keep top 85% of matches
            'Icp/MaxTranslationError': '0.05', # Reject if translation error > 5cm
            'Icp/MaxRotationError': '0.05',   # Reject if rotation error > 0.05 rad
            
            # --- STABILITY IN REPETITIVE ENVIRONMENTS ---
            'Odom/FilteringStrategy': '2',  # 2=Kalman filter for smoother output
            'Odom/GuessMotion': 'true',     # Use velocity model to predict motion
            
            # --- 2D MODE (for ground robots) ---
            'Reg/Force3DoF': 'true',        # Constrain to 2D (X, Y, Yaw only)
            # --- ADD THESE TO YOUR PARAMETERS LIST ---
            'PCL/FilterNaNs': 'true',         # Specifically removes the NaN points causing the crash
            'Icp/PointToPlane': 'false',      # Set to false if you don't have perfect normals
                        
            # --- SIMULATION TIME ---
            'use_sim_time': True
        }],
        arguments=['--ros-args', '--log-level', 'WARN'],  
        remappings=[
            ('scan_cloud', '/rgbd_camera/points'),  # Your point cloud topic
            # ('imu', '/imu'),                    # Your IMU topic
            ('odom', '/icp/odometry')                # Output odometry
        ]
    )
    
    return LaunchDescription([
        icp_odometry    
    ])