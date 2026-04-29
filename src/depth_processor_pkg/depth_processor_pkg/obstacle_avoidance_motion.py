import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32MultiArray
from geometry_msgs.msg import Twist

class ObstacleAvoidanceMotion(Node):
    def __init__(self):
        super().__init__('obstacle_avoidance_motion')
        self.subscription = self.create_subscription(
            Float32MultiArray,
            '/depth/averages',
            self.listener_callback,
            10)
        self.get_logger().info('Obstacle Avoidance Motion Node has been started.')  
        self.cmd_vel_pub = self.create_publisher(Twist, '/cmd_vel', 10)


    def listener_callback(self, msg):
        # msg.data is a list of 3 average distances: [left_avg, middle_avg, right_avg]
        left_avg, middle_avg, right_avg = msg.data
        
        # Simple logic for obstacle avoidance based on average distances
 # Create a new Twist message object
        move_msg = Twist()

        # --- NAVIGATION LOGIC ---
        if middle_avg > 1:
            self.get_logger().info('Path is clear. Moving straight.')
            move_msg.linear.x = 0.3
            move_msg.angular.z = 0.0

        # elif middle_avg < 0.5 and left_avg < 0.5 and right_avg < 0.5:
        #     if left_avg > right_avg:
        #         self.get_logger().info('Obstacle all around. Moving backward and then left.')
        #         move_msg.linear.x = -0.1
        #         move_msg.angular.z = 0.5
        #     else:
        #         self.get_logger().info('Obstacle all around. Moving backward and then right.')
        #         move_msg.linear.x = -0.1
        #         move_msg.angular.z = -0.5

        elif left_avg > right_avg:
            self.get_logger().info('More space on left. Turning left until path ahead is clear.')
            move_msg.linear.x = 0.0
            move_msg.angular.z = 0.5

        elif right_avg > left_avg:
            self.get_logger().info('More space on right. Turning right until path ahead is clear.')
            move_msg.linear.x = 0.0
            move_msg.angular.z = -0.5

        else:
            self.get_logger().info('Path uncertain. Holding position.')
            move_msg.linear.x = 0.0
            move_msg.angular.z = 0.0

        # --- PUBLISH THE COMMAND ---
        self.cmd_vel_pub.publish(move_msg)


def main(args=None):
    rclpy.init(args=args)
    node = ObstacleAvoidanceMotion()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()