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
            'Db/SqliteCache': 'true',
            
            # --- 1. FRAMES & TF ---
            'frame_id': 'base_footprint_link',
            'odom_frame_id': 'odom',
            'map_frame_id': 'map',
            'publish_tf': True,  # RTAB-Map handles map -> odom
            'wait_for_transform': 0.5,
            
            # --- 2. SUBSCRIPTIONS ---
            'subscribe_depth': False,
            'subscribe_rgbd': True,
            'subscribe_scan': False,
            'approx_sync': True,
            'queue_size': 30,  # Increased for sim stability
            
            # --- 3. THE "Z-AXIS LOCK" (Stops the Diving Arrow) ---
            'Reg/Force3DoF': 'true',        # Forces robot to stay at Z=0
            'Optimizer/Slam2D': 'true',     # Tells optimizer this is a 2D floor
            'Grid/FromDepth': 'true',
            
            # --- 4. ANTI-DISTORTION (Repetitive Rack Fix) ---
            'RGBD/ProximityBySpace': 'false', # Don't try to close loops just by proximity
            'RGBD/OptimizeMaxError': '0.5',    # Reject loop closures that shift map >1m
            'Vis/MinInliers': '20',           # Require high quality matches only
            'RGBD/NeighborLinkRefining': 'true',
            
            # --- 5. MOTION UPDATE THRESHOLDS ---
            # Set these slightly higher to avoid "jitter" in the map
            'RGBD/AngularUpdate': '0.1',  # 0.1 rad (~5.7 deg)
            'RGBD/LinearUpdate': '0.1',   # 10cm
            
            # --- 6. OPTIMIZATION ---
            'Optimizer/Strategy': '2',  # g2o
            'Optimizer/Iterations': '20', # Reduced for faster real-time performance
            
            'use_sim_time': use_sim_time
        }],
        remappings=[
            ('rgbd_image', '/rgbd_image'),
            ('odom', '/odometry/filtered'), # Listening to your smooth EKF output
            ('grid_map', '/map')
        ],
        # Forces a clean slate every time you launch
        arguments=['--delete_db_on_start'] 
    )
    
    return LaunchDescription([
        use_sim_time_arg,
        rtabmap_slam
    ])