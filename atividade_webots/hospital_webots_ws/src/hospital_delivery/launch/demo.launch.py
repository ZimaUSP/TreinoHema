"""Demonstração automática: simulador, driver e nó de missão."""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, TimerAction
from launch.conditions import IfCondition, UnlessCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    package_dir = get_package_share_directory('hospital_delivery')
    challenge = LaunchConfiguration('challenge')
    world = LaunchConfiguration('world')

    simulation = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(package_dir, 'launch', 'activity.launch.py')
        ),
        launch_arguments={'world': world}.items(),
    )

    regular_mission = Node(
        package='hospital_delivery',
        executable='delivery_l',
        name='delivery_l',
        output='screen',
        parameters=[{'use_sim_time': True}],
        condition=UnlessCondition(challenge),
    )

    challenge_mission = Node(
        package='hospital_delivery',
        executable='delivery_challenge',
        name='delivery_challenge',
        output='screen',
        parameters=[{'use_sim_time': True}],
        condition=IfCondition(challenge),
    )

    delayed_missions = TimerAction(
        period=4.0,
        actions=[regular_mission, challenge_mission],
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'challenge',
            default_value='false',
            description='Executa a versão com segurança por LiDAR.',
        ),
        DeclareLaunchArgument(
            'world',
            default_value='hospital_l',
            description='Mundo a ser carregado pelo Webots.',
        ),
        simulation,
        delayed_missions,
    ])
