import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    
    # Launch arguments
    use_sim_time = LaunchConfiguration('use_sim_time')
    
    use_sim_time_arg = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation time'
    )
    
    # Database path
    database_path = os.path.expanduser('~/.ros/rtabmap.db')
    
    # RTAB-Map SLAM Node
    rtabmap_slam = Node(
        package='rtabmap_slam',
        executable='rtabmap',
        output='screen',
        parameters=[{
            'database_path': database_path,
            'frame_id': 'base_footprint_link',
            'odom_frame_id': 'odom',
            'map_frame_id': 'map',
            'publish_tf': True,
            'subscribe_rgbd': True,
            'use_sim_time': use_sim_time,
            'queue_size': 30,

            # --- THE "AISLE SYMMETRY" FIXES ---
            
            # 1. Optimizer Settings (GTSAM is better for warehouse constraints)
            'Optimizer/Strategy': '2',          # 2 = GTSAM
            'Optimizer/Robust': 'true',         # Use robust kernel
            'Optimizer/RobustKernelDelta': '0.1', # Small delta = more skeptical of bad links
            'Optimizer/VarianceIgnored': 'false', # Use sensor covariances from EKF
            'RGBD/OptimizeMaxError': '0.5',     # Reject loop closures that jump > 50cm

            # 2. Visual Loop Closure Filtering
            'Vis/MinInliers': '20',             # Require many matches to accept a loop closure
            'RGBD/LoopClosureRecheck': 'true',  # Double check visual links
            'RGBD/ProximityBySpace': 'true',    # Only check for loops near current position
            'RGBD/ProximityPathMaxNeighbors': '10',
            
            # 3. Motion Updates (Don't update the map if moving too slow)
            'RGBD/AngularUpdate': '0.1',        # Update if rotates > 0.1 rad
            'RGBD/LinearUpdate': '0.1',         # Update if moves > 10cm
            
            # Memory Management
            'Mem/IncrementalMemory': 'true',    # Set to false for Localization-only mode
            'Mem/RehearsalSimilarity': '0.45',  # Higher = less likely to merge similar aisles
            
            # Occupancy Grid for Nav2
            'Grid/FromDepth': 'true',
            'Grid/RangeMax': '5.0',
            'Grid/CellSize': '0.05',
            'Reg/Strategy': '0',                # 0=Vis, 1=Icp, 2=VisIcp
        }],
        remappings=[
            ('rgbd_image', '/rgbd_image'),
            ('odom', '/odometry/filtered'),     # Subscribing to your EKF output
            ('grid_map', '/map')
        ],
        arguments=['--delete_db_on_start'] 
    )
    
    return LaunchDescription([
        use_sim_time_arg,
        rtabmap_slam
    ])