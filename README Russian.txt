Шаг 1: Клонирование репозитория
Открыть терминал и выполнить:
cd ~
git clone https://github.com/agent000008/pipeline_monitoring.git
cd pipeline_monitoring
Шаг 2: Установка ROS Noetic (если не установлен)
Для Ubuntu 20.04:
sudo apt update
sudo apt install ros-noetic-desktop-full -y
Добавить ROS в PATH:
echo "source /opt/ros/noetic/setup.bash" >> ~/.bashrc
source ~/.bashrc
Шаг 3: Установка Python зависимостей
pip3 install pyyaml numpy
Шаг 4: Создание рабочего пространства ROS
mkdir -p ~/catkin_ws/src
cd ~/catkin_ws/src
ln -s ~/pipeline_monitoring .
cd ~/catkin_ws
catkin_make
source devel/setup.bash
Шаг 5: Установка Clover симуляции
cd ~/catkin_ws/src
git clone https://github.com/CopterExpress/clover.git
cd ~/catkin_ws
catkin_make
Добавить пути к моделям Gazebo:
echo 'export GAZEBO_MODEL_PATH=$GAZEBO_MODEL_PATH:~/catkin_ws/src/clover/clover_description/models' >> ~/.bashrc
source ~/.bashrc
Шаг 6: Запуск системы (3 терминала)
Терминал 1: Запуск ROS Master
cd ~/catkin_ws
source devel/setup.bash
roscore
Терминал 2: Запуск Gazebo с исправлением рендеринга
cd ~/catkin_ws
source devel/setup.bash
export LIBGL_ALWAYS_SOFTWARE=1
rosrun gazebo_ros gazebo --verbose
Терминал 3: Генерация трубопровода и маркеров
cd ~/catkin_ws
source devel/setup.bash
Ждем 15 секунд пока Gazebo полностью запустится
sleep 15
Генерация основного трубопровода с врезками
rosrun pipeline_monitoring generate_world_fixed.py
Ждем 5 секунд
sleep 5
Создание сетки ArUco маркеров
rosrun pipeline_monitoring create_aruco_grid.py