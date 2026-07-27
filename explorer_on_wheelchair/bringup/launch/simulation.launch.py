# Copyright 2021 Open Source Robotics Foundation, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os

from ament_index_python.packages import (
    get_package_share_directory,
)
from explorer_bringup.launch.optional_parameters import declare_parameter_spacenav
from launch import LaunchDescription
from launch.actions import SetLaunchConfiguration
from launch.conditions import IfCondition
from launch.substitutions import (
    Command,
    FindExecutable,
    PathJoinSubstitution,
)
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

from build.explorer_bringup.ament_cmake_python.explorer_bringup.explorer_bringup.launch.optional_parameters import (
    declare_parameter_input_device,
)
from explorer_stack.explorer_bringup.explorer_bringup.launch.controller_manager_spawner import (
    declare_node_forward_position_controller_spawner,
    declare_node_gripper_controller_spawner,
)
from explorer_stack.explorer_bringup.explorer_bringup.launch.hardware_parameters import (
    declare_hardware_argument_list,
)
from explorer_stack.explorer_bringup.explorer_bringup.launch.optional import (
    declare_joy_node,
    declare_spacenav_node_group,
)
from explorer_stack.explorer_bringup.explorer_bringup.launch.shared import (
    declare_input_integrator_node,
    declare_output_integrator_node,
)
from explorer_stack.explorer_bringup.explorer_bringup.launch.shared_parameters import (
    CONTROLLER_CONFIG_TYPE,
    get_parameter_can_port,
    get_parameter_gui,
    get_parameter_host_id,
    get_parameter_simulation,
    get_parameter_use_poc2,
)
from explorer_stack.explorer_bringup.explorer_bringup.launch.simulation import (
    declare_simulation_node_group,
)
from explorer_stack.explorer_bringup.explorer_bringup.launch.simulation_parameters import (
    declare_simulation_argument_list,
)


def _declare_arguments(robot_controller_config: CONTROLLER_CONFIG_TYPE):
    return [
        *declare_simulation_argument_list(
            robot_controller_config=robot_controller_config
        ),
        *declare_hardware_argument_list(
            robot_controller_config=robot_controller_config
        ),
        declare_parameter_spacenav(),
        declare_parameter_input_device(),
    ]


def generate_launch_description():
    # Use default robot controller config (forward_position_controller)
    robot_controller_config = "controller"
    controller_position_topic_name = "/forward_position_controller/commands"

    # Initialize Arguments
    declared_arguments = _declare_arguments(
        robot_controller_config=robot_controller_config
    )

    world = os.path.join(
        get_package_share_directory("explorer_on_wheelchair"),
        "description/worlds",
        "empty_world.world",
    )

    input_integrator_node = declare_input_integrator_node()
    output_integrator_node = declare_output_integrator_node(
        controller_position_topic_name=controller_position_topic_name
    )

    diff_drive_base_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=[
            "diff_drive_base_controller",
            "--controller-manager",
            "/controller_manager",
        ],
    )

    head_position_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=[
            "head_position_controller",
            "--controller-manager",
            "/controller_manager",
        ],
    )

    robot_controller_list = [
        declare_node_forward_position_controller_spawner(),
        declare_node_gripper_controller_spawner(),
        diff_drive_base_controller_spawner,
        head_position_controller_spawner,
    ]

    robot_simulation = declare_simulation_node_group(
        robot_controller_list=robot_controller_list,
        launch_qp_solving=True,
        qp_solving_post_start_list=[
            input_integrator_node,
            output_integrator_node,
        ],
        controller_position_topic_name=controller_position_topic_name,
    )

    spacenav_node_group = declare_spacenav_node_group()

    joy_node = declare_joy_node()

    wheelchair_controller_node = Node(
        package="ros2_control_wheelchair",
        executable="wheelchair_controller",
        output="screen",
    )

    head_controller_node = Node(
        package="ros2_control_wheelchair",
        executable="head_controller",
        output="screen",
    )

    # Declare GUI controller node
    gui_control_node = Node(
        package="explorer_user_interfaces",
        executable="rqt_jointcontrol",
        condition=IfCondition(get_parameter_gui()),
    )

    # Bridge
    image_bridge = Node(
        package="ros_gz_image",
        executable="image_bridge",
        arguments=[
            "camera",
            "depth_camera",
            "rgbd_camera/image",
            "rgbd_camera/depth_image",
        ],
        output="screen",
    )

    nodes = [
        SetLaunchConfiguration(
            name="simulation",
            value="True",
        ),
        SetLaunchConfiguration(
            name="robot_description_param",
            value=Command(
                [
                    PathJoinSubstitution([FindExecutable(name="xacro")]),
                    " ",
                    PathJoinSubstitution(
                        [
                            FindPackageShare("explorer_on_wheelchair"),
                            "description/urdf",
                            "simulation.urdf.xacro",
                        ]
                    ),
                    " can_port:=",
                    get_parameter_can_port(),
                    " host_id:=",
                    get_parameter_host_id(),
                    " simulation:=",
                    get_parameter_simulation(),
                    " use_POC2:=",
                    get_parameter_use_poc2(),
                    " robot_controller_config:=",
                    robot_controller_config,
                ]
            ),
        ),
        SetLaunchConfiguration(
            name="robot_semantic_srdf",
            value=Command(
                [
                    PathJoinSubstitution([FindExecutable(name="xacro")]),
                    " ",
                    PathJoinSubstitution(
                        [
                            FindPackageShare("explorer_on_wheelchair"),
                            "description/urdf",
                            "explorer.srdf",
                        ]
                    ),
                    " ",
                ]
            ),
        ),
        robot_simulation,
        # spacenav_node_group,
        joy_node,
        gui_control_node,
        image_bridge,
        wheelchair_controller_node,
        head_controller_node,
    ]

    return LaunchDescription([*declared_arguments, *nodes])
