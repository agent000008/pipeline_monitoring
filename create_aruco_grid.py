#!/usr/bin/env python3
import rospy
from geometry_msgs.msg import Pose, Point, Quaternion
from gazebo_msgs.srv import SpawnModel
from tf.transformations import quaternion_from_euler
import yaml
import os

rospy.init_node('aruco_grid_generator')
rospy.wait_for_service('/gazebo/spawn_sdf_model')
spawn = rospy.ServiceProxy('/gazebo/spawn_sdf_model', SpawnModel)

print("Creating 7x7 ArUco marker grid...")

marker_size = 0.33
spacing = 0.5
z_height = 0.0
marker_id = 0

aruco_map = {'aruco_map': {'markers': [], 'length_units': 'm'}}

for i in range(7):
    for j in range(7):
        x = i * (marker_size + spacing)
        y = j * (marker_size + spacing)
        
        pose = Pose()
        pose.position = Point(x, y, z_height)
        quaternion = quaternion_from_euler(0, 0, 0)
        pose.orientation = Quaternion(*quaternion)
        
        sdf = f"""<?xml version="1.0"?>
<sdf version="1.6">
  <model name="aruco_{marker_id}">
    <static>true</static>
    <link name="link">
      <visual name="visual">
        <geometry>
          <box>
            <size>{marker_size} {marker_size} 0.01</size>
          </box>
        </geometry>
        <material>
          <ambient>0.1 0.1 0.1 1</ambient>
          <diffuse>0.3 0.3 0.3 1</diffuse>
        </material>
      </visual>
    </link>
  </model>
</sdf>"""
        
        try:
            spawn(f"aruco_{marker_id}", sdf, "", pose, "world")
            print(f"ArUco marker {marker_id} at ({x:.2f}, {y:.2f})")
            
            aruco_map['aruco_map']['markers'].append({
                'id': marker_id,
                'length': marker_size,
                'x': x,
                'y': y,
                'z': z_height,
                'roll': 0.0,
                'pitch': 0.0,
                'yaw': 0.0
            })
        except Exception as e:
            print(f"Error marker {marker_id}: {e}")
        
        marker_id += 1

map_path = os.path.expanduser('~/aruco_map_7x7.yaml')
with open(map_path, 'w') as f:
    yaml.dump(aruco_map, f, default_flow_style=False)

print(f"Created {marker_id} ArUco markers")
print(f"Map saved to {map_path}")
