
import time
import serial
import threading
import queue


class Hit:
    def __init__(self, hit_channel, hit_amplitude, hit_time):
        self.channel = hit_channel
        self.amplitude = hit_amplitude
        self.time = hit_time


class ArduinoController:
    def __init__(self, port, baudrate=115200, timeout=5, system_ready_msg="ready", name="ArduinoController"):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.system_ready_msg = system_ready_msg
        self.name = name
        self.serial_connection = None
        self.messages = queue.Queue()
        self.running = False

    def connect(self):
        try:
            print("initialising")
            self.serial_connection = serial.Serial(self.port, self.baudrate)
            self.running = True
            thread = threading.Thread(target=self._listen_for_messages)
            thread.start()
            print(f"Connected to device at {self.port} "
                  f"with baud rate {self.baudrate} and timeout {self.timeout}")
        except serial.SerialException as e:
            print(f"Error connecting to {self.port}: {e}")

    def _listen_for_messages(self):
        while self.running:
            if self.serial_connection.in_waiting > 0:
                message = self.serial_connection.readline().decode().strip()
                self.messages.put({"time": time.time(), "msg": message})

    def disconnect(self):
        self.running = False
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()

    def get_message(self):
        return self.messages.get() if not self.messages.empty() else None

    @staticmethod
    def parse_hit_msg(msg: str, hit_time: float):
        if not msg.startswith('h'):
            raise ValueError(f"Hit messages start with 'h'. This message is {msg}")
        msg = msg[1:]
        hit_channel, hit_amplitude = msg.split('a')
        return Hit(hit_channel=int(hit_channel), hit_amplitude=float(hit_amplitude), hit_time=hit_time)

    def get_hit(self):
        msg = self.get_message()
        if msg is not None and msg['msg'].startswith('h'):
            return self.parse_hit_msg(msg['msg'], msg['time'])
        return None
