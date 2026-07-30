cmake_minimum_required(VERSION 3.8)
project(explorer_ws_tests)

find_package(ament_cmake REQUIRED)

if(BUILD_TESTING)
  find_package(ament_cmake_ros REQUIRED)
  find_package(ament_cmake_gtest REQUIRED)
  find_package(ament_cmake_pytest REQUIRED)
  find_package(launch_testing_ament_cmake REQUIRED)

  ## Helper function
  function(add_ros_isolated_launch_test path)
    set(RUNNER "${ament_cmake_ros_DIR}/run_test_isolated.py")
    add_launch_test("${path}" RUNNER "${RUNNER}" ${ARGN})
  endfunction()

  ## INTEGRATION TESTS

  #ament_add_gtest(test_service_responses test/integration/test_service_responses.cpp)
  #target_link_libraries(test_service_responses my_package_lib)
  # (Integration tests usually need rclcpp linked as well)
  #ament_target_dependencies(test_service_responses rclcpp)

  ## LAUNCH & E2E TESTS
  add_ros_isolated_launch_test(test/launch/test_explorer_on_wheelchair.py)
  add_ros_isolated_launch_test(test/launch/test_explorer_mode_0_with_qontrol_controller.py)
  add_ros_isolated_launch_test(test/launch/test_explorer_cartesian_control_with_qontrol_controller.py)
  
endif()

ament_package()