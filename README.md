# xgb_plc_modbus

LS **XBC-DR10E** PLC ↔ **ROS 2 Humble** Modbus RTU 브리지 패키지.

- 노드: `xgb_ros2_modbus_node`
- 실행 파일: `plc_node`
- 시리얼: `/dev/ttyUSB0`, 115200 8N1, slave ID `1`

## 클론 & 빌드

워크스페이스 이름은 다른 프로젝트 `ros2_ws` 와 겹치지 않게 **`plcmodbus_ws`** 를 씁니다.

```bash
mkdir -p ~/plcmodbus_ws/src
cd ~/plcmodbus_ws/src
git clone https://github.com/jasper104615-collab/plcmodbus485.git xgb_plc_modbus

cd ~/plcmodbus_ws
source /opt/ros/humble/setup.bash
colcon build --packages-select xgb_plc_modbus
source install/setup.bash
```

## 실행

```bash
ros2 run xgb_plc_modbus plc_node
```

## 의존성

```bash
sudo apt install ros-humble-rclpy ros-humble-std-msgs -y
pip3 install pymodbus pyserial
pip3 uninstall serial -y   # pyserial 과 충돌하는 패키지 제거 (있을 때만)
```

USB 권한:

```bash
sudo usermod -aG dialout $USER
# 재로그인 후
ls -l /dev/ttyUSB0
```

## ROS 토픽

| 토픽 | 타입 | 방향 | PLC |
|------|------|------|-----|
| `/plc_word_read` | Int32 | publish | P020 (1초 주기) |
| `/plc_bit_control` | Bool | subscribe | M0000 |
| `/plc_m0` ~ `/plc_m3` | Bool | subscribe | M0000~M0003 |
| `/plc_m_all` | Bool | subscribe | M0000~M0003 일괄 |
| `/plc_word_control` | Int32 | subscribe | P000 |

## 테스트

```bash
ros2 topic pub --once /plc_m_all std_msgs/msg/Bool "{data: true}"
ros2 topic echo /plc_word_read
```

## 패키지 구조

```
xgb_plc_modbus/
├── package.xml
├── setup.py          # entry_points: plc_node
├── setup.cfg
├── resource/
└── xgb_plc_modbus/
    └── plc_node.py   # 노드 소스
```
