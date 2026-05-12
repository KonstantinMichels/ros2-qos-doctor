from glob import glob
from setuptools import find_packages, setup

package_name = 'ros2_qos_doctor'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml', 'LICENSE', 'README.md']),
        ('share/' + package_name + '/examples', glob('examples/*.yaml')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='ros2-qos-doctor contributors',
    maintainer_email='maintainers@example.com',
    description='Diagnose ROS 2 QoS incompatibilities and suggest fixes.',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'qos_doctor = ros2_qos_doctor.qos_doctor:main',
        ],
    },
)
