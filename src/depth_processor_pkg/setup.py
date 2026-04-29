from setuptools import find_packages, setup

package_name = 'depth_processor_pkg'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='harpreetsinghmunday',
    maintainer_email='harpreetsinghmunday@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [ 'depth_processor_node = depth_processor_pkg.depth_processor_node:main',
                            'obstacle_avoidance_motion = depth_processor_pkg.obstacle_avoidance_motion:main'
        ],
    },
)
