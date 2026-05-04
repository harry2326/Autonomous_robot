import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Twist
import math


class ForwardMotionNode(Node):
    def __init__(self):
        super().__init__('forward_motion_node')
        self.start_x = None
        self.right = None
        self.start_yaw = None
        self.complete_square = 0
        self.goal_reached = False
       

        self.odom_subscriber = self.create_subscription(
            Odometry,
            '/odom',
            self.odom_callback,
            10,
        )

        self.cmd_vel_publisher = self.create_publisher(
            Twist,
            '/cmd_vel',
            10,
        )

        self.timer = self.create_timer(0.1, self.timer_callback)

    def odom_callback(self, msg: Odometry):
        current_x = msg.pose.pose.position.x
        current_y = msg.pose.pose.position.y
        q = msg.pose.pose.orientation
        self.current_yaw = math.atan2(2.0 * (q.w * q.z + q.x * q.y), 1.0 - 2.0 * (q.y * q.y + q.z * q.z))
        self.current_yaw_deg = math.degrees(self.current_yaw)

        if self.start_x is None:
            self.start_x = current_x
            self.start_y = current_y
            self.get_logger().info(f'Starting x position: {self.start_x:.3f}')
            return

        if self.right is None and not self.goal_reached:
            distance = math.sqrt((current_x - self.start_x)**2 + (current_y - self.start_y)**2)
        
            if distance >= 0.5:
                self.right = True
                self.start_yaw = self.current_yaw
                self.get_logger().info(
                    f'Reached forward goal: {distance:.3f} m from start'
                )
        elif self.right:
            yaw_diff = abs(self.current_yaw - self.start_yaw)
            if yaw_diff >= math.radians(90):
                self.right = None
                self.complete_square += 1
                if self.complete_square < 4:
                    self.goal_reached = False
                    self.start_x = current_x
                    self.start_y = current_y
                else:
                    self.goal_reached = True

                    self.get_logger().info('Square completed')

    def timer_callback(self):
        twist = Twist()

        if self.start_x is None:
            # Wait until first odom message arrives
            twist.linear.x = 0.0
        elif self.goal_reached:
            twist.linear.x = 0.0
            twist.angular.z = 0.0
        elif self.right:
            twist.linear.x = 0.0
            twist.angular.z = -0.5  # Right turn
        else:
            twist.linear.x = 0.2
            twist.angular.z = 0.0

        self.cmd_vel_publisher.publish(twist)

    def destroy_node(self):
        # Stop the robot before shutdown.
        stop_twist = Twist()
        stop_twist.linear.x = 0.0
        stop_twist.angular.z = 0.0
        self.cmd_vel_publisher.publish(stop_twist)
        return super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = ForwardMotionNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()