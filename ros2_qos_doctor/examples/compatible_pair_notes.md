# ros2-qos-doctor Example Nodes

These nodes intentionally create small QoS scenarios for testing and documenting
`ros2-qos-doctor`.

The compatible examples are just as important as the mismatch examples:

- A `BEST_EFFORT` subscriber can communicate with a `RELIABLE` publisher.
- A `VOLATILE` subscriber can communicate with a `TRANSIENT_LOCAL` publisher.

The mismatch examples demonstrate common cases where endpoints exist in the ROS
graph but DDS does not match them because the subscriber requests a policy that
the publisher does not offer.
