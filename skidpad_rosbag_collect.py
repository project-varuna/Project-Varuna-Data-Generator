import rospy
import rosbag
from datetime import datetime

def record_rosbag(topics, duration, throttle_value, steering_value):
    # Initialize ROS node
    rospy.init_node('rosbag_recorder_node', anonymous=True)

    # Generate rosbag name with throttle, steering values, and timestamp
    bag_name = "skidpad_throttle_{}_steering_{}_date_{}.bag".format(
        throttle_value, steering_value, datetime.now().strftime("%Y%m%d_%H%M%S"))
    bag = rosbag.Bag(bag_name, 'w')

    rospy.loginfo("Starting rosbag recording for topics: {}".format(", ".join(topics)))

    start_time = rospy.Time.now()

    try:
        while not rospy.is_shutdown():
            current_time = rospy.Time.now()
            elapsed_time = (current_time - start_time).to_sec()

            if elapsed_time > duration:
                rospy.loginfo("Recording duration completed.")
                break

            # Record messages for each topic
            for topic in topics:
                try:
                    msg = rospy.wait_for_message(topic, rospy.AnyMsg, timeout=0.1)
                    bag.write(topic, msg)
                except rospy.ROSException as e:
                    rospy.logwarn(f"Could not record topic {topic}: {e}")

    finally:
        bag.close()
        rospy.loginfo("Rosbag saved as {}".format(bag_name))

if __name__ == "__main__":
    topics = [
        '/autodrive/rzr_1/gnss',
        '/autodrive/rzr_1/imu',
        '/autodrive/rzr_1/steering',
        '/autodrive/rzr_1/throttle'
    ]
    duration = float(input("Enter recording duration (seconds): "))
    throttle_value = float(input("Enter throttle value: "))
    steering_value = float(input("Enter steering angle value: "))
    record_rosbag(topics, duration, throttle_value, steering_value)
