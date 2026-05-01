import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import numpy as np # Needed for mathematical operations
import cv2 # Import OpenCV
from std_msgs.msg import Float32MultiArray
import random


class DepthChecker(Node):
    def __init__(self):
        super().__init__('depth_checker')
        self.bridge = CvBridge()
        self.subscription = self.create_subscription(
            Image,
            '/rgbd_camera/depth_image',
            self.listener_callback,
            10)
        self.average_distance_publisher = self.create_publisher(Float32MultiArray, '/depth/averages', 10)
        self.debug_publisher = self.create_publisher(Image, '/depth/debug', 10)
        self.get_logger().info('Depth Checker Node has been started.')

    def listener_callback(self, msg):
        # Convert ROS Image to NumPy array
        cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='passthrough')
        height, width = cv_image.shape # e.g., 480, 640


        # clean_image = np.nan_to_num(cv_image, nan=5.0, posinf=5.0, neginf=0.0)
        
        # display_img = cv2.normalize(clean_image, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
        # display_img = cv2.cvtColor(display_img, cv2.COLOR_GRAY2BGR) # Convert to color to draw red lines

        # row_split = height // 3
        # col_split = width // 3

        # # 2. Draw the boundaries (Vertical line at 2/3 height, then 3 columns)
        # # cv2.rectangle(image, (x_start, y_start), (x_end, y_end), color, thickness)
        
        # #  Draw the Bottom 1/3 area
        # cv2.rectangle(display_img, (0, row_split), (width, 2*row_split -30 ), (0, 255, 0), 2)
        
        # # Draw the sector dividers (Vertical lines in the bottom portion)
        # cv2.line(display_img, (col_split + 50 , row_split), (col_split + 50 , 2*row_split -30), (255, 0, 0), 2)
        # cv2.line(display_img, (2*col_split -50 , row_split), (2*col_split - 50 , 2*row_split - 30), (255, 0, 0), 2)

        # # 3. Publish this image back to ROS
        # debug_msg = self.bridge.cv2_to_imgmsg(display_img, encoding="bgr8")
        # self.debug_publisher.publish(debug_msg)



        # --- 1. Vertical Division (Take the bottom 1/3) ---
        # Slicing: [start_row:end_row, start_col:end_col]
        row_split = height // 3
        bottom_portion = cv_image[row_split : 2*row_split -30, :]

        # # --- 2. Horizontal Division of the Bottom Portion ---
        col_split = width // 3
        
        left_sector   = bottom_portion[:, 0 : col_split ]
        end_left_sector = bottom_portion[:, 0 : 20] 
        end_right_sector = bottom_portion[:, width-20 : width]
        middle_sector = bottom_portion[:, col_split : 2 * col_split ]
        right_sector  = bottom_portion[:, 2 * col_split  : width]

        # # --- 3. Calculate Averages ---
        # # Note: We use np.nanmean because depth cameras often return 'NaN' 
        # # (Not a Number) for pixels that are too close or too far.
        avg_left   = np.nanmin(left_sector)
        avg_middle = np.nanmin(middle_sector)
        avg_right  = np.nanmin(right_sector)
        avg_end_left = np.nanmin(end_left_sector)       
        avg_end_right = np.nanmin(end_right_sector)

        # 4. Create the message object
        avg_msg = Float32MultiArray()
        
        # 5. Assign the data as a list
        avg_msg.data = [float(avg_left), float(avg_middle), float(avg_right), float(avg_end_left), float(avg_end_right)]

        # 6. Publish
        self.average_distance_publisher.publish(avg_msg)
        
        self.get_logger().info(f'Published Averages: {avg_msg.data}')
       

def main(args=None):
    rclpy.init(args=args)
    node = DepthChecker()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()