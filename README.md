# Pipeline Monitoring Setup Guide

## Step 1: Clone the repository
Open a terminal and run:
```bash
cd ~
git clone https://github.com/agent000008/pipeline_monitoring.git
cd pipeline_monitoring
```

## Step 2: Install ROS Noetic (if not already installed)

For **Ubuntu 20.04**:
```bash
sudo apt update
sudo apt install ros-noetic-desktop-full -y
```

Add ROS to PATH:

```bash
echo "source /opt/ros/noetic/setup.bash" >> ~/.bashrc
source ~/.bashrc
```

## Step 3: Install Python dependencies

```bash
pip3 install pyyaml numpy
```

## Step 4: Create a ROS workspace

```bash
mkdir -p ~/catkin_ws/src
cd ~/catkin_ws/src
ln -s ~/pipeline_monitoring .
cd ~/catkin_ws
catkin_make
source devel/setup.bash
```

## Step 5: Install Clover Simulations

```bash
cd ~/catkin_ws/src
git clone https://github.com/CopterExpress/clover.git
cd ~/catkin_ws
catkin_make
```

Add paths to Gazebo models:

```bash
echo 'export GAZEBO_MODEL_PATH=$GAZEBO_MODEL_PATH:/catkin_ws/src/clover/clover_description/models' >> ~/.bashrc
source ~/.bashrc
```

##  Step 6: Start the System (3 Terminals)
### Terminal 1: Start ROS Master

```bash
cd ~/catkin_ws
source devel/setup.bash
roscore
```

### Terminal 2: Start Gazebo with the patch Rendering

```bash
cd ~/catkin_ws
source devel/setup.bash
export LIBGL_ALWAYS_SOFTWARE=1
rosrun gazebo_ros gazebo --verbose
```

### Terminal 3: Generating pipeline and markers

```bash
cd ~/catkin_ws
source devel/setup.bash
sleep 15
rosrun pipeline_monitoring generate_world_fixed.py
sleep 5
rosrun pipeline_monitoring create_aruco_grid.py
```
