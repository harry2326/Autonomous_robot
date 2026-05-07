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
    
    # Database path (where map is saved)
    database_path = os.path.expanduser('~/.ros/rtabmap.db')
    
    # RTAB-Map SLAM Node
    rtabmap_slam = Node(
        package='rtabmap_slam',
        executable='rtabmap',
        output='screen',
        parameters=[{
            # Database
            'database_path': database_path,
            'Db/SqliteCache': 'true',  # Use cache for better performance
            
            # Frames
            'frame_id': 'base_footprint_link',
            'odom_frame_id': 'odom',
            'map_frame_id': 'map',
            'publish_tf': True,  # Publish map→odom transform
            
            # Subscription
            'subscribe_depth': False,
            'subscribe_rgbd': True,  # Use synchronized RGBD
            'subscribe_scan': False,  # Set true if you have laser
            'rgbd_cameras': 1,
            
            # Queue and sync
            'queue_size':30,
            'qos': 1,
            'approx_sync': True,
            
            # SLAM parameters
            'RGBD/NeighborLinkRefining': 'true',
            'RGBD/ProximityBySpace': 'true',
            'RGBD/AngularUpdate': '0.01',  # Update if robot rotates >0.01 rad
            'RGBD/LinearUpdate': '0.01',   # Update if robot moves >1cm
            'RGBD/OptimizeFromGraphEnd': 'false',
            
            # Memory management
            'Mem/RehearsalSimilarity': '0.30',
            'Mem/STMSize': '30',
            'Mem/IncrementalMemory': 'true',
            'Mem/saveDepth16Format': 'true',
            
            # Loop closure
            'Mem/UseOdomGravity': 'false',
            'Rtabmap/DetectionRate': '1.0',  # Check for loop closure every 1 Hz
            
            # Visualization
            'RGBD/CreateOccupancyGrid': 'true',  # Create 2D grid for Nav2
            'Grid/FromDepth': 'true',
            'Grid/CellSize': '0.05',  # 5cm resolution
            'Grid/RangeMax': '5.0',   # Max depth for grid
            'Grid/ClusterRadius': '0.1',
            
            # Optimization
            'Optimizer/Strategy': '1',  # 0=TORO, 1=g2o, 2=GTSAM
            'Optimizer/Iterations': '100',
            
            # Use simulation time
            'use_sim_time': use_sim_time
        }],
        remappings=[
            ('rgbd_image', '/rgbd_image'),
            ('odom', '/odometry/filtered'),  # Use fused odometry from EKF
            ('grid_map', '/map')  # Publish 2D occupancy grid
        ],
        arguments=['--delete_db_on_start']  # Delete old map on startup (optional)
    )
    
    return LaunchDescription([
        use_sim_time_arg,
        rtabmap_slam
    ])