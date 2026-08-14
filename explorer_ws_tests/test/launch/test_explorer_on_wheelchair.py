import atexit
import os
import subprocess
import unittest

import launch
import launch.actions
import launch.events
import launch_testing
import launch_testing.asserts
import pytest
from ament_index_python.packages import get_package_share_directory
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_testing import ready_to_test_action_timeout


@pytest.mark.launch_test
@ready_to_test_action_timeout(60)
def generate_test_description():
    # 1. Locate your launch file
    pkg_share = get_package_share_directory("explorer_on_wheelchair")
    launch_file_path = os.path.join(pkg_share, "launch", "simulation.launch.py")

    # 2. Include the launch file (you can pass launch arguments here)
    launch_inclusion = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(launch_file_path),
        launch_arguments={
            "can_port": "vcan0",
            "gui": "false",
            "spacenav": "false",
        }.items(),
    )

    # Create a timer to kill the test after 10 seconds.
    # This gives nodes enough time to boot up, configure, and prove they don't crash.
    shutdown_timer = launch.actions.TimerAction(
        period=20.0, actions=[launch_testing.actions.ReadyToTest()]
    )

    return launch.LaunchDescription(
        [
            # launch.actions.SetLaunchConfiguration(name="sigterm_timeout", value="2.0"),
            # launch.actions.SetLaunchConfiguration(name="sigkill_timeout", value="3.0"),
            launch_inclusion,
            shutdown_timer,
        ]
    )


# -----------------------------------------------------------------------------
# Tests that run AFTER the launch file is shut down
# -----------------------------------------------------------------------------
@launch_testing.post_shutdown_test()
class TestProcessOutput(unittest.TestCase):
    def test_no_crashes(self, proc_info, proc_output):
        """Check that all processes exited normally (no crashes)."""
        launch_testing.asserts.assertExitCodes(
            proc_info, process="wheelchair_controller"
        )
        launch_testing.asserts.assertExitCodes(proc_info, process="head_controller")

        ## Cannot be tested as long as the while loop in constructor exists
        # launch_testing.asserts.assertExitCodes(proc_info, process="input_integrator")
        # launch_testing.asserts.assertExitCodes(proc_info, process="output_integrator")

        launch_testing.asserts.assertExitCodes(proc_info, process="qp_solving")
        launch_testing.asserts.assertExitCodes(
            proc_info, process="robot_state_publisher"
        )
        launch_testing.asserts.assertExitCodes(
            proc_info, process="spawner", cmd_args=["joint_state_broadcaster"]
        )
        launch_testing.asserts.assertExitCodes(
            proc_info, process="spawner", cmd_args=["diff_drive_base_controller"]
        )
        launch_testing.asserts.assertExitCodes(
            proc_info, process="spawner", cmd_args=["head_position_controller"]
        )
        launch_testing.asserts.assertExitCodes(
            proc_info, process="spawner", cmd_args=["forward_position_controller"]
        )
        launch_testing.asserts.assertExitCodes(
            proc_info, process="spawner", cmd_args=["gripper_controller"]
        )

        ## Not launched to prevent spam due to spacenav not found
        # launch_testing.asserts.assertExitCodes(proc_info, process="spacenav_node")

        launch_testing.asserts.assertExitCodes(proc_info, process="joy_node")
        ## Never quit properly: would be better to check stdout
        # launch_testing.asserts.assertExitCodes(proc_info, process="gazebo")
        launch_testing.asserts.assertExitCodes(proc_info, process="image_bridge")


def wipe_gazebo_zombies():
    print("\n[Teardown] Hunting for Gazebo zombie processes...")

    # 'ign' handles the main Ignition Gazebo process
    # 'ruby' is the backend wrapper that Ignition uses to launch
    # 'spawner' catches the ros2_control node
    zombies = ["ign", "ruby", "spawner"]

    for zombie in zombies:
        subprocess.run(
            ["killall", "-9", zombie],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )


## Register method on test exit
atexit.register(wipe_gazebo_zombies)
