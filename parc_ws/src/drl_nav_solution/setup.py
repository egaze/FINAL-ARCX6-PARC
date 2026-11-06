import os
from glob import glob

from setuptools import find_packages, setup

package_name = 'drl_nav_solution'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml', 'README.md']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.py')),
        (os.path.join('share', package_name, 'weights'), glob('weights/*.npz')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='ARCX6',
    maintainer_email='eyiramgaze@gmail.com',
    description='Map-free PARC 2026 solution navigated by a PEEMEF-DARC reinforcement-learning policy',
    license='MIT',
    entry_points={
        'console_scripts': [
            'drl_visitor = drl_nav_solution.drl_visitor:main',
        ],
    },
)
