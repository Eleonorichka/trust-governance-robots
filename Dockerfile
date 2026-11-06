FROM ros:humble

# Install dependencies for Trust-Arch
RUN apt-get update && apt-get install -y \
    curl \
    jq \
    python3-flask \
    wget \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install matplotlib plotly "kaleido==0.2.1" scipy pandas numpy

# Source ROS 2 setup in .bashrc
RUN echo "source /opt/ros/humble/setup.bash" >> /root/.bashrc
