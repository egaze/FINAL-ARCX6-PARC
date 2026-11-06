import os
from glob import glob

from setuptools import find_packages, setup

package_name = 'explore_solution'

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
    description='Map-free exploration solution for PARC 2026',
    license='MIT',
    entry_points={
        'console_scripts': [
            'explore_visitor = explore_solution.explore_visitor:main',
        ],
    },
)
