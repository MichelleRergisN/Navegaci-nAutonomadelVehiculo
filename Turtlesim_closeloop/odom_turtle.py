#!/usr/bin/env python3
import rclpy, time, math
from rclpy.node import Node
from turtlesim.msg import Pose

class TurtleOdometry(Node):
    def __init__(self):
        super().__init__("odometry_node")
        self.get_logger().info("Robot pose estimated by odometry [turtlesim mode]")

        self.rate = 100.0
        self.v = 0.0
        self.w = 0.0

        # Posición inicial de turtlesim (centro del canvas 11x11)
        self.x, self.y, self.theta = 5.5, 5.5, 0.0

        self.pub = self.create_publisher(Pose, "/odom", 1)
        self.timer = self.create_timer(1.0 / self.rate, self.callback_odometry)

        # Suscribirse a la pose real del turtlesim para obtener v y w
        self.create_subscription(Pose, "/turtle1/pose", self.pose_callback, 1)

        self.t0 = time.time()

    def callback_odometry(self):
        elapsed_time = time.time() - self.t0
        self.t0 = time.time()

        # Integrar posición con el mismo modelo cinemático unicycle
        self.x     += elapsed_time * self.v * math.cos(self.theta)
        self.y     += elapsed_time * self.v * math.sin(self.theta)
        self.theta += elapsed_time * self.w
        self.theta  = math.atan2(math.sin(self.theta), math.cos(self.theta))

        msg = Pose()
        msg.x     = self.x
        msg.y     = self.y
        msg.theta = self.theta
        self.pub.publish(msg)

    def pose_callback(self, msg):
        # turtlesim publica directamente v y w en su Pose
        self.v = msg.linear_velocity
        self.w = msg.angular_velocity


def main(args=None):
    rclpy.init(args=args)
    nodeh = TurtleOdometry()
    try:
        rclpy.spin(nodeh)
    except KeyboardInterrupt:
        print("Terminado por el usuario!!")


if __name__ == "__main__":
    main()
