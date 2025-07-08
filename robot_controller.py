import RPi.GPIO as GPIO
from picamera2 import Picamera2
from picamera2.encoders import JpegEncoder
from picamera2.outputs import FileOutput
import threading
import time
import json
from flask import Flask, render_template, jsonify, request, Response
import io
import cv2

class RobotController:
    def __init__(self):
        # Motor control pins
        self.ENA = 17
        self.IN1 = 27
        self.IN2 = 22
        
        # Additional motor pins for dual motor control
        self.ENB = 18
        self.IN3 = 23
        self.IN4 = 24
        
        # Initialize GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        # Setup motor pins
        GPIO.setup(self.ENA, GPIO.OUT)
        GPIO.setup(self.IN1, GPIO.OUT)
        GPIO.setup(self.IN2, GPIO.OUT)
        GPIO.setup(self.ENB, GPIO.OUT)
        GPIO.setup(self.IN3, GPIO.OUT)
        GPIO.setup(self.IN4, GPIO.OUT)
        
        # Initialize PWM for speed control
        self.pwm_a = GPIO.PWM(self.ENA, 100)
        self.pwm_b = GPIO.PWM(self.ENB, 100)
        self.pwm_a.start(0)
        self.pwm_b.start(0)
        
        # Initialize camera
        self.picam2 = Picamera2()
        self.camera_config = self.picam2.create_preview_configuration(
            main={"size": (640, 480)},
            buffer_count=4
        )
        self.picam2.configure(self.camera_config)
        self.picam2.start()
        
        # Robot state
        self.current_mode = "MANUAL"
        self.is_running = True
        
        # Start camera thread
        self.camera_thread = threading.Thread(target=self._camera_loop, daemon=True)
        self.camera_thread.start()
    
    def forward(self, speed=100):
        """Move robot forward"""
        self.pwm_a.ChangeDutyCycle(speed)
        self.pwm_b.ChangeDutyCycle(speed)
        GPIO.output(self.IN1, GPIO.HIGH)
        GPIO.output(self.IN2, GPIO.LOW)
        GPIO.output(self.IN3, GPIO.HIGH)
        GPIO.output(self.IN4, GPIO.LOW)
        print(f"Moving forward at {speed}% speed")
    
    def backward(self, speed=100):
        """Move robot backward"""
        self.pwm_a.ChangeDutyCycle(speed)
        self.pwm_b.ChangeDutyCycle(speed)
        GPIO.output(self.IN1, GPIO.LOW)
        GPIO.output(self.IN2, GPIO.HIGH)
        GPIO.output(self.IN3, GPIO.LOW)
        GPIO.output(self.IN4, GPIO.HIGH)
        print(f"Moving backward at {speed}% speed")
    
    def left(self, speed=100):
        """Turn robot left"""
        self.pwm_a.ChangeDutyCycle(speed)
        self.pwm_b.ChangeDutyCycle(speed)
        GPIO.output(self.IN1, GPIO.LOW)
        GPIO.output(self.IN2, GPIO.HIGH)
        GPIO.output(self.IN3, GPIO.HIGH)
        GPIO.output(self.IN4, GPIO.LOW)
        print(f"Turning left at {speed}% speed")
    
    def right(self, speed=100):
        """Turn robot right"""
        self.pwm_a.ChangeDutyCycle(speed)
        self.pwm_b.ChangeDutyCycle(speed)
        GPIO.output(self.IN1, GPIO.HIGH)
        GPIO.output(self.IN2, GPIO.LOW)
        GPIO.output(self.IN3, GPIO.LOW)
        GPIO.output(self.IN4, GPIO.HIGH)
        print(f"Turning right at {speed}% speed")
    
    def stop(self):
        """Stop robot movement"""
        self.pwm_a.ChangeDutyCycle(0)
        self.pwm_b.ChangeDutyCycle(0)
        GPIO.output(self.IN1, GPIO.LOW)
        GPIO.output(self.IN2, GPIO.LOW)
        GPIO.output(self.IN3, GPIO.LOW)
        GPIO.output(self.IN4, GPIO.LOW)
        print("Robot stopped")
    
    def joystick_control(self, x, y, magnitude):
        """Control robot using joystick input"""
        if magnitude < 0.1:  # Dead zone
            self.stop()
            return
        
        # Calculate speed based on magnitude
        speed = int(magnitude * 100)
        speed = max(20, min(100, speed))  # Clamp between 20-100%
        
        # Calculate direction based on angle
        if abs(x) > abs(y):
            if x > 0:
                self.right(speed)
            else:
                self.left(speed)
        else:
            if y > 0:
                self.forward(speed)
            else:
                self.backward(speed)
    
    def _camera_loop(self):
        """Camera streaming loop"""
        while self.is_running:
            try:
                # Capture frame
                frame = self.picam2.capture_array()
                # Convert to JPEG
                _, buffer = cv2.imencode('.jpg', frame)
                frame_bytes = buffer.tobytes()
                
                # Store latest frame for streaming
                self.latest_frame = frame_bytes
                time.sleep(0.033)  # ~30 FPS
            except Exception as e:
                print(f"Camera error: {e}")
                time.sleep(1)
    
    def get_camera_frame(self):
        """Get the latest camera frame"""
        if hasattr(self, 'latest_frame'):
            return self.latest_frame
        return None
    
    def set_mode(self, mode):
        """Set robot operation mode"""
        self.current_mode = mode
        print(f"Robot mode changed to: {mode}")
    
    def cleanup(self):
        """Cleanup GPIO and camera"""
        self.is_running = False
        self.stop()
        self.pwm_a.stop()
        self.pwm_b.stop()
        GPIO.cleanup()
        self.picam2.close()

