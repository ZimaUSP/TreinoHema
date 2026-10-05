"""Missão em L com parada e retomada diante de um obstáculo."""

import math
from enum import Enum, auto

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node
from sensor_msgs.msg import LaserScan


class MissionState(Enum):
    WAITING = auto()
    FIRST_STRAIGHT = auto()
    BEFORE_TURN = auto()
    TURNING = auto()
    SECOND_STRAIGHT = auto()
    DELIVERING = auto()
    FINISHED = auto()


class DeliveryChallenge(Node):
    LINEAR_SPEED = 0.20
    ANGULAR_SPEED = 0.50

    WAIT_TIME = 2.0
    FIRST_STRAIGHT_TIME = 10.0
    BEFORE_TURN_TIME = 1.0
    TURN_TIME = 3.1416
    SECOND_STRAIGHT_TIME = 7.5
    DELIVERY_TIME = 5.0

    SLOW_DISTANCE = 0.80
    STOP_DISTANCE = 0.50
    FRONT_HALF_ANGLE = math.radians(15.0)

    def __init__(self):
        super().__init__('delivery_challenge')

        self.publisher = self.create_publisher(Twist, '/cmd_vel', 10)
        self.scan_subscription = self.create_subscription(
            LaserScan,
            '/scan',
            self.scan_callback,
            10,
        )

        self.state = MissionState.WAITING
        self.state_started_at = self.get_clock().now()
        self.front_distance = math.inf
        self.blocked_since = None
        self.finished_logged = False

        self.timer = self.create_timer(0.05, self.control_loop)
        self.get_logger().info('Missão com segurança iniciada.')

    def scan_callback(self, message):
        front_ranges = []

        for index, distance in enumerate(message.ranges):
            angle = message.angle_min + index * message.angle_increment
            is_front = abs(angle) <= self.FRONT_HALF_ANGLE
            is_valid = (
                math.isfinite(distance)
                and message.range_min <= distance <= message.range_max
            )
            if is_front and is_valid:
                front_ranges.append(distance)

        self.front_distance = min(front_ranges) if front_ranges else math.inf

    def elapsed_in_state(self):
        return (
            self.get_clock().now() - self.state_started_at
        ).nanoseconds / 1e9

    def change_state(self, new_state):
        self.state = new_state
        self.state_started_at = self.get_clock().now()
        self.blocked_since = None
        self.get_logger().info(f'Novo estado: {new_state.name}')

    def update_pause(self):
        """Pausa o cronômetro somente no segundo corredor."""
        now = self.get_clock().now()
        blocked = (
            self.state == MissionState.SECOND_STRAIGHT
            and self.front_distance < self.STOP_DISTANCE
        )

        if blocked and self.blocked_since is None:
            self.blocked_since = now
            self.get_logger().warn(
                'Carrinho detectado a %.2f m: parada de segurança.'
                % self.front_distance
            )

        if not blocked and self.blocked_since is not None:
            paused_duration = now - self.blocked_since
            self.state_started_at = self.state_started_at + paused_duration
            self.blocked_since = None
            self.get_logger().info('Caminho liberado: retomando missão.')

        return blocked

    def apply_safety(self, command):
        if (
            self.state != MissionState.SECOND_STRAIGHT
            or command.linear.x <= 0.0
        ):
            return command

        if self.front_distance < self.STOP_DISTANCE:
            command.linear.x = 0.0
            command.angular.z = 0.0
        elif self.front_distance < self.SLOW_DISTANCE:
            command.linear.x *= 0.5

        return command

    def control_loop(self):
        blocked = self.update_pause()
        elapsed = self.elapsed_in_state()
        command = Twist()

        if blocked:
            self.publisher.publish(command)
            return

        if self.state == MissionState.WAITING:
            if elapsed >= self.WAIT_TIME:
                self.change_state(MissionState.FIRST_STRAIGHT)

        elif self.state == MissionState.FIRST_STRAIGHT:
            command.linear.x = self.LINEAR_SPEED
            if elapsed >= self.FIRST_STRAIGHT_TIME:
                command.linear.x = 0.0
                self.change_state(MissionState.BEFORE_TURN)

        elif self.state == MissionState.BEFORE_TURN:
            if elapsed >= self.BEFORE_TURN_TIME:
                self.change_state(MissionState.TURNING)

        elif self.state == MissionState.TURNING:
            command.angular.z = self.ANGULAR_SPEED
            if elapsed >= self.TURN_TIME:
                command.angular.z = 0.0
                self.change_state(MissionState.SECOND_STRAIGHT)

        elif self.state == MissionState.SECOND_STRAIGHT:
            command.linear.x = self.LINEAR_SPEED
            if elapsed >= self.SECOND_STRAIGHT_TIME:
                command.linear.x = 0.0
                self.change_state(MissionState.DELIVERING)

        elif self.state == MissionState.DELIVERING:
            if elapsed >= self.DELIVERY_TIME:
                self.change_state(MissionState.FINISHED)

        elif self.state == MissionState.FINISHED and not self.finished_logged:
            self.get_logger().info('Entrega concluída. Robô parado.')
            self.finished_logged = True

        command = self.apply_safety(command)
        self.publisher.publish(command)


def main(args=None):
    rclpy.init(args=args)
    node = DeliveryChallenge()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.publisher.publish(Twist())
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
