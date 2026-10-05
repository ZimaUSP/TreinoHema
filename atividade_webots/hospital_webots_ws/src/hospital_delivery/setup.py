from glob import glob
import os

from setuptools import find_packages, setup


package_name = 'hospital_delivery'


setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        (
            'share/ament_index/resource_index/packages',
            ['resource/' + package_name],
        ),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.py')),
        (os.path.join('share', package_name, 'worlds'), glob('worlds/*.wbt')),
        (os.path.join('share', package_name, 'protos'), glob('protos/*.proto')),
        (os.path.join('share', package_name, 'resource'), glob('resource/*.urdf')),
        (
            os.path.join(
                'share', package_name, 'controllers', 'straight_line_webots'
            ),
            glob('controllers/straight_line_webots/*.py'),
        ),
        (
            os.path.join('share', package_name, 'student_templates'),
            glob('student_templates/*.py'),
        ),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Equipe de Robótica Hospitalar',
    maintainer_email='robotica@example.com',
    description=(
        'Atividade introdutória de Webots e ROS 2 para entrega hospitalar.'
    ),
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'delivery_l = hospital_delivery.delivery_l:main',
            (
                'delivery_challenge = '
                'hospital_delivery.delivery_challenge:main'
            ),
        ],
    },
)
