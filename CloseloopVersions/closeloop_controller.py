#!/usr/bin/env python3
import math

import rclpy, time
from rclpy.node import Node
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose

class TurtleController(Node):
    def __init__(self):
        super().__init__("turtle_close_loop_controller")
        self.get_logger().info("Turtle Close Loop Controller Started")
        self.create_timer(0.1, self.state_machine)
        #self.pub = self.create_publisher(Twist, "/turtle1/cmd_vel", 1)
        self.pub = self.create_publisher(Twist, "/cmd_vel", 1)
        #self.create_subscription(Pose, "/turtle1/pose", self.pose_callback, 1)
        self.create_subscription(Pose, "/odom", self.odom_callback, 1)
        self.create_subscription(Pose, "/next_point", self.target_callback, 1)

        
        # Parámetros de movimiento
        self.v = 1.0  
        self.w = 1.0  
        self.Kw = 2.0
        self.Kv = 1.0
        self.t0 = time.time()
        self.tolerance_distance = 0.1
        self.tolerance_angle = 0.05

        self.state = "stop"
        self.end_of_accion = False
        self.x, self.y, self.theta = 5.5, 5.5, 0.0
        self.got_target = False
    
    def odom_callback(self, msg):
        self.x = msg.x
        self.y = msg.y
        self.theta = msg.theta


    def target_callback(self, msg):
        if self.got_target == False:
            self.target_x = msg.x
            self.target_y = msg.y
            self.got_target = True
            self.get_logger().info(f"Nuevo punto objetivo: x={msg.x}, y={msg.y}")


    def pose_callback(self, msg):
        self.x = msg.x
        self.y = msg.y
        self.theta = msg.theta


    def state_machine(self):
        if self.state == "stop" and self.got_target == True:
            self.state = "state1"
        if self.state == "state1" and self.end_of_accion == True:
            self.state = "state2"
            self.end_of_accion = False
            self.t0 = time.time()
        if self.state == "state2" and self.end_of_accion == True:
            self.state = "state1"
            self.end_of_accion = False
            self.t0 = time.time()

        if self.state == "stop": self.stop()
        if self.state == "state1": self.go_to_angle()
        if self.state == "state2": self.go_to_point()

    def go_to_point(self):
        if self.got_target == True:

            msg = Twist()
            elapsed_time = time.time() - self.t0
            Dx = self.target_x - self.x
            Dy = self.target_y - self.y
            etheta = math.atan2(Dy, Dx) - self.theta
            etheta = math.atan2(math.sin(etheta), math.cos(etheta))
            error_distance = math.sqrt(Dx**2 + Dy**2)

        
            if error_distance > self.tolerance_distance:  
                msg.linear.x = min(self.v, self.Kv * error_distance)
                msg.angular.z = self.Kw * etheta
                self.pub.publish(msg)
            else:
                self.pub.publish(msg)
                print("Got target")
                self.got_target = False
                self.end_of_accion = True

    def go_to_angle(self):
        if self.got_target == True:
            msg = Twist()
            elapsed_time = time.time() - self.t0
            Dx = self.target_x - self.x
            Dy = self.target_y - self.y
            etheta = math.atan2(Dy, Dx) - self.theta
            etheta = math.atan2(math.sin(etheta), math.cos(etheta))
            if abs(etheta) > self.tolerance_angle:  
                msg.angular.z = self.Kw * etheta
                self.pub.publish(msg)
            else:
                self.pub.publish(msg)
                print("Got target angle")
                self.got_target = False
                self.end_of_accion = True



    def stop(self):
        msg = Twist()
        self.pub.publish(msg)
        if self.end_of_accion == False:
            print("Stopping")
            self.end_of_accion = True


def main(args=None):
    rclpy.init(args=args)
    nodeh = TurtleController()
    try:
        rclpy.spin(nodeh)
    except KeyboardInterrupt:
        print("\nPrograma terminado.")
    finally:
        nodeh.destroy_node()
        rclpy.shutdown()

if __name__ == "__main__":
    main()
