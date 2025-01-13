import rospy
from std_msgs.msg import Float32
import rosbag
from datetime import datetime


def skidpad_control(velocity, steering_angle):
    # Initialize ROS node
    rospy.init_node('skidpad_control_node', anonymous=True)

    # Parameters
    rate_hz = 10
    run_time = 20  # seconds
    steering_direction = "ccw" if steering_angle > 0 else "cw"

    # Converting float to underscores
    throttle_str = f"throttle_{int(velocity)}_{int((velocity - int(velocity)) * 10)}"
    steering_str = f"steering_{-int(steering_angle)}_{int((abs(steering_angle) - int(abs(steering_angle))) * 10)}"

    output_bag_name = f"skidpad_{steering_direction}_{throttle_str}_{steering_str}_date_{datetime.now().strftime('%Y%m%d')}.bag"

    # Publishers
    throttle_pub = rospy.Publisher('/autodrive/rzr_1/throttle_command', Float32, queue_size=10)
    steering_pub = rospy.Publisher('/autodrive/rzr_1/steering_command', Float32, queue_size=10)
    handbrake_pub = rospy.Publisher('/autodrive/rzr_1/handbrake_command', Float32, queue_size=10)
    # handbrake_pub.publish(Float32(data=0.0))  # Release handbrake

    # ROS Bag for recording
    bag = rosbag.Bag(output_bag_name, 'w')

    # Start time
    start_time = rospy.Time.now()
    rate = rospy.Rate(rate_hz)

    try:
        while not rospy.is_shutdown():
            current_time = rospy.Time.now()
            elapsed_time = (current_time - start_time).to_sec()

            # Stop after run_time seconds
            if elapsed_time > run_time:
                rospy.loginfo("Run time completed.")
                break

            # Publish control commands
            throttle_msg = Float32()
            steering_msg = Float32()

            throttle_msg.data = velocity
            steering_msg.data = steering_angle

            throttle_pub.publish(throttle_msg)
            steering_pub.publish(steering_msg)

            # Record specific topics in the rosbag
            for topic in ['/autodrive/rzr_1/gnss', '/autodrive/rzr_1/imu',
                          '/autodrive/rzr_1/steering', '/autodrive/rzr_1/throttle']:
                try:
                    msg = rospy.wait_for_message(topic, rospy.AnyMsg, timeout=1.0)
                    bag.write(topic, msg)
                except rospy.ROSException as e:
                    rospy.logwarn(f"Could not record topic {topic}: {e}")

            # Simulate processing rate
            rate.sleep()

    finally:
        # Send zero throttle and steering commands
        throttle_pub.publish(Float32(data=0.0))
        steering_pub.publish(Float32(data=0.0))

        # Engage handbrake
        handbrake_pub.publish(Float32(data=1.0))

        # Close bag file
        bag.close()
        rospy.loginfo("Rosbag saved to {}".format(output_bag_name))
        rospy.loginfo("Node shutting down.")
        # Disengage handbrake
        handbrake_pub.publish(Float32(data=0.0))


if __name__ == "__main__":
    # Example: Call skidpad_control with arguments
    velocity = float(input("Enter throttle value: "))
    steering_angle = float(input("Enter steering angle value: "))
    skidpad_control(velocity, steering_angle)
