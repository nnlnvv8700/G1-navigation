import os
import yaml
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

def _load_sensor_offsets(local_planner_share, robot_config):
    sensor_offsets = {
        'sensorOffsetX': 0.0,
        'sensorOffsetY': 0.0,
        'sensorOffsetZ': 0.0
    }

    try:
        robot_config_path = os.path.join(local_planner_share, 'config', robot_config + '.yaml')
        with open(robot_config_path, 'r') as file:
            config_data = yaml.safe_load(file)

        # Extract sensor offsets from sensorMountingOffsets/ros__parameters section
        if 'sensorMountingOffsets' in config_data and 'ros__parameters' in config_data['sensorMountingOffsets']:
            mounting_offsets = config_data['sensorMountingOffsets']['ros__parameters']
            for key in sensor_offsets.keys():
                if key in mounting_offsets:
                    sensor_offsets[key] = mounting_offsets[key]
    except Exception as e:
        print(f"Warning: Could not read robot config from {robot_config}.yaml, using defaults: {e}")

    return sensor_offsets


def _launch_setup(context):
    local_planner_share = get_package_share_directory('local_planner')
    config_name = LaunchConfiguration('config').perform(context)
    robot_config = LaunchConfiguration('robot_config').perform(context)
    two_way_drive = LaunchConfiguration('twoWayDrive').perform(context)
    autonomy_mode = LaunchConfiguration('autonomyMode').perform(context)
    joy_to_speed_delay = LaunchConfiguration('joyToSpeedDelay').perform(context)
    goal_x = LaunchConfiguration('goalX').perform(context)
    goal_y = LaunchConfiguration('goalY').perform(context)
    camera_offset_z = LaunchConfiguration('cameraOffsetZ').perform(context)
    sensor_offsets = _load_sensor_offsets(local_planner_share, robot_config)

    config_file = os.path.join(local_planner_share, 'config', f'{config_name}.yaml')
    robot_config_file = os.path.join(local_planner_share, 'config', f'{robot_config}.yaml')

    # LocalPlanner node
    localPlanner_node = Node(
        package='local_planner',
        executable='localPlanner',
        name='localPlanner',
        output='screen',
        parameters=[
            {
                'pathFolder': os.path.join(local_planner_share, 'paths'),
                'twoWayDrive': True,
                'laserVoxelSize': 0.05,
                'terrainVoxelSize': 0.2,
                'useTerrainAnalysis': True,
                'checkObstacle': True,
                'checkRotObstacle': False,
                'adjacentRange': 3.5,
                'obstacleHeightThre': 0.1,
                'groundHeightThre': 0.1,
                'costHeightThre1': 0.1,
                'costHeightThre2': 0.05,
                'useCost': False,
                'slowPathNumThre': 5,
                'slowGroupNumThre': 1,
                'pointPerPathThre': 2,
                'minRelZ': -0.4,
                'maxRelZ': 0.3,
                'dirWeight': 0.02,
                'dirThre': 90.0,
                'dirToVehicle': False,
                'pathScale': 0.875,
                'minPathScale': 0.675,
                'pathScaleStep': 0.1,
                'pathScaleBySpeed': True,
                'minPathRange': 0.8,
                'pathRangeStep': 0.6,
                'pathRangeBySpeed': True,
                'pathCropByGoal': True,
                'autonomyMode': autonomy_mode.lower() == 'true',
                'joyToSpeedDelay': float(joy_to_speed_delay),
                'joyToCheckObstacleDelay': 5.0,
                'freezeAng': 90.0,
                'freezeTime': 0.0,
                'goalX': float(goal_x),
                'goalY': float(goal_y),
            },
            config_file,
            robot_config_file,
        ]
    )

    # PathFollower node
    pathFollower_node = Node(
        package='local_planner',
        executable='pathFollower',
        name='pathFollower',
        output='screen',
        parameters=[
            {
                'pubSkipNum': 1,
                'twoWayDrive': two_way_drive.lower() == 'true',
                'switchTimeThre': 1.0,
                'useInclRateToSlow': False,
                'inclRateThre': 120.0,
                'slowRate1': 0.25,
                'slowRate2': 0.5,
                'slowRate3': 0.75,
                'slowTime1': 2.0,
                'slowTime2': 2.0,
                'useInclToStop': False,
                'inclThre': 45.0,
                'stopTime': 5.0,
                'noRotAtStop': False,
                'noRotAtGoal': False,
                'autonomyMode': autonomy_mode.lower() == 'true',
                'joyToSpeedDelay': float(joy_to_speed_delay),
            },
            config_file,
            robot_config_file,
        ]
    )

    # Static transform publishers with sensor offsets from config
    vehicleTransPublisher_node = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='vehicleTransPublisher',
        arguments=[
            str(-sensor_offsets['sensorOffsetX']),
            str(-sensor_offsets['sensorOffsetY']),
            str(-sensor_offsets['sensorOffsetZ']),
            '0', '0', '0',
            '/sensor',
            '/vehicle'
        ]
    )

    sensorTransPublisher_node = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='sensorTransPublisher',
        arguments=[
            '0', '0', LaunchConfiguration('cameraOffsetZ'),
            '-1.5707963', '0', '-1.5707963',
            '/sensor', '/camera'
        ]
    )

    return [
        localPlanner_node,
        pathFollower_node,
        vehicleTransPublisher_node,
        sensorTransPublisher_node,
    ]


def generate_launch_description():
    robot_config_env = os.environ.get('ROBOT_CONFIG_PATH', 'unitree/unitree_g1')

    return LaunchDescription([
        DeclareLaunchArgument(
            'config',
            default_value='omniDir',
            description='omniDir: if with mecanum wheels, standard: if with standard wheels'
        ),
        DeclareLaunchArgument(
            'robot_config',
            default_value=robot_config_env,
            description='Robot-specific config file (without .yaml extension)'
        ),
        DeclareLaunchArgument(
            'twoWayDrive',
            default_value='false'
        ),
        DeclareLaunchArgument(
            'autonomyMode',
            default_value='true'
        ),
        DeclareLaunchArgument(
            'joyToSpeedDelay',
            default_value='2.0'
        ),
        DeclareLaunchArgument(
            'goalX',
            default_value='0.0'
        ),
        DeclareLaunchArgument(
            'goalY',
            default_value='0.0'
        ),
        DeclareLaunchArgument(
            'cameraOffsetZ',
            default_value='0.0'
        ),
        DeclareLaunchArgument(
            'realRobot',
            default_value='false',
            description='Deprecated compatibility argument; Unitree WebRTC control ignores this value.'
        ),
        DeclareLaunchArgument(
            'sensorOffsetX',
            default_value='0.0',
            description='Deprecated compatibility argument; sensor offsets now come from robot_config.'
        ),
        DeclareLaunchArgument(
            'sensorOffsetY',
            default_value='0.0',
            description='Deprecated compatibility argument; sensor offsets now come from robot_config.'
        ),
        OpaqueFunction(function=_launch_setup),
    ])
