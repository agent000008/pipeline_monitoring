#!/usr/bin/env python3
import rospy
import random
import math
from geometry_msgs.msg import Pose, Point, Quaternion
from gazebo_msgs.srv import SpawnModel
from tf.transformations import quaternion_from_euler
import yaml
import os

rospy.init_node('pipeline_generator_fixed')
rospy.wait_for_service('/gazebo/spawn_sdf_model')
spawn = rospy.ServiceProxy('/gazebo/spawn_sdf_model', SpawnModel)

ARUCO_FIELD_SIZE = 7.0
ARUCO_MIN_X = -ARUCO_FIELD_SIZE/2
ARUCO_MAX_X = ARUCO_FIELD_SIZE/2
ARUCO_MIN_Y = -ARUCO_FIELD_SIZE/2
ARUCO_MAX_Y = ARUCO_FIELD_SIZE/2

main_pipe_start = Point(1.0, 1.0, 0.0)
num_taps = 5
min_tap_distance = 0.75

print("Pipeline Generation")
print(f"ArUco field: {ARUCO_FIELD_SIZE}x{ARUCO_FIELD_SIZE}m")
print(f"Start point: ({main_pipe_start.x}, {main_pipe_start.y})")
print(f"Taps: {num_taps} with {min_tap_distance}m spacing")

def calculate_max_length_at_angle(angle):
    max_length_x = float('inf')
    max_length_y = float('inf')
    
    if math.cos(angle) > 0.001:
        max_length_x = (ARUCO_MAX_X - main_pipe_start.x) / math.cos(angle)
    elif math.cos(angle) < -0.001:
        max_length_x = (main_pipe_start.x - ARUCO_MIN_X) / abs(math.cos(angle))
    
    if math.sin(angle) > 0.001:
        max_length_y = (ARUCO_MAX_Y - main_pipe_start.y) / math.sin(angle)
    elif math.sin(angle) < -0.001:
        max_length_y = (main_pipe_start.y - ARUCO_MIN_Y) / abs(math.sin(angle))
    
    return min(max_length_x, max_length_y)

max_bend_angle = math.radians(30)
best_angle = 0
best_length = 0

angles_to_test = []
for deg in range(-30, 31, 5):
    angles_to_test.append(math.radians(deg))

angles_to_test.append(0)
angles_to_test.append(math.radians(45))

for angle in angles_to_test:
    max_len = calculate_max_length_at_angle(angle)
    if max_len > best_length and max_len < float('inf'):
        best_length = max_len
        best_angle = angle

print(f"Maximum possible length: {best_length:.2f}m")
print(f"Best angle: {math.degrees(best_angle):.1f} deg")

if best_length < 5.0:
    print(f"ERROR: Maximum length {best_length:.2f}m is less than minimum 5m")
    print("From point (1,1) in 7x7 field, maximum is ~6.5m")
    print("Trying to find working configuration...")
    
    for angle in [0, math.radians(15), math.radians(-15), math.radians(30), math.radians(-30)]:
        max_len = calculate_max_length_at_angle(angle)
        if max_len >= 5.0:
            best_angle = angle
            best_length = max_len
            print(f"Found: angle {math.degrees(angle):.1f} deg, length {max_len:.2f}m")
            break

if best_length < 5.0:
    print("Cannot create pipe 5-10m. Using maximum possible.")
    target_length = best_length
else:
    target_length = random.uniform(5.5, min(best_length, 9.5))

pipe_bend_angle = best_angle
main_pipe_length = target_length

end_x = main_pipe_start.x + main_pipe_length * math.cos(pipe_bend_angle)
end_y = main_pipe_start.y + main_pipe_length * math.sin(pipe_bend_angle)

end_x = max(ARUCO_MIN_X, min(ARUCO_MAX_X, end_x))
end_y = max(ARUCO_MIN_Y, min(ARUCO_MAX_Y, end_y))
main_pipe_end = Point(end_x, end_y, 0.0)

actual_length = math.sqrt((end_x - main_pipe_start.x)**2 + (end_y - main_pipe_start.y)**2)
main_pipe_length = actual_length

print(f"Pipe length: {main_pipe_length:.2f}m")
print(f"Angle: {math.degrees(pipe_bend_angle):.1f} deg")
print(f"Start: ({main_pipe_start.x:.2f}, {main_pipe_start.y:.2f})")
print(f"End: ({main_pipe_end.x:.2f}, {main_pipe_end.y:.2f})")

def create_horizontal_cylinder(name, radius, length, color="0.3 0.3 0.8 1"):
    return f"""<?xml version="1.0"?>
<sdf version="1.6">
  <model name="{name}">
    <static>true</static>
    <link name="link">
      <visual name="visual">
        <geometry>
          <cylinder>
            <radius>{radius}</radius>
            <length>{length}</length>
          </cylinder>
        </geometry>
        <pose>0 0 0 0 1.5708 0</pose>
        <material>
          <ambient>{color}</ambient>
          <diffuse>{color}</diffuse>
        </material>
      </visual>
      <collision name="collision">
        <geometry>
          <cylinder>
            <radius>{radius}</radius>
            <length>{length}</length>
          </cylinder>
        </geometry>
        <pose>0 0 0 0 1.5708 0</pose>
      </collision>
    </link>
  </model>
</sdf>"""

