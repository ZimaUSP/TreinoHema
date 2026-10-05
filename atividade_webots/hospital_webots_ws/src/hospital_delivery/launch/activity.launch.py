"""Inicia o mundo hospitalar e a ponte entre Webots e ROS 2."""

import os

import launch
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.substitutions import LaunchConfiguration
from webots_ros2_driver.webots_controller import WebotsController
from webots_ros2_driver.webots_launcher import WebotsLauncher


def _launch_setup(context):
    package_dir = get_package_share_directory('hospital_delivery')
    world_name = LaunchConfiguration('world').perform(context)
    if not world_name.endswith('.wbt'):
        world_name += '.wbt'

    world_path = os.path.join(package_dir, 'worlds', world_name)
    robot_description_path = os.path.join(
        package_dir,
        'resource',
        'hospital_robot.urdf',
    )

    webots = WebotsLauncher(world=world_path)
    robot_driver = WebotsController(
        robot_name='hospital_robot',
        parameters=[
            {
                'robot_description': robot_description_path,
                'use_sim_time': True,
            },
        ],
    )

    shutdown_handler = launch.actions.RegisterEventHandler(
        event_handler=launch.event_handlers.OnProcessExit(
            target_action=webots,
            on_exit=[launch.actions.EmitEvent(
                event=launch.events.Shutdown()
            )],
        )
    )

    return [webots, robot_driver, shutdown_handler]


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument(
            'world',
            default_value='hospital_l',
            description=(
                'Nome do mundo: hospital_l ou hospital_l_challenge, '
                'com ou sem a extensão .wbt.'
            ),
        ),
        OpaqueFunction(function=_launch_setup),
    ])
