# Raspberry Pi Robot Controller

A web-based robot controller for Raspberry Pi with live camera feed using picamera2 and motor control via GPIO.

## Features

- **Web Interface**: Control your robot from any device on the network
- **Live Camera Feed**: Real-time video streaming using picamera2
- **Dual Motor Control**: Independent control of left and right motors
- **Joystick Support**: Analog joystick control with speed and direction
- **Speed Control**: PWM-based speed control for smooth movement
- **Multiple Modes**: Manual control and future autonomous modes

## Hardware Requirements

### Raspberry Pi Setup
- Raspberry Pi 4 (recommended) or Pi 3
- Pi Camera Module 2 or 3
- Motor driver board (L298N or similar)
- 2 DC motors with wheels
- Chassis and battery pack

### Pin Connections

| Component | GPIO Pin | Description |
|-----------|----------|-------------|
| Motor A Enable | GPIO 17 | PWM speed control for left motor |
| Motor A Input 1 | GPIO 27 | Direction control for left motor |
| Motor A Input 2 | GPIO 22 | Direction control for left motor |
| Motor B Enable | GPIO 18 | PWM speed control for right motor |
| Motor B Input 3 | GPIO 23 | Direction control for right motor |
| Motor B Input 4 | GPIO 24 | Direction control for right motor |

## Installation

1. **Update your Raspberry Pi**:
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

2. **Install required system packages**:
   ```bash
   sudo apt install -y python3-pip python3-opencv libcamera-tools
   ```

3. **Enable camera and I2C**:
   ```bash
   sudo raspi-config
   ```
   - Navigate to "Interface Options"
   - Enable "Camera"
   - Enable "I2C" (if using I2C sensors)

4. **Install Python dependencies**:
   ```bash
   pip3 install -r requirements.txt
   ```

5. **Test motor connections**:
   ```bash
   python3 motor_test.py
   ```

## Usage

### Starting the Robot Controller

1. **Run the main controller**:
   ```bash
   python3 robot_controller.py
   ```

2. **Access the web interface**:
   - Open a web browser
   - Navigate to `http://[RASPBERRY_PI_IP]:5000`
   - Replace `[RASPBERRY_PI_IP]` with your Pi's IP address

### Web Interface Controls

- **Directional Buttons**: Forward, Backward, Left, Right, Stop
- **Joystick**: Analog control with speed and direction
- **Mode Selection**: Switch between manual and autonomous modes
- **Live Camera Feed**: Real-time video from the Pi Camera

### API Endpoints

- `GET /` - Web interface
- `GET /video_feed` - Live camera stream
- `POST /api/control` - Send movement commands
- `POST /api/joystick` - Joystick control data
- `POST /api/mode` - Change operation mode
- `GET /api/status` - Get robot status

## Troubleshooting

### Camera Issues
- Ensure camera is properly connected
- Check camera is enabled in raspi-config
- Verify picamera2 is installed: `pip3 install picamera2`

### Motor Issues
- Check wiring connections
- Verify motor driver power supply
- Test with motor_test.py first
- Ensure GPIO pins are not used by other processes

### Network Issues
- Check firewall settings
- Ensure port 5000 is accessible
- Verify Pi is on the same network as control device

## Safety Notes

- Always test motors on a safe surface first
- Keep hands clear of moving parts during testing
- Use appropriate power supply for your motors
- Monitor battery levels during operation

## Customization

### Adding Sensors
You can extend the robot by adding:
- Ultrasonic distance sensors
- Line following sensors
- IMU for orientation
- GPS for navigation

### Autonomous Features
The code structure supports adding:
- Obstacle avoidance
- Line following
- GPS navigation
- Computer vision processing

## License

This project is open source. Feel free to modify and distribute.

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests. 