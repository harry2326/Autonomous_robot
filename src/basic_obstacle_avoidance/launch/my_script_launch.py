import os
from click import launch
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
import xacro

def generate_launch_description():
    # 1. Paths and Xacro processing
    pkg_path = get_package_share_directory('basic_obstacle_avoidance')
    
    # Path to your custom world file
    world_file_path = os.path.join(pkg_path, 'worlds', 'world2.sdf')
    
    ekf_file_path = os.path.join(pkg_path, 'config', 'ekf.yaml')
    # Path to RViz config
    rviz_config_file = os.path.join(pkg_path, 'rviz', 'T2D2_.rviz')
    
    xacro_file = os.path.join(pkg_path, 'URDF', 'T2D2.xacro')
    robot_description_config = xacro.process_file(xacro_file)
    robot_desc = robot_description_config.toxml()
    
    # 2. Include the Gazebo launch file with your custom world
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(
            get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py')]),
        launch_arguments={'gz_args': f'-r {world_file_path}'}.items(),
    )
    
    # 3. Robot State Publisher
    rsp = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': robot_desc, 'use_sim_time': True}]
    )
    
    # 4. Spawn the robot in Gazebo
    spawn = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=['-topic', 'robot_description',
                   '-name', 'T2D2',
                   '-z', '0.5'],
        output='screen',
    )
    
    # 5. RViz2 with config file
    rviz2 = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', rviz_config_file],
        parameters=[{'use_sim_time': True}]  
    )
    
    # 6. Bridge RGB Image
    bridge_camera_image = Node(
        package='ros_gz_image',
        executable='image_bridge',
        arguments=['/rgbd_camera/image'],
        output='screen'
    )
    
    # 7. Bridge Depth Image
    bridge_depth_image = Node(
        package='ros_gz_image',
        executable='image_bridge',
        arguments=['/rgbd_camera/depth_image'],
        output='screen'
    )
    
    # 8. Bridge Camera Info
    bridge_camera_info = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/rgbd_camera/camera_info@sensor_msgs/msg/CameraInfo@gz.msgs.CameraInfo'
        ],
        output='screen'
    )
    
    # 9. Bridge Point Cloud
    bridge_points = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/rgbd_camera/points@sensor_msgs/msg/PointCloud2@gz.msgs.PointCloudPacked'
        ],
        output='screen'
    )
    
    # 10. Bridge cmd_vel for robot control
    bridge_cmd_vel = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist'
        ],
        output='screen'
    )

    # 11. Bridge IMU sensor from Gazebo to ROS
    bridge_imu = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/imu@sensor_msgs/msg/Imu@gz.msgs.IMU'
        ],
        parameters=[{'lazy': True}],
        output='screen'
    )
    rtabmap_vo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(pkg_path, 'launch', 'rtabmap_vo_sync.launch.py')
        ])
    )

    # 12. Updated Bridge for TF
    bridge_tf = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            # '/model/T2D2/tf@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V',
            # '/model/T2D2/tf_static@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V',
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
            # Use the [ to ensure the bridge handles the Model -> JointState conversion correctly
            '/model/T2D2/joint_state@sensor_msgs/msg/JointState[gz.msgs.Model',
            '/model/T2D2/odometry@nav_msgs/msg/Odometry@gz.msgs.Odometry',
        ],
        remappings=[
            # ('/model/T2D2/tf', '/tf'),
            # ('/model/T2D2/tf_static', '/tf_static'),
            ('/model/T2D2/joint_state', '/joint_states'),
            ('/model/T2D2/odometry', '/odom'), # Standardized naming
        ],
        output='screen'
    )

    # Robot localization node to fuse odometry and IMU data for better state estimation.
    robot_localization_node = Node(
    package='robot_localization',
    executable='ekf_node',
    name='ekf_filter_node',
    output='screen',
    parameters=[ekf_file_path, {'use_sim_time': True}]
    )
    

    
    #launching depth processing
    # depth_process = Node(
    #     package='depth_processor_pkg',
    #     executable='depth_processor_node',
    #     name='depth_processor_node',
    #     output='screen',
    #     parameters=[{'use_sim_time': True}]
    # )

    # # Obstacle avoidance motion node
    # obstacle_avoidance_motion = Node(
    #     package='depth_processor_pkg',
    #     executable='obstacle_avoidance_motion',
    #     name='obstacle_avoidance_motion',
    #     output='screen',
    #     parameters=[{'use_sim_time': True}]
    # )
    
        
    return LaunchDescription([
        gazebo,
        rsp,
        spawn,
        bridge_camera_image,
        bridge_depth_image,
        bridge_camera_info,
        bridge_points,
        bridge_cmd_vel,
        bridge_tf,
        bridge_imu,
        rtabmap_vo_launch,
        robot_localization_node,
        rviz2,
        # depth_process,
        # obstacle_avoidance_motion,
    ])