################################################################################
# ZHAW INIT
# Description:  Dockerfile to create the Base CPU Docker image
# Authors:      Mark Straub and Leonardo Militano
# Date:         2023-11-01
################################################################################

# Base image
FROM ros:humble-ros-base AS BASE

ENV ROS_VERSION=2

RUN mkdir -p /root/colcon_ws/src

# Install dependencies
RUN apt-get update && \
    apt-get install -y python3-colcon-bash python3-colcon-common-extensions python3-rosdep python3-vcstool ros-humble-cyclonedds ros-humble-rmw-cyclonedds-cpp iproute2 nano bmon

# Install ros-foxglove-bridge
# https://github.com/foxglove/ros-foxglove-bridge
# RUN cd /root/colcon_ws/src && \
#     git clone -b ros2 https://github.com/foxglove/ros-foxglove-bridge.git src/ros-foxglove-bridge && \
#     apt update && \
#     rosdep update && \
#     rosdep install --ignore-src --default-yes --from-path src

RUN apt-get update && \
    apt-get install -y ros-$ROS_DISTRO-foxglove-bridge


RUN bash -c "cd /root/colcon_ws && \
    source /opt/ros/humble/setup.bash && \
    colcon build --event-handlers console_direct+ --symlink-install"

ENV RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
ENV CYCLONEDDS_URI=file:///root/cyclonedds.xml

ADD ./cyclonedds.xml /root/cyclonedds.xml