def generate_tap_positions(pipe_start, pipe_end, num_taps=5, min_spacing=0.75):
    positions = []
    
    dx = pipe_end.x - pipe_start.x
    dy = pipe_end.y - pipe_start.y
    pipe_length = math.sqrt(dx*dx + dy*dy)
    
    required_length = (num_taps - 1) * min_spacing
    
    if pipe_length >= required_length:
        spacing = min_spacing
        start_offset = (pipe_length - required_length) / 2
    else:
        spacing = pipe_length / (num_taps + 1)
        start_offset = spacing
        print(f"Pipe too short for {min_spacing}m spacing. Using {spacing:.2f}m")
    
    for i in range(num_taps):
        t = (start_offset + i * spacing) / pipe_length
        if t < 0 or t > 1:
            continue
            
        x = pipe_start.x + t * dx
        y = pipe_start.y + t * dy
        z = 0.0
        
        positions.append(Point(x, y, z))
    
    return positions, spacing

mid_x = (main_pipe_start.x + main_pipe_end.x) / 2
mid_y = (main_pipe_start.y + main_pipe_end.y) / 2

pose = Pose()
pose.position = Point(mid_x, mid_y, 0.0)
quaternion = quaternion_from_euler(0, 0, pipe_bend_angle)
pose.orientation = Quaternion(*quaternion)

sdf_main = create_horizontal_cylinder("main_pipeline", 0.1, main_pipe_length, "0.3 0.3 0.8 1")

try:
    spawn("main_pipeline", sdf_main, "", pose, "world")
    print(f"Main pipe spawned: {main_pipe_length:.2f}m")
except Exception as e:
    print(f"Error: {e}")
    exit()

print(f"Generating {num_taps} taps...")
tap_positions, actual_spacing = generate_tap_positions(main_pipe_start, main_pipe_end, num_taps, min_tap_distance)
created_taps = []

for i, pos in enumerate(tap_positions):
    tap_angle = pipe_bend_angle + math.radians(90)
    tap_length = random.uniform(0.5, 1.5)
    
    tap_pose = Pose()
    tap_pose.position = Point(pos.x, pos.y, 0.0)
    quaternion = quaternion_from_euler(0, 0, tap_angle)
    tap_pose.orientation = Quaternion(*quaternion)
    
    tap_sdf = f"""<?xml version="1.0"?>
<sdf version="1.6">
  <model name="tap_{i}">
    <static>true</static>
    <link name="link">
      <visual name="visual">
        <geometry>
          <cylinder>
            <radius>0.05</radius>
            <length>{tap_length}</length>
          </cylinder>
        </geometry>
        <pose>{tap_length/2} 0 0 0 1.5708 0</pose>
        <material>
          <ambient>0.8 0.3 0.3 1</ambient>
          <diffuse>0.8 0.3 0.3 1</diffuse>
        </material>
      </visual>
      <collision name="collision">
        <geometry>
          <cylinder>
            <radius>0.05</radius>
            <length>{tap_length}</length>
          </cylinder>
        </geometry>
        <pose>{tap_length/2} 0 0 0 1.5708 0</pose>
      </collision>
    </link>
  </model>
</sdf>"""
    
    try:
        spawn(f"tap_{i}", tap_sdf, "", tap_pose, "world")
        print(f"Tap {i}: ({pos.x:.2f}, {pos.y:.2f}), {tap_length:.2f}m")
        
        created_taps.append({
            'id': i,
            'position': [pos.x, pos.y, 0.0],
            'length': tap_length
        })
    except Exception as e:
        print(f"Error tap {i}: {e}")

data = {
    'aruco_field': {
        'size': ARUCO_FIELD_SIZE,
        'bounds': {'x': [ARUCO_MIN_X, ARUCO_MAX_X], 'y': [ARUCO_MIN_Y, ARUCO_MAX_Y]}
    },
    'main_pipe': {
        'start': [main_pipe_start.x, main_pipe_start.y, 0.0],
        'end': [main_pipe_end.x, main_pipe_end.y, 0.0],
        'length': main_pipe_length,
        'angle': math.degrees(pipe_bend_angle)
    },
    'taps': created_taps,
    'tap_spacing': actual_spacing
}

file_path = os.path.expanduser('~/pipeline_config.yaml')
with open(file_path, 'w') as f:
    yaml.dump(data, f, default_flow_style=False)

rospy.set_param('/pipeline/taps', [[tap['position'][0], tap['position'][1], 0.0] for tap in created_taps])

print(f"Summary:")
print(f"Pipe length: {main_pipe_length:.2f}m (target: 5-10m)")
print(f"Taps created: {len(created_taps)}/{num_taps}")
print(f"Spacing: {actual_spacing:.2f}m (target: {min_tap_distance}m)")
print(f"All within ArUco field (7x7m)")
