import rclpy
from rclpy.node import Node
from std_msgs.msg import Int32, Bool
from pymodbus.client import ModbusSerialClient

# M0000~M0003 → Modbus 코일 주소 0~3
M_COIL_ADDR = {0: 0, 1: 1, 2: 2, 3: 3}


class XgbRos2ModbusNode(Node):
    def __init__(self):
        super().__init__('xgb_ros2_modbus_node')

        self.word_pub = self.create_publisher(Int32, '/plc_word_read', 10)
        self.bit_sub = self.create_subscription(
            Bool, '/plc_bit_control', self.bit_control_callback, 10)
        for m_idx in M_COIL_ADDR:
            self.create_subscription(
                Bool, f'/plc_m{m_idx}',
                lambda msg, addr=M_COIL_ADDR[m_idx]: self.m_bit_callback(msg, addr),
                10)
        self.m_all_sub = self.create_subscription(
            Bool, '/plc_m_all', self.m_all_callback, 10)
        self.word_sub = self.create_subscription(
            Int32, '/plc_word_control', self.word_control_callback, 10)

        self.client = ModbusSerialClient(
            port='/dev/ttyUSB0',
            baudrate=115200,
            parity='N',
            stopbits=1,
            bytesize=8,
        )

        if self.client.connect():
            self.get_logger().info(
                '★★★ XBC-DR10E (/dev/ttyUSB0) 연결 성공! 통신 시작 ★★★')
        else:
            self.get_logger().error(
                'PLC 연결 실패... 배선이나 포트 상태를 다시 확인하세요.')

        self.create_timer(1.0, self.read_timer_callback)

    def read_timer_callback(self):
        if not self.client.connected:
            return

        result = self.client.read_holding_registers(
            address=0, count=1, device_id=1)

        if not result.isError():
            p020_value = result.registers[0]
            msg = Int32()
            msg.data = p020_value
            self.word_pub.publish(msg)
            self.get_logger().info(
                f'==> PLC에서 읽은 P020 데이터: {p020_value}')
        else:
            self.get_logger().warn('PLC 워드 읽기 실패 (Modbus 에러)')

    def _write_m_coil(self, address: int, value: bool, label: str) -> bool:
        if not self.client.connected:
            return False
        response = self.client.write_coil(
            address=address, value=value, device_id=1)
        if not response.isError():
            status = 'ON' if value else 'OFF'
            self.get_logger().info(f' <== {label} -> {status}')
            return True
        self.get_logger().error(f'{label} 제어 실패')
        return False

    def bit_control_callback(self, msg):
        self._write_m_coil(0, msg.data, 'M0000 (P0040)')

    def m_bit_callback(self, msg, address: int):
        m_num = address
        self._write_m_coil(address, msg.data, f'M{m_num:04d}')

    def m_all_callback(self, msg):
        if not self.client.connected:
            return
        values = [msg.data] * len(M_COIL_ADDR)
        response = self.client.write_coils(
            address=0, values=values, device_id=1)
        if not response.isError():
            status = 'ON' if msg.data else 'OFF'
            self.get_logger().info(
                f' <== M0000~M0003 일괄 제어 -> {status}')
        else:
            self.get_logger().error('M0000~M0003 일괄 제어 실패')

    def word_control_callback(self, msg):
        if not self.client.connected:
            return

        target_value = msg.data
        response = self.client.write_register(
            address=0, value=target_value, device_id=1)

        if not response.isError():
            self.get_logger().info(
                f' <== PLC P000 워드에 값 입력 성공: {target_value}')
        else:
            self.get_logger().error('PLC 워드 쓰기 실패')


def main(args=None):
    rclpy.init(args=args)
    node = XgbRos2ModbusNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.client.close()
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
