import os
from glob import glob

from setuptools import find_packages, setup

package_name = 'live_solution'

setup(
    name=package_name,
    version='0.0.1',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='ARCX6',
    maintainer_email='eyiramgaze@gmail.com',
    description='No prior map: odometry + live SLAM, camera-coverage exploration',
    license='MIT',
    entry_points={'console_scripts': ['live_visitor = live_solution.live_visitor:main',
                                    'odom_fix = live_solution.odom_fix:main']},
)
