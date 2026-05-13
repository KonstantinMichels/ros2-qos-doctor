# ros2-qos-doctor

`ros2-qos-doctor` is an early MVP command line tool for diagnosing ROS 2 QoS incompatibilities between publishers and subscribers.

The first target platform is ROS 2 Jazzy on Ubuntu 24.04.

ROS 2 QoS settings are powerful, but mismatches can make a topic look mysteriously silent: a publisher and subscriber may both exist, yet DDS refuses to match them because one endpoint requests a policy the other endpoint does not offer. This is especially common when recording with rosbag2, using simulation time, bridging systems, or mixing sensor and state topics with different defaults.

Unlike `ros2 topic info -v`, this tool tries to interpret the endpoint QoS data, explain why communication may fail, and suggest a concrete fix.

## Build

From a ROS 2 workspace:

```bash
cd ~/ros2_qos_doctor_ws/src
git clone <repo-url> ros2-qos-doctor
cd ~/ros2_qos_doctor_ws
source /opt/ros/jazzy/setup.bash
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install
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

Scan all visible topics and report only detected QoS problems:

```bash
ros2 run ros2_qos_doctor qos_doctor --all
```

Also show topics without detected QoS problems:

```bash
ros2 run ros2_qos_doctor qos_doctor --all --show-compatible
```

Print rosbag2 QoS override suggestions for incompatible topics found by a
system scan:

```bash
ros2 run ros2_qos_doctor qos_doctor --all --rosbag2-yaml
```

Run tests:

```bash
colcon test --packages-select ros2_qos_doctor
colcon test-result --verbose
```

## Reproducible QoS Demos

The `ros2_qos_doctor` package includes small Python example nodes that
intentionally create QoS combinations for testing and documentation. Each demo
uses `std_msgs/msg/String` and can be run with `ros2 run`.

Use the nodes in these pairs:

| Demo | Publisher | Subscriber | Topic | Expected |
| --- | --- | --- | --- | --- |
| Reliability mismatch | `best_effort_publisher` | `reliable_subscriber` | `/qos_demo/reliability` | Incompatible |
| Reliability compatible | `reliable_publisher` | `best_effort_subscriber` | `/qos_demo/reliability_compatible` | Compatible |
| Durability mismatch | `volatile_publisher` | `transient_local_subscriber` | `/qos_demo/durability` | Incompatible |
| Durability compatible | `transient_local_publisher` | `volatile_subscriber` | `/qos_demo/durability_compatible` | Compatible |

For example, `best_effort_publisher` and `best_effort_subscriber` are not a
pair; they intentionally run on different topics for different demos.

Build the workspace:

```bash
cd ~/ros2_qos_doctor_ws
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install
source install/setup.bash
```

### Reliability Mismatch

This demo publishes with `BEST_EFFORT` reliability and subscribes with
`RELIABLE` reliability. It is incompatible because the subscriber requests
stronger delivery than the publisher offers.

Terminal 1:

```bash
ros2 run ros2_qos_doctor best_effort_publisher
```

Terminal 2:

```bash
ros2 run ros2_qos_doctor reliable_subscriber
```

Terminal 3:

```bash
ros2 run ros2_qos_doctor qos_doctor /qos_demo/reliability
```

Expected `ros2-qos-doctor` result:

```text
Compatibility:
  Incompatible

Problem:
  Reliability mismatch. The subscriber requests RELIABLE delivery, but the publisher only offers BEST_EFFORT delivery.

Suggested fix:
  Set the subscriber reliability to BEST_EFFORT.
```

### Reliability Compatible

This demo publishes with `RELIABLE` reliability and subscribes with
`BEST_EFFORT` reliability. It is compatible because a `BEST_EFFORT` subscriber
can communicate with a `RELIABLE` publisher.

Terminal 1:

```bash
ros2 run ros2_qos_doctor reliable_publisher
```

Terminal 2:

```bash
ros2 run ros2_qos_doctor best_effort_subscriber
```

Terminal 3:

```bash
ros2 run ros2_qos_doctor qos_doctor /qos_demo/reliability_compatible
```

Expected `ros2-qos-doctor` result:

```text
Compatibility:
  Compatible
```

## Scan All Topics

Use `--all` to scan the current ROS graph and report topics with detected QoS
incompatibilities:

```bash
ros2 run ros2_qos_doctor qos_doctor --all
```

By default, compatible topics are hidden so the report stays focused. Add
`--show-compatible` to include topics without detected QoS issues:

```bash
ros2 run ros2_qos_doctor qos_doctor --all --show-compatible
```

Add `--rosbag2-yaml` to include suggested rosbag2 QoS override snippets for
topics with detected incompatibilities:

```bash
ros2 run ros2_qos_doctor qos_doctor --all --rosbag2-yaml
```

Example with the reliability mismatch demo:

Terminal 1:

```bash
ros2 run ros2_qos_doctor best_effort_publisher
```

Terminal 2:

```bash
ros2 run ros2_qos_doctor reliable_subscriber
```

Terminal 3:

```bash
ros2 run ros2_qos_doctor qos_doctor --all
```

Expected result:

```text
ros2-qos-doctor system scan

Scanned topics: 3
Topics with publishers and subscribers: 1
Topics with QoS issues: 1

❌ /qos_demo/reliability
   Reliability mismatch:
   Publisher /best_effort_publisher offers BEST_EFFORT
   Subscriber /reliable_subscriber requests RELIABLE

   Suggested fix:
   Set the subscriber reliability to BEST_EFFORT.
```

### Durability Mismatch

This demo publishes with `VOLATILE` durability and subscribes with
`TRANSIENT_LOCAL` durability. It is incompatible because the subscriber requests
stored samples, but the publisher only offers volatile samples.

Terminal 1:

```bash
ros2 run ros2_qos_doctor volatile_publisher
```

Terminal 2:

```bash
ros2 run ros2_qos_doctor transient_local_subscriber
```

Terminal 3:

```bash
ros2 run ros2_qos_doctor qos_doctor /qos_demo/durability
```

Expected `ros2-qos-doctor` result:

```text
Compatibility:
  Incompatible

Problem:
  Durability mismatch. The subscriber requests TRANSIENT_LOCAL durability, but the publisher only offers VOLATILE durability.

Suggested fix:
  Set the subscriber durability to VOLATILE.
```

### Durability Compatible

This demo publishes with `TRANSIENT_LOCAL` durability and subscribes with
`VOLATILE` durability. It is compatible because a `VOLATILE` subscriber can
communicate with a `TRANSIENT_LOCAL` publisher.

Terminal 1:

```bash
ros2 run ros2_qos_doctor transient_local_publisher
```

Terminal 2:

```bash
ros2 run ros2_qos_doctor volatile_subscriber
```

Terminal 3:

```bash
ros2 run ros2_qos_doctor qos_doctor /qos_demo/durability_compatible
```

Expected `ros2-qos-doctor` result:

```text
Compatibility:
  Compatible
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

- JSON output
- Better rosbag2 integration
- Special handling for `/tf`, `/tf_static`, `/clock`, and sensor topics
- RMW implementation information

## License

MIT
