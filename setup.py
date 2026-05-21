from setuptools import find_packages, setup

package_name = 'xgb_plc_modbus'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools', 'pymodbus>=3.0'],
    zip_safe=True,
    maintainer='kimsungyeoun',
    maintainer_email='kimsungyeoun@todo.todo',
    description='LS XBC-DR10E PLC Modbus RTU ROS 2 node',
    license='MIT',
    entry_points={
        'console_scripts': [
            'plc_node = xgb_plc_modbus.plc_node:main',
        ],
    },
)
