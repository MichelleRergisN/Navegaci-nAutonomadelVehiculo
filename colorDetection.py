#!/usr/bin/env python3
import cv2
import numpy as np
import rclpy
from rclpy.node import Node
from rclpy import qos
from sensor_msgs.msg import Image
from std_msgs.msg import String
from cv_bridge import CvBridge


class ColorDetectionNode(Node):

    def __init__(self):
        super().__init__('color_detection_node')
        self.get_logger().info("Nodo de detección de semáforo iniciado")

        self.bridge = CvBridge()
        self.frame = None

        # Publisher del estado del semáforo
        self.pub = self.create_publisher(String, '/traffic_light', 10)

        # Subscriber de cámara
        self.sub = self.create_subscription(Image,'/video_source/raw',self.image_callback,qos.qos_profile_sensor_data)

        # Timer de procesamiento
        self.timer = self.create_timer(0.05, self.process_image)

        # Estado actual
        self.current_state = "NONE"

    def image_callback(self, msg):
        self.frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')

    def process_image(self):
        if self.frame is None:
            return

        frame = self.frame.copy()

        # Convertir a HSV
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # =====================
        # Rangos de color
        # =====================

        # Verde
        lower_green = np.array([40, 50, 50])
        upper_green = np.array([80, 255, 255])

        # Amarillo
        lower_yellow = np.array([20, 100, 100])
        upper_yellow = np.array([35, 255, 255])

        # Rojo (dos rangos)
        lower_red1 = np.array([0, 150, 120])
        upper_red1 = np.array([10, 255, 255])

        lower_red2 = np.array([170, 150, 120])
        upper_red2 = np.array([180, 255, 255])

        # =====================
        # Máscaras
        # =====================
        mask_green = cv2.inRange(hsv, lower_green, upper_green)
        mask_yellow = cv2.inRange(hsv, lower_yellow, upper_yellow)
        mask_red = cv2.inRange(hsv, lower_red1, upper_red1) + \
                   cv2.inRange(hsv, lower_red2, upper_red2)

        # =====================
        # Cálculo de áreas
        # =====================
        area_green = np.sum(mask_green > 0)
        area_yellow = np.sum(mask_yellow > 0)
        area_red = np.sum(mask_red > 0)

        # =====================
        # Decisión de estado
        # =====================
        threshold = 5000  # Ajustable según tu cámara

        if area_red > threshold:
            state = "RED"
        elif area_yellow > threshold:
            state = "YELLOW"
        elif area_green > threshold:
            state = "GREEN"
        else:
            state = "NONE"

        # Publicar solo si cambia (opcional pero recomendado)
        if state != self.current_state:
            self.current_state = state
            msg = String()
            msg.data = state
            self.pub.publish(msg)
            self.get_logger().info(f"Estado detectado: {state}")

        # =====================
        # Visualización
        # =====================
        result = frame.copy()

        if state == "RED":
            cv2.putText(result, "ROJO", (50, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)

        elif state == "YELLOW":
            cv2.putText(result, "AMARILLO", (50, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 3)

        elif state == "GREEN":
            cv2.putText(result, "VERDE", (50, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)

        cv2.imshow("Camara", frame)
        cv2.imshow("Deteccion", result)

        cv2.waitKey(1)


def main(args=None):
    rclpy.init(args=args)
    node = ColorDetectionNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        print("Nodo detenido por el usuario")

    node.destroy_node()
    cv2.destroyAllWindows()
    rclpy.shutdown()


if __name__ == '__main__':
    main()