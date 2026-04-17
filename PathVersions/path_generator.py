#!/usrbin/env python
import rclpy, time
from rclpy.node import Node
from turtlesim.msg import Pose



class PathGeneratorClass(Node):
	def __init__(self):
		super().__init__("path_generator")
		self.create_timer(0.1, self.callback_path_gen)
		self.pub = self.create_publisher(Pose, "/next_point", 1)
		self.point_list = [[1.0, 1.0, 20.0],
					    [10.0, 10.0, 40.0],
						[1.0, 1.0, 60.0]] #Point to visit
		self.t0 = time.time()
		
	def callback_path_gen(self):
		if len(self.point_list) > 0:
			elapsed_time = time.time()-self.t0
			[x,y,t] = self.point_list[0]
			print("Elapsed time ", elapsed_time)
			if elapsed_time < t:
				msg = Pose()
				msg.x = x
				msg.y = y
				self.pub.publish(msg)
			else:
				self.point_list.pop(0)
		else:
			print("End of list")
			rclpy.shutdown()
    


def main(args=None):
	rclpy.init(args=args)
	nodeh = PathGeneratorClass()
	
	
	try: rclpy.spin(nodeh)
	except KeyboardInterrupt: print("Terminado por el usuario!!")
	

if __name__== "__main__":
	main()
