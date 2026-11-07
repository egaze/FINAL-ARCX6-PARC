from setuptools import find_packages, setup

package_name = 'arcx6_monitor'

setup(
    name=package_name,
    version='0.0.1',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='ARCX6',
    maintainer_email='eyiramgaze@gmail.com',
    description='Read-only run monitor for the ARCX6 PARC 2026 solutions',
    license='MIT',
    entry_points={'console_scripts': [
        'run_monitor = arcx6_monitor.run_monitor:main',
    ]},
)
