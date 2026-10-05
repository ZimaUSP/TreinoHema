"""Plugin que conecta o robô simulado aos comandos ROS 2.

O webots_ros2_driver carrega esta classe a partir do arquivo URDF em
``resource/hospital_robot.urdf``. O plugin converte ``geometry_msgs/Twist``
em velocidades individuais para as duas rodas do robô.
"""

import math

import rclpy
from geometry_msgs.msg import Twist


class HospitalRobotDriver:
    """Driver diferencial mínimo para fins didáticos."""

    def init(self, webots_node, properties):
        self._robot = webots_node.robot

        self._wheel_radius = float(properties.get('wheelRadius', 0.05))
        self._half_wheel_separation = float(
            properties.get('halfWheelSeparation', 0.16)
        )
        self._max_wheel_speed = float(properties.get('maxWheelSpeed', 12.0))
        self._command_timeout = float(properties.get('commandTimeout', 0.75))

        self._left_motor = self._robot.getDevice('left wheel motor')
        self._right_motor = self._robot.getDevice('right wheel motor')

        self._left_motor.setPosition(float('inf'))
        self._right_motor.setPosition(float('inf'))
        self._left_motor.setVelocity(0.0)
        self._right_motor.setVelocity(0.0)

        self._target_twist = Twist()
        self._last_command_time = self._robot.getTime()

        if not rclpy.ok():
            rclpy.init(args=None)

        self._node = rclpy.create_node('hospital_robot_driver')
        self._subscription = self._node.create_subscription(
            Twist,
            '/cmd_vel',
            self._cmd_vel_callback,
            10,
        )

        self._node.get_logger().info(
            'Driver iniciado: raio=%.3f m, meia-separação=%.3f m'
            % (self._wheel_radius, self._half_wheel_separation)
        )

    def _cmd_vel_callback(self, message):
        self._target_twist = message
        self._last_command_time = self._robot.getTime()

    def _clamp(self, value):
        return max(-self._max_wheel_speed, min(self._max_wheel_speed, value))

    def step(self):
        rclpy.spin_once(self._node, timeout_sec=0)

        command_age = self._robot.getTime() - self._last_command_time
        if command_age > self._command_timeout:
            forward_speed = 0.0
            angular_speed = 0.0
        else:
            forward_speed = self._target_twist.linear.x
            angular_speed = self._target_twist.angular.z

        left_speed = (
            forward_speed
            - angular_speed * self._half_wheel_separation
        ) / self._wheel_radius
        right_speed = (
            forward_speed
            + angular_speed * self._half_wheel_separation
        ) / self._wheel_radius

        if not math.isfinite(left_speed) or not math.isfinite(right_speed):
            left_speed = 0.0
            right_speed = 0.0

        self._left_motor.setVelocity(self._clamp(left_speed))
        self._right_motor.setVelocity(self._clamp(right_speed))
