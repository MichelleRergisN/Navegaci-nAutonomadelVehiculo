#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import String

class TrafficDecisionNode(Node):
    def __init__(self):
        super().__init__("traffic_decision_node")

        self.get_logger().info("Nodo de decisión de semáforo iniciado")

        self.current_cmd = Twist()
        self.traffic_state = "GREEN"

        # Subscripciones
        self.create_subscription(Twist, "/cmd_vel_raw", self.cmd_callback, 10)

        self.create_subscription(String, "/traffic_light", self.traffic_callback, 10)

        # Publicador final
        self.pub = self.create_publisher(Twist, "/cmd_vel", 10)

        self.timer = self.create_timer(0.02, self.control_loop)

    def cmd_callback(self, msg):
        self.current_cmd = msg

    def traffic_callback(self, msg):
        self.traffic_state = msg.data

    def control_loop(self):
        output = Twist()

        # 🔴 ROJO → STOP
        if self.traffic_state == "RED":
            output.linear.x = 0.0
            output.angular.z = 0.0

        # 🟡 AMARILLO → REDUCE VELOCIDAD
        elif self.traffic_state == "YELLOW":
            output.linear.x = 0.5 * self.current_cmd.linear.x
            output.angular.z = self.current_cmd.angular.z

        # 🟢 VERDE → NORMAL
        else:
            output = self.current_cmd

        self.pub.publish(output)


def main(args=None):
    rclpy.init(args=args)
    node = TrafficDecisionNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
