import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import FrontendLaunchDescriptionSource, PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
  world_name = LaunchConfiguration('world_name')
  cameraOffsetZ = LaunchConfiguration('cameraOffsetZ')
  vehicleX = LaunchConfiguration('vehicleX')
  vehicleY = LaunchConfiguration('vehicleY')
  checkTerrainConn = LaunchConfiguration('checkTerrainConn')
  robot_config = LaunchConfiguration('robot_config')
  autonomy_mode = LaunchConfiguration('autonomyMode')
  slam_config_file = LaunchConfiguration('slam_config_file')

  network_interface = LaunchConfiguration('network_interface')
  g1_loco_client_path = LaunchConfiguration('g1_loco_client_path')
  unitree_sdk_lib_path = LaunchConfiguration('unitree_sdk_lib_path')
  command_timeout = LaunchConfiguration('command_timeout')
  max_x_linear_velocity = LaunchConfiguration('max_x_linear_velocity')
  max_y_linear_velocity = LaunchConfiguration('max_y_linear_velocity')
  max_angular_velocity = LaunchConfiguration('max_angular_velocity')

  declare_world_name = DeclareLaunchArgument('world_name', default_value='real_world', description='')
  declare_cameraOffsetZ = DeclareLaunchArgument('cameraOffsetZ', default_value='0.25', description='')
  declare_vehicleX = DeclareLaunchArgument('vehicleX', default_value='0.0', description='')
  declare_vehicleY = DeclareLaunchArgument('vehicleY', default_value='0.0', description='')
  declare_checkTerrainConn = DeclareLaunchArgument('checkTerrainConn', default_value='true', description='')
  declare_robot_config = DeclareLaunchArgument(
    'robot_config',
    default_value='unitree/unitree_g1',
    description='Robot-specific navigation and mounting config'
  )
  declare_autonomy_mode = DeclareLaunchArgument(
    'autonomyMode',
    default_value='true',
    description='Enable waypoint autonomy by default on G1'
  )
  declare_slam_config_file = DeclareLaunchArgument(
    'slam_config_file',
    default_value=os.path.join(
      get_package_share_directory('arise_slam_mid360'),
      'config',
      'livox_mid360.yaml'),
    description='Path to arise_slam_mid360 config yaml'
  )

  declare_network_interface = DeclareLaunchArgument(
    'network_interface',
    default_value='enp108s0',
    description='Network interface used by g1_loco_client; use enp108s0 for the Unitree SDK control link, not Meta'
  )
  declare_g1_loco_client_path = DeclareLaunchArgument(
    'g1_loco_client_path',
    default_value='/home/mhw/robot_g1/unitree_sdk2/build/bin/g1_loco_client',
    description='Path to Unitree g1_loco_client executable'
  )
  declare_unitree_sdk_lib_path = DeclareLaunchArgument(
    'unitree_sdk_lib_path',
    default_value='/home/mhw/robot_g1/unitree_sdk2/thirdparty/lib/x86_64',
    description='Path to Unitree SDK shared libraries'
  )
  declare_command_timeout = DeclareLaunchArgument(
    'command_timeout',
    default_value='0.1',
    description='Minimum time between bridge commands in seconds'
  )
  declare_max_x_linear_velocity = DeclareLaunchArgument(
    'max_x_linear_velocity',
    default_value='0.2',
    description='Safety clamp for x velocity in m/s'
  )
  declare_max_y_linear_velocity = DeclareLaunchArgument(
    'max_y_linear_velocity',
    default_value='0.15',
    description='Safety clamp for y velocity in m/s'
  )
  declare_max_angular_velocity = DeclareLaunchArgument(
    'max_angular_velocity',
    default_value='0.2',
    description='Safety clamp for yaw rate in rad/s'
  )

  start_local_planner = IncludeLaunchDescription(
    PythonLaunchDescriptionSource(os.path.join(
      get_package_share_directory('local_planner'), 'launch', 'local_planner.launch.py')
    ),
    launch_arguments={
      'robot_config': robot_config,
      'autonomyMode': autonomy_mode,
      'cameraOffsetZ': cameraOffsetZ,
      'goalX': vehicleX,
      'goalY': vehicleY,
    }.items()
  )

  start_terrain_analysis = IncludeLaunchDescription(
    PythonLaunchDescriptionSource(os.path.join(
        get_package_share_directory('terrain_analysis'), 'launch', 'terrain_analysis.launch.py')
    )
  )

  start_terrain_analysis_ext = IncludeLaunchDescription(
    FrontendLaunchDescriptionSource(os.path.join(
      get_package_share_directory('terrain_analysis_ext'), 'launch', 'terrain_analysis_ext.launch')
    ),
    launch_arguments={
      'checkTerrainConn': checkTerrainConn,
    }.items()
  )

  start_sensor_scan_generation = IncludeLaunchDescription(
    FrontendLaunchDescriptionSource(os.path.join(
      get_package_share_directory('sensor_scan_generation'), 'launch', 'sensor_scan_generation.launch')
    )
  )

  start_arise_slam = IncludeLaunchDescription(
    PythonLaunchDescriptionSource(os.path.join(
      get_package_share_directory('arise_slam_mid360'), 'launch', 'arize_slam.launch.py')
    ),
    launch_arguments={
      'config_file': slam_config_file,
      'robot_config': robot_config,
    }.items()
  )

  start_visualization_tools = IncludeLaunchDescription(
    FrontendLaunchDescriptionSource(os.path.join(
      get_package_share_directory('visualization_tools'), 'launch', 'visualization_tools.launch')
    ),
    launch_arguments={
      'world_name': world_name,
    }.items()
  )

  start_joy = Node(
    package='joy',
    executable='joy_node',
    name='ps3_joy',
    output='screen',
    parameters=[{
      'dev': "/dev/input/js0",
      'deadzone': 0.12,
      'autorepeat_rate': 0.0,
    }]
  )

  start_mid360 = IncludeLaunchDescription(
    PythonLaunchDescriptionSource(
      [get_package_share_directory('livox_ros_driver2'), '/launch_ROS2/msg_MID360_launch.py']),
  )

  start_g1_bridge = IncludeLaunchDescription(
    PythonLaunchDescriptionSource(os.path.join(
      get_package_share_directory('g1_controller'),
      'launch',
      'cmd_vel_to_g1.launch.py')
    ),
    launch_arguments={
      'network_interface': network_interface,
      'g1_loco_client_path': g1_loco_client_path,
      'unitree_sdk_lib_path': unitree_sdk_lib_path,
      'command_timeout': command_timeout,
      'max_x_linear_velocity': max_x_linear_velocity,
      'max_y_linear_velocity': max_y_linear_velocity,
      'max_angular_velocity': max_angular_velocity,
    }.items()
  )

  ld = LaunchDescription()

  ld.add_action(declare_world_name)
  ld.add_action(declare_cameraOffsetZ)
  ld.add_action(declare_vehicleX)
  ld.add_action(declare_vehicleY)
  ld.add_action(declare_checkTerrainConn)
  ld.add_action(declare_robot_config)
  ld.add_action(declare_autonomy_mode)
  ld.add_action(declare_slam_config_file)

  ld.add_action(declare_network_interface)
  ld.add_action(declare_g1_loco_client_path)
  ld.add_action(declare_unitree_sdk_lib_path)
  ld.add_action(declare_command_timeout)
  ld.add_action(declare_max_x_linear_velocity)
  ld.add_action(declare_max_y_linear_velocity)
  ld.add_action(declare_max_angular_velocity)

  ld.add_action(start_local_planner)
  ld.add_action(start_terrain_analysis)
  ld.add_action(start_terrain_analysis_ext)
  ld.add_action(start_sensor_scan_generation)
  ld.add_action(start_arise_slam)
  ld.add_action(start_visualization_tools)
  ld.add_action(start_joy)
  ld.add_action(start_mid360)
  ld.add_action(start_g1_bridge)

  return ld