# Initialize robot controller
robot = RobotController()

# Flask app setup
app = Flask(__name__)

def gen_frames():
    """Generate camera frames for streaming"""
    while True:
        frame = robot.get_camera_frame()
        if frame:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        else:
            time.sleep(0.1)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/control', methods=['POST'])
def control():
    data = request.get_json() or {}
    action = data.get('action')
    
    if action == 'forward':
        robot.forward()
    elif action == 'backward':
        robot.backward()
    elif action == 'left':
        robot.left()
    elif action == 'right':
        robot.right()
    elif action == 'stop':
        robot.stop()
    else:
        return jsonify({'status': 'error', 'message': 'Invalid action'})
    
    print(f"Action received: {action}")
    return jsonify({'status': 'success', 'action': action})

@app.route('/api/joystick', methods=['POST'])
def joystick():
    data = request.get_json() or {}
    side = data.get('side')
    x = data.get('x', 0)
    y = data.get('y', 0)
    magnitude = data.get('magnitude', 0)
    angle = data.get('angle', 0)
    
    if robot.current_mode == "MANUAL":
        robot.joystick_control(x, y, magnitude)
    
    print(f"Joystick {side}: x={x:.2f}, y={y:.2f}, magnitude={magnitude:.2f}, angle={angle:.2f}")
    return jsonify({'status': 'success', 'side': side, 'x': x, 'y': y, 'magnitude': magnitude, 'angle': angle})

@app.route('/api/mode', methods=['POST'])
def mode():
    data = request.get_json() or {}
    mode = data.get('mode')
    
    robot.set_mode(mode)
    print(f"Mode changed to: {mode}")
    return jsonify({'status': 'success', 'mode': mode})

@app.route('/api/status')
def status():
    return jsonify({
        'battery': '85%',
        'location': 'Home',
        'mode': robot.current_mode,
        'status': 'connected'
    })

if __name__ == '__main__':
    try:
        print("Starting Robot Controller...")
        print("Web interface available at: http://localhost:5000")
        app.run(host='0.0.0.0', port=5000, debug=False)
    except KeyboardInterrupt:
        print("\nShutting down robot controller...")
        robot.cleanup()
    except Exception as e:
        print(f"Error: {e}")
        robot.cleanup() 