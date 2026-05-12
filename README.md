# ros2-qos-doctor

`ros2-qos-doctor` is an early MVP command line tool for diagnosing ROS 2 QoS incompatibilities between publishers and subscribers.

The first target platform is ROS 2 Jazzy on Ubuntu 24.04.

ROS 2 QoS settings are powerful, but mismatches can make a topic look mysteriously silent: a publisher and subscriber may both exist, yet DDS refuses to match them because one endpoint requests a policy the other endpoint does not offer. This is especially common when recording with rosbag2, using simulation time, bridging systems, or mixing sensor and state topics with different defaults.

Unlike `ros2 topic info -v`, this tool tries to interpret the endpoint QoS data, explain why communication may fail, and suggest a concrete fix.

## Build

From a ROS 2 workspace:

```bash
cd ~/ros_ws/src
git clone <repo-url> ros2-qos-doctor
cd ~/ros_ws
rosdep install --from-paths src --ignore-src -r -y
colcon build --packages-select ros2_qos_doctor
source install/setup.bash
```

## Usage

Inspect one topic:

```bash
ros2 run ros2_qos_doctor qos_doctor /tf
```

Print a rosbag2 QoS override suggestion when an incompatibility is detected:

```bash
ros2 run ros2_qos_doctor qos_doctor /tf --rosbag2-yaml
```

Run tests:

```bash
colcon test --packages-select ros2_qos_doctor
colcon test-result --verbose
```

## Example Output

```text
ros2-qos-doctor

Topic: /tf

Publishers:
  - node: /carla_native_tf_bridge
    type: tf2_msgs/msg/TFMessage
    reliability: reliable
    durability: volatile
    history: keep_last
    depth: 100

Subscribers:
  - node: /rosbag2_recorder
    type: tf2_msgs/msg/TFMessage
    reliability: reliable
    durability: transient_local
    history: keep_last
    depth: 100

Compatibility:
  Incompatible

Problem:
  Durability mismatch.
  The subscriber requests TRANSIENT_LOCAL durability, but the publisher only offers VOLATILE durability.

Suggested fix:
  Set the subscriber durability to VOLATILE.

rosbag2 override suggestion:
  /tf:
    reliability: reliable
    durability: volatile
    history: keep_last
    depth: 100
```

## MVP Scope

The MVP checks the most common hard incompatibilities:

- Reliability: `BEST_EFFORT` publisher with `RELIABLE` subscriber.
- Durability: `VOLATILE` publisher with `TRANSIENT_LOCAL` subscriber.

Other QoS policies are displayed but not yet interpreted.

## Planned Features

- `--all` system scan
- JSON output
- Better rosbag2 integration
- Special handling for `/tf`, `/tf_static`, `/clock`, and sensor topics
- RMW implementation information

## License

MIT
