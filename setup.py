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
        ('share/' + package_name + '/examples', glob('examples/*.md')),
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
            (
                'best_effort_publisher = '
                'ros2_qos_doctor.examples.best_effort_publisher:main'
            ),
            'reliable_subscriber = ros2_qos_doctor.examples.reliable_subscriber:main',
            'reliable_publisher = ros2_qos_doctor.examples.reliable_publisher:main',
            (
                'best_effort_subscriber = '
                'ros2_qos_doctor.examples.best_effort_subscriber:main'
            ),
            'volatile_publisher = ros2_qos_doctor.examples.volatile_publisher:main',
            (
                'transient_local_subscriber = '
                'ros2_qos_doctor.examples.transient_local_subscriber:main'
            ),
            (
                'transient_local_publisher = '
                'ros2_qos_doctor.examples.transient_local_publisher:main'
            ),
            'volatile_subscriber = ros2_qos_doctor.examples.volatile_subscriber:main',
            (
                'deadline_mismatch_publisher = '
                'ros2_qos_doctor.examples.deadline_mismatch_publisher:main'
            ),
            (
                'deadline_mismatch_subscriber = '
                'ros2_qos_doctor.examples.deadline_mismatch_subscriber:main'
            ),
            (
                'deadline_compatible_publisher = '
                'ros2_qos_doctor.examples.deadline_compatible_publisher:main'
            ),
            (
                'deadline_compatible_subscriber = '
                'ros2_qos_doctor.examples.deadline_compatible_subscriber:main'
            ),
            (
                'liveliness_mismatch_publisher = '
                'ros2_qos_doctor.examples.liveliness_mismatch_publisher:main'
            ),
            (
                'liveliness_mismatch_subscriber = '
                'ros2_qos_doctor.examples.liveliness_mismatch_subscriber:main'
            ),
            (
                'liveliness_compatible_publisher = '
                'ros2_qos_doctor.examples.liveliness_compatible_publisher:main'
            ),
            (
                'liveliness_compatible_subscriber = '
                'ros2_qos_doctor.examples.liveliness_compatible_subscriber:main'
            ),
            (
                'lease_mismatch_publisher = '
                'ros2_qos_doctor.examples.lease_mismatch_publisher:main'
            ),
            (
                'lease_mismatch_subscriber = '
                'ros2_qos_doctor.examples.lease_mismatch_subscriber:main'
            ),
            (
                'lease_compatible_publisher = '
                'ros2_qos_doctor.examples.lease_compatible_publisher:main'
            ),
            (
                'lease_compatible_subscriber = '
                'ros2_qos_doctor.examples.lease_compatible_subscriber:main'
            ),
        ],
    },
)
