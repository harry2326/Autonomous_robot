import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32MultiArray
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
import time
import math 
import random
import numpy as np

class ObstacleAvoidanceMotion(Node):
    def __init__(self):
        super().__init__('obstacle_avoidance_motion')

        self.last_action = 'forward'  # 'forward', 'turning_left', 'turning_right'
        self.turn_start_time = None
        
        # Thresholds
        self.SAFE_FORWARD_DIST = 1.0      # Minimum center distance to go forward
        self.SIDE_CLEARANCE_STRAIGHT = 0.5  # Side clearance needed when going straight
        self.SIDE_CLEARANCE_AFTER_TURN = 0.8  # MORE clearance needed after turning
        self.MIN_TURN_TIME = 1.0  # Minimum time to complete a turn (seconds)
        self.ROBOT_WIDTH = 0.4  
        self.SAFETY_MARGIN = 0.2
        self.MIN_PASSAGE_WIDTH = self.ROBOT_WIDTH + self.SAFETY_MARGIN
        self.stuck_counter = 0
        self.STUCK_THRESHOLD = 10  # Consecutive stuck detections
        self.last_distances = []
        self.MAX_HISTORY = 20

        self.subscription = self.create_subscription(
            Float32MultiArray,
            '/depth/averages',
            self.listener_callback,
            10)
        self.get_logger().info('Obstacle Avoidance Motion Node has been started.')  
        self.cmd_vel_pub = self.create_publisher(Twist, '/cmd_vel', 10)



    def is_stuck(self, left_avg, middle_avg, right_avg):
            # """Detect if robot is stuck (distances not changing)"""
            
            current = (left_avg, middle_avg, right_avg)
            self.last_distances.append(current)
            
            # Keep only recent history
            if len(self.last_distances) > self.MAX_HISTORY:
                self.last_distances.pop(0)
            
            # Need enough history
            if len(self.last_distances) < self.MAX_HISTORY:
                return False
            
            # Check variance in distances
            middle_variance = np.var([d[1] for d in self.last_distances])
            
            # If middle distance barely changes, we're stuck
            if middle_variance < 0.0:  # Very low variance
                self.stuck_counter += 1
            else:
                self.stuck_counter = 0
            
            return self.stuck_counter > self.STUCK_THRESHOLD
    
    def listener_callback(self, msg):
        # msg.data is a list of 5 average distances: [left_avg, middle_avg, right_avg, end_left_avg, end_right_avg]
        data = [float(x) for x in msg.data]
        left_avg, middle_avg, right_avg, end_left_avg, end_right_avg = data
        total_width = left_avg + right_avg
        width_balance = abs(left_avg - right_avg)


        total_width = left_avg + right_avg
        width_balance = abs(left_avg - right_avg)
    
        # ---  CONTEXT DETECTION ---
        # Corridor: Narrow enough to need centering, but wide enough to fit.
        is_corridor = (self.MIN_PASSAGE_WIDTH < total_width < 1.5) and (width_balance < 0.5)
        
        # Dead End/Too Narrow: Total space is less than robot width.
        is_blocked = (total_width < self.MIN_PASSAGE_WIDTH) or (middle_avg < 0.3)
        
        # Simple logic for obstacle avoidance based on average distances
        # Create a new Twist message object
        move_msg = Twist()
    
        current_time = self.get_clock().now()
        
        # Check if we just finished turning
        recently_turned = False
        if self.last_action in ['turning_left', 'turning_right']:
            if self.turn_start_time is not None:
                time_since_turn = (current_time - self.turn_start_time).nanoseconds / 1e9
                recently_turned = time_since_turn < self.MIN_TURN_TIME
        
        # Determine required side clearance
        if recently_turned or self.last_action in ['turning_left', 'turning_right']:
            required_side_clearance = self.SIDE_CLEARANCE_AFTER_TURN
        else:
            required_side_clearance = self.SIDE_CLEARANCE_STRAIGHT


        
        # Decision logic

        # if end_left_avg < 0.3:
        #     self.get_logger().warn("Scraping LEFT side! Adjusting...")
        #     move_msg.linear.x = 0.0 # Move very slowly
        #     move_msg.angular.z = -0.4 # Turn away from the wall (Right)
            
    
        # elif end_right_avg   < 0.3:
        #     self.get_logger().warn("Scraping RIGHT side! Adjusting...")
        #     move_msg.linear.x = 0.0
        #     move_msg.angular.z = 0.4 # Turn away from the wall (Left)
        if self.is_stuck(left_avg, middle_avg, right_avg):
            self.get_logger().warn('STUCK DETECTED! Executing recovery behavior.')
            
            # Recovery: back up and turn randomly
            move_msg.linear.x = -0.2
            move_msg.angular.z = float(random.choice([-0.8, 0.8]))
            
            # Reset stuck counter after recovery
            self.stuck_counter = 0
            self.last_distances.clear()

        elif is_blocked:
            self.get_logger().info("PATH BLOCKED: Searching for exit...")
            move_msg.linear.x = 0.0
            # Turn toward the side with more space
            # move_msg.angular.z = 0.5 if left_avg > right_avg else -0.5
            move_msg.angular.z = 0.0


            self.last_action = 'stopped'

        # LAYER 3: CORRIDOR NAVIGATION (Adaptive Centering)
        elif is_corridor:
            self.get_logger().info("MODE: Corridor Centering")
            move_msg.linear.x = 0.2  # Maintain steady slow speed
            # Proportional Steering: steer toward the side with MORE space
            # If left=0.6, right=0.4 -> diff=0.2 -> steer left slightly
            steering_gain = 0.8 
            move_msg.angular.z = (left_avg - right_avg) * steering_gain
            self.last_action = 'forward_corridor'
            

        elif (middle_avg > self.SAFE_FORWARD_DIST and 
            left_avg > required_side_clearance and 
            right_avg > required_side_clearance):
            
            self.get_logger().info(f'Path clear. Moving forward. (L:{left_avg:.2f} C:{middle_avg:.2f} R:{right_avg:.2f})')
            move_msg.linear.x = 0.3
            move_msg.angular.z = 0.0
            self.last_action = 'forward'
            self.turn_start_time = None
        
        elif left_avg > right_avg + 0.2:  # 0.2m hysteresis
            self.get_logger().info(f'Turning left. (L:{left_avg:.2f} > R:{right_avg:.2f})')
            move_msg.linear.x = 0.0
            move_msg.angular.z = 0.5
            
            if self.last_action != 'turning_left':
                self.turn_start_time = current_time
            self.last_action = 'turning_left'
        
        elif right_avg > left_avg + 0.2:  # 0.2m hysteresis
            self.get_logger().info(f'Turning right. (L:{left_avg:.2f} < R:{right_avg:.2f})')
            move_msg.linear.x = 0.0
            move_msg.angular.z = -0.5
            
            if self.last_action != 'turning_right':
                self.turn_start_time = current_time
            self.last_action = 'turning_right'
        
        else:
            if self.last_action == 'turning_left':
                move_msg.linear.x = 0.1
                move_msg.angular.z = 0.5
                self.get_logger().info('Continuing left turn (hysteresis)')
            elif self.last_action == 'turning_right':
                move_msg.linear.x = 0.1
                move_msg.angular.z = -0.5
                self.get_logger().info('Continuing right turn (hysteresis)')
            else:
                move_msg.linear.x = 0.0
                move_msg.angular.z = 0.0
        
        self.cmd_vel_pub.publish(move_msg)


def main(args=None):
    rclpy.init(args=args)
    node = ObstacleAvoidanceMotion()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()