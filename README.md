# Autonomous Robot Navigation System

A ROS2-based autonomous mobile robot navigation system featuring depth-based obstacle avoidance, SLAM localization, and intelligent path planning algorithms.

## 📋 Table of Contents

- [Project Overview](#project-overview)
- [Key Features](#key-features)
- [System Architecture](#system-architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Project Structure](#project-structure)
- [Quick Start](#quick-start)
- [Modules Description](#modules-description)
- [Configuration](#configuration)
- [Usage Examples](#usage-examples)
- [Troubleshooting](#troubleshooting)
- [Contributors](#contributors)

---

## 🤖 Project Overview

This project implements a complete autonomous navigation system for mobile robots using ROS2. The robot autonomously navigates unknown environments using depth camera inputs, implements intelligent obstacle avoidance strategies, and performs simultaneous localization and mapping (SLAM) to build environmental maps.

**Key Technologies:**
- ROS2 (Robot Operating System 2)
- Gazebo Simulator
- RTABMap (SLAM)
- OpenCV (Computer Vision)
- Extended Kalman Filter (EKF) for sensor fusion

---

## ✨ Key Features

### 🔍 Obstacle Avoidance
- **Depth-based Detection**: Uses RGBD camera to detect obstacles in real-time
- **Intelligent Navigation**: Three-zone detection (left, center, right) for adaptive movement
- **Stuck Detection**: Automatically detects and recovers from stuck situations
- **Multi-Mode Navigation**:
  - Forward movement when path is clear
  - Corridor centering for narrow passages
  - Blocked path recovery
  - Smart turning with hysteresis

### 🗺️ SLAM & Localization
- **Visual SLAM**: Using RTABMap for loop closure detection
- **ICP Matching**: Iterative Closest Point for precise localization
- **Visual Odometry**: VO-Sync for drift correction
- **EKF Integration**: Robot Localization package for sensor fusion

### 🎮 Simulation Environment
- **Gazebo Integration**: Complete simulation environment with physics
- **URDF Models**: T2D2 robot with detailed geometry (xacro files)
- **Multiple Worlds**: Different test environments for validation
- **RViz Visualization**: Real-time visualization of robot state

---

## 🏗️ System Architecture

```
Autonomous Robot Navigation System
│
├── Perception Layer
│   ├── Depth Processor Node (depth_processor_pkg)
│   │   └── Processes RGBD camera input
│   │   └── Calculates distance to obstacles
│   │
│   └── SLAM Layer
│       ├── RTABMap SLAM
│       ├── Visual Odometry
│       └── Loop Closure Detection
│
├── Decision Layer
│   └── Obstacle Avoidance Motion Node
│       ├── Path Clear Detection
│       ├── Corridor Navigation
│       ├── Stuck Detection & Recovery
│       └── Command Generation
│
├── Control Layer
│   ├── ROS2 Navigation Stack
│   ├── cmd_vel Publisher
│   └── Motion Execution
│
└── Simulation & Testing
    ├── Gazebo Environment
    ├── Sensor Simulation
    └── World Models

```

### Data Flow Pipeline

```
RGBD Camera Feed
        ↓
Depth Processor Node (depth_processor_pkg)
        ↓
Depth Image Processing & Sector Calculation
        ↓
Float32MultiArray (/depth/averages)
    [left, center, right, end_left, end_right]
        ↓
Obstacle Avoidance Motion Node
        ↓
Decision Logic & Context Analysis
        ↓
Twist Message (/cmd_vel)
        ↓
Robot Base Controller
        ↓
Robot Motion
```

---

## 📦 Prerequisites

### System Requirements
- **OS**: Ubuntu 22.04 LTS (recommended)
- **ROS2 Version**: Humble or later
- **Python**: 3.10+
- **GPU**: Optional (recommended for SLAM)

### Required Packages

```bash
# Core ROS2 packages
ros-humble-geometry2
ros-humble-sensor-msgs
ros-humble-nav-msgs
ros-humble-cv-bridge

# Simulation
ros-humble-gazebo-*
ros-humble-ros2-control
ros-humble-ros2-controllers

# Navigation & SLAM
ros-humble-rtabmap-ros
ros-humble-robot-localization
ros-humble-navigation2

# Gazebo bridges
ros-humble-ros-gz-sim
ros-humble-ros-gz-bridge
ros-humble-ros-gz-image

# Python dependencies
numpy
opencv-python
opencv-contrib-python
```

---

## 🚀 Installation

### 1. Create ROS2 Workspace

```bash
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws
```

### 2. Clone the Repository

```bash
cd src
git clone https://github.com/harry2326/Autonomous_robot.git
cd ..
```

### 3. Install Dependencies

```bash
# Install system dependencies
sudo apt-get update
sudo apt-get install -y \
  python3-pip \
  python3-numpy \
  python3-opencv \
  ros-humble-rtabmap-ros \
  ros-humble-robot-localization

# Install Python dependencies
pip3 install numpy opencv-python opencv-contrib-python
```

### 4. Build the Workspace

```bash
cd ~/ros2_ws
colcon build --symlink-install

# For a specific package
colcon build --packages-select depth_processor_pkg

# With compile flags for optimization
colcon build --symlink-install -DCMAKE_BUILD_TYPE=Release
```

### 5. Source the Setup File

```bash
source install/setup.bash

# Add to ~/.bashrc for automatic sourcing
echo "source ~/ros2_ws/install/setup.bash" >> ~/.bashrc
```

---

## 📁 Project Structure

```
Autonomous_robot-main/
│
├── src/
│   │
│   ├── basic_obstacle_avoidance/          # ROS2 package (CMake)
│   │   ├── CMakeLists.txt
│   │   ├── package.xml
│   │   ├── URDF/
│   │   │   ├── T2D2.xacro                # Robot definition
│   │   │   ├── links.xacro               # Robot links
│   │   │   ├── links_gazebo.xacro        # Gazebo plugins
│   │   │   └── materials.xacro           # Materials definition
│   │   ├── launch/
│   │   │   ├── my_script_launch.py       # Main launch file
│   │   │   ├── rtabmap_slam.launch.py    # SLAM with visual odometry
│   │   │   ├── rtabmap_slam1.launch.py   # Alternative SLAM config
│   │   │   ├── rtabmap_ICP.launch.py     # ICP-based SLAM
│   │   │   └── rtabmap_vo_sync.launch.py # VO synchronization
│   │   ├── config/
│   │   │   └── ekf.yaml                  # EKF filter configuration
│   │   ├── rviz/
│   │   │   └── T2D2_.rviz                # RViz configuration
│   │   └── worlds/
│   │       └── world2.sdf                # Gazebo world definition
│   │
│   └── depth_processor_pkg/                # ROS2 package (Python)
│       ├── package.xml
│       ├── setup.py
│       ├── setup.cfg
│       ├── depth_processor_pkg/
│       │   ├── __init__.py
│       │   ├── depth_processor_node.py   # Depth image processing
│       │   ├── obstacle_avoidance_motion.py  # Motion control logic
│       │   └── square.py                 # Square movement pattern
│       ├── resource/
│       └── test/
│           ├── test_copyright.py
│           ├── test_flake8.py
│           └── test_pep257.py
│
└── README.md                              # This file

```

---

## ⚡ Quick Start

### Option 1: Run in Simulation

```bash
# Terminal 1: Launch Gazebo and robot
ros2 launch basic_obstacle_avoidance my_script_launch.py

# Terminal 2: Run SLAM
ros2 launch basic_obstacle_avoidance rtabmap_slam.launch.py

# Terminal 3: Run depth processor
ros2 run depth_processor_pkg depth_processor_node

# Terminal 4: Run obstacle avoidance
ros2 run depth_processor_pkg obstacle_avoidance_motion

# Terminal 5: Visualize in RViz (optional)
rviz2 -d ~/ros2_ws/src/basic_obstacle_avoidance/rviz/T2D2_.rviz
```

### Option 2: Run with ICP-Based SLAM

```bash
# Launch Gazebo
ros2 launch basic_obstacle_avoidance my_script_launch.py

# Run ICP SLAM
ros2 launch basic_obstacle_avoidance rtabmap_ICP.launch.py

# Run navigation nodes
ros2 run depth_processor_pkg depth_processor_node
ros2 run depth_processor_pkg obstacle_avoidance_motion
```

### Option 3: Run Visual Odometry Sync

```bash
# For synchronized visual odometry processing
ros2 launch basic_obstacle_avoidance rtabmap_vo_sync.launch.py
```

---

## 📚 Modules Description

### 1. **Depth Processor Node** (`depth_processor_pkg/depth_processor_node.py`)

**Purpose**: Processes depth images from RGBD camera and calculates distance to obstacles

**Key Functions**:
- Converts ROS Image messages to OpenCV format
- Divides depth image into sectors (left, center, right, edges)
- Calculates minimum distance in each sector
- Publishes processed depth data

**Input Topics**:
- `/rgbd_camera/depth_image` - Raw depth image from camera

**Output Topics**:
- `/depth/averages` - Float32MultiArray containing [left, center, right, end_left, end_right]
- `/depth/debug` - Debug visualization image

**Parameters**:
- Image height/width (automatically detected)
- Sector division ratio (1/3 bottom portion analyzed)
- Edge detection zones

**Algorithm**:
```
1. Receive depth image (480x640)
2. Extract bottom 1/3 of image
3. Divide into 5 zones:
   - Left sector (0 to 1/3 width)
   - Center sector (1/3 to 2/3 width)
   - Right sector (2/3 to full width)
   - Far left edge (0 to 20 pixels)
   - Far right edge (last 20 pixels)
4. Calculate minimum distance in each zone
5. Publish as Float32MultiArray
```

---

### 2. **Obstacle Avoidance Motion Node** (`depth_processor_pkg/obstacle_avoidance_motion.py`)

**Purpose**: Implements intelligent navigation logic based on depth information

**Key Functions**:
- Forward motion planning
- Left/right turning logic
- Corridor navigation with centering
- Dead-end/blocked path detection
- Stuck situation recovery

**Input Topics**:
- `/depth/averages` - Processed depth data from depth processor

**Output Topics**:
- `/cmd_vel` - Twist message for robot movement

**Parameters**:
```
SAFE_FORWARD_DIST = 1.0 m        # Min center distance to move forward
SIDE_CLEARANCE_STRAIGHT = 0.5 m  # Side clearance when moving straight
SIDE_CLEARANCE_AFTER_TURN = 0.8 m # Additional clearance after turning
MIN_TURN_TIME = 1.0 s             # Minimum turn duration
ROBOT_WIDTH = 0.4 m               # Physical robot width
SAFETY_MARGIN = 0.2 m             # Buffer zone
STUCK_THRESHOLD = 10              # Consecutive stuck detections before recovery
```

**Navigation Logic Layers**:

1. **Stuck Detection & Recovery**
   - Monitors distance variance over 20 frames
   - Executes backup + random turn if stuck
   - Resets detection after recovery

2. **Blocked Path Detection**
   - Total width < min passage width
   - Center distance < 0.3m
   - Actions: Stop and search

3. **Corridor Navigation**
   - Width: MIN_PASSAGE_WIDTH < total < 1.5m
   - Proportional steering toward wider side
   - Maintains 0.2m/s forward speed

4. **Standard Forward Motion**
   - Center > 1.0m
   - Sides > clearance threshold
   - Moves at 0.3m/s

5. **Turning Logic**
   - Hysteresis-based (0.2m threshold)
   - Turn speed: 0.5 rad/s
   - Turn time tracking for state management

---

### 3. **Square Movement** (`depth_processor_pkg/square.py`)

**Purpose**: Test module for executing square-shaped movements

**Features**:
- Programmed motion in square patterns
- Distance/angle control
- Odometry feedback

---

## ⚙️ Configuration

### EKF Configuration (`config/ekf.yaml`)

Extended Kalman Filter for sensor fusion:

```yaml
ekf_filter_node:
  ros__parameters:
    # Input topics
    imu0: /imu/data
    odom0: /odometry/filtered
    
    # Process noise (system uncertainty)
    process_noise_cov:
      x: 0.05
      y: 0.05
      
    # Measurement noise (sensor uncertainty)
    initial_state_cov:
      x: 1.0
      y: 1.0
```

### RTABMap Configuration

**SLAM Variants Available**:

1. **Visual SLAM** (`rtabmap_slam.launch.py`)
   - Uses visual features for loop closure
   - Visual odometry + feature matching
   - Best for textured environments

2. **ICP SLAM** (`rtabmap_ICP.launch.py`)
   - Iterative Closest Point matching
   - Depth-based point cloud registration
   - Better for uniform surfaces

3. **VO Sync** (`rtabmap_vo_sync.launch.py`)
   - Synchronized visual odometry
   - Reduced drift through correlation
   - Lower computational overhead

### Robot Model (URDF/Xacro)

**T2D2 Robot Specifications**:
- Differential drive base
- RGBD camera (mounted forward)
- Range finder sensors
- Inertial measurement unit (IMU)

**Files**:
- `T2D2.xacro` - Main robot assembly
- `links.xacro` - Physical links and joints
- `links_gazebo.xacro` - Gazebo plugins and physics
- `materials.xacro` - Visual materials

---

## 💡 Usage Examples

### Example 1: Basic Navigation in Simulation

```bash
# Terminal 1: Launch simulation and robot
ros2 launch basic_obstacle_avoidance my_script_launch.py

# Terminal 2: Start SLAM
ros2 launch basic_obstacle_avoidance rtabmap_slam.launch.py

# Terminal 3: Run processing nodes
ros2 run depth_processor_pkg depth_processor_node
ros2 run depth_processor_pkg obstacle_avoidance_motion

# Terminal 4: Monitor with RViz
rviz2

# The robot will now autonomously navigate the Gazebo world
# avoiding obstacles and building a map
```

### Example 2: Monitor Depth Data

```bash
# Listen to raw depth values
ros2 topic echo /depth/averages

# Expected output:
# data: [0.8, 1.2, 0.9, 0.95, 0.87]
# Left=0.8m, Center=1.2m, Right=0.9m, EdgeL=0.95m, EdgeR=0.87m
```

### Example 3: Test Stuck Detection

```bash
# Run the obstacle avoidance node
ros2 run depth_processor_pkg obstacle_avoidance_motion

# Manually publish constant depth values (simulating stuck situation)
ros2 topic pub /depth/averages std_msgs/Float32MultiArray \
  "{data: [0.9, 0.9, 0.9, 0.9, 0.9]}" -r 10

# Watch for STUCK DETECTED message in logs
```

### Example 4: Visualize Robot State

```bash
# In RViz, add displays for:
# - Robot Model (from TF)
# - PointCloud2 (from /cloud_map)
# - Odometry (from /odometry/filtered)
# - Laser Scan (from /scan, if available)
# - Camera Image (/camera/image_raw)
```

---

## 🔧 Troubleshooting

### Issue: Depth Processor Node Won't Start

**Error**: `ModuleNotFoundError: No module named 'cv_bridge'`

**Solution**:
```bash
sudo apt-get install ros-humble-cv-bridge
source /opt/ros/humble/setup.bash
colcon build
```

---

### Issue: Robot Not Moving in Gazebo

**Error**: Robot statue but no motion

**Solution**:
1. Check if `/cmd_vel` topic is being published:
   ```bash
   ros2 topic echo /cmd_vel
   ```

2. Verify Gazebo plugins are loaded:
   ```bash
   grep "ros_gz" ~/ros2_ws/src/basic_obstacle_avoidance/URDF/links_gazebo.xacro
   ```

3. Ensure launch file includes proper bridges:
   ```bash
   ros2 launch basic_obstacle_avoidance my_script_launch.py --show
   ```

---

### Issue: SLAM Not Building Map

**Error**: RTABMap running but map not created

**Solution**:
```bash
# Check visual features are being detected
ros2 run rqt_image_view rqt_image_view
# Subscribe to /camera/image_raw

# Verify RTABMap parameters
rosparam get /rtabmap/rtabmap/

# Check database
rtabmap-databaseViewer ~/.ros/rtabmap.db
```

---

### Issue: High CPU Usage

**Error**: System running slow during SLAM

**Solution**:
```bash
# Reduce image resolution in launch files
# Disable loop closure detection temporarily
# Use ICP SLAM instead of visual SLAM
# Reduce keyframe rate

ros2 launch basic_obstacle_avoidance rtabmap_ICP.launch.py
```

---

### Issue: Odometry Drift

**Error**: Robot's pose diverges from actual position

**Solution**:
1. Calibrate EKF parameters
2. Improve camera calibration
3. Enable loop closure detection
4. Increase RTABMap's confidence threshold

---

## 📊 Performance Metrics

### Recommended Specifications

| Metric | Target | Notes |
|--------|--------|-------|
| **Depth Processing Rate** | 20-30 Hz | Real-time obstacle detection |
| **Navigation Update Rate** | 10 Hz | Sufficient for reactive control |
| **SLAM Loop Rate** | 5-10 Hz | Balance between accuracy and speed |
| **CPU Usage** | < 70% | Leave headroom for system |
| **Memory Usage** | < 2 GB | Manageable on modest hardware |
| **Turn Response** | < 500ms | Time to detect and react to obstacles |

---

## 🤝 Contributors

**Original Developer**: Harpreet Singh (harpreetsinghmunday@todo.todo)

**Project Maintainers**:
- Autonomous Robotics Team

---

## 📝 License

Please see LICENSE file for details.

---

## 🔗 References

### ROS2 Documentation
- [ROS2 Humble Docs](https://docs.ros.org/en/humble/)
- [ROS2 Navigation Stack](https://navigation.ros.org/)

### SLAM & Localization
- [RTABMap Documentation](http://wiki.ros.org/rtabmap_ros)
- [Robot Localization Package](http://wiki.ros.org/robot_localization)

### Simulation
- [Gazebo Documentation](https://gazebosim.org/)
- [URDF/Xacro Guide](http://wiki.ros.org/urdf)

### Computer Vision
- [OpenCV Documentation](https://docs.opencv.org/)
- [cv_bridge Documentation](http://wiki.ros.org/cv_bridge)

---

## 📞 Support & Issues

For issues, questions, or contributions:
1. Check existing GitHub issues
2. Create detailed bug reports with logs
3. Include ROS2 version and system info
4. Provide reproducible steps

---

## 🎯 Future Enhancements

- [ ] Real robot implementation (TurtleBot3, etc.)
- [ ] Multi-floor navigation with level detection
- [ ] Semantic understanding with object detection
- [ ] Dynamic obstacle handling (moving objects)
- [ ] Path optimization with graph-based planning
- [ ] Fleet management for multiple robots
- [ ] Improved stuck recovery using wall following
- [ ] Integration with navigation2 stack
- [ ] Real-time performance optimization
- [ ] Formal testing framework

---

**Last Updated**: May 2026  
**Version**: 1.0.0

