import RPi.GPIO as GPIO
import time
import threading

class MotorControl:
    def __init__(self):
        # GPIO pin definitions for motor driver
        self.MOTOR_A_ENABLE = 17  # PWM for left motor speed
        self.MOTOR_A_IN1 = 27     # Left motor direction 1
        self.MOTOR_A_IN2 = 22     # Left motor direction 2
        self.MOTOR_B_ENABLE = 18  # PWM for right motor speed
        self.MOTOR_B_IN3 = 23     # Right motor direction 1
        self.MOTOR_B_IN4 = 24     # Right motor direction 2
        
        # LED pin definitions
        self.FRONT_LED_PIN = 20   # GPIO20 for front LEDs
        self.BACK_LED_PIN = 12    # GPIO12 for back LEDs
        
        # PWM frequency
        self.PWM_FREQ = 1000
        
        # Motor speed limits
        self.MAX_SPEED = 100
        self.MIN_SPEED = 0
        
        # Current motor states
        self.left_speed = 0
        self.right_speed = 0
        self.left_direction = 0  # -1: backward, 0: stop, 1: forward
        self.right_direction = 0
        
        # Joystick positions
        self.left_joystick_x = 0
        self.left_joystick_y = 0
        self.right_joystick_x = 0
        self.right_joystick_y = 0
        
        # Threading lock for motor control
        self.motor_lock = threading.Lock()
        
        # Emergency stop flag
        self.emergency_stop = False
        
        # LED control threads and flags
        self.front_led_blinking = False
        self.back_led_blinking = False
        self.front_led_thread = None
        self.back_led_thread = None
        self.led_lock = threading.Lock()
        
        self.setup_gpio()
    
    def setup_gpio(self):
        """Initialize GPIO pins for motor control"""
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        # Setup motor control pins
        motor_pins = [
            self.MOTOR_A_ENABLE, self.MOTOR_A_IN1, self.MOTOR_A_IN2,
            self.MOTOR_B_ENABLE, self.MOTOR_B_IN3, self.MOTOR_B_IN4
        ]
        
        for pin in motor_pins:
            GPIO.setup(pin, GPIO.OUT)
        
        # Setup LED pins
        GPIO.setup(self.FRONT_LED_PIN, GPIO.OUT)
        GPIO.setup(self.BACK_LED_PIN, GPIO.OUT)
        GPIO.output(self.FRONT_LED_PIN, GPIO.LOW)
        GPIO.output(self.BACK_LED_PIN, GPIO.LOW)
        
        # Setup PWM for speed control
        self.pwm_a = GPIO.PWM(self.MOTOR_A_ENABLE, self.PWM_FREQ)
        self.pwm_b = GPIO.PWM(self.MOTOR_B_ENABLE, self.PWM_FREQ)
        
        # Start PWM with 0% duty cycle
        self.pwm_a.start(0)
        self.pwm_b.start(0)
        
        print("Motor control GPIO initialized")
    
    def set_motor_speed(self, motor, speed, direction):
        """Set motor speed and direction"""
        if self.emergency_stop:
            self.stop_all()
            return
        
        with self.motor_lock:
            if motor == 'left':
                self.left_speed = abs(speed)
                self.left_direction = direction
                self._control_motor('left', self.left_speed, direction)
            elif motor == 'right':
                self.right_speed = abs(speed)
                self.right_direction = direction
                self._control_motor('right', self.right_speed, direction)
    
    def _control_motor(self, motor, speed, direction):
        """Internal method to control individual motor"""
        # Clamp speed to valid range
        speed = max(self.MIN_SPEED, min(self.MAX_SPEED, speed))
        
        if motor == 'left':
            if direction == 1:  # Forward
                GPIO.output(self.MOTOR_A_IN1, GPIO.HIGH)
                GPIO.output(self.MOTOR_A_IN2, GPIO.LOW)
            elif direction == -1:  # Backward
                GPIO.output(self.MOTOR_A_IN1, GPIO.LOW)
                GPIO.output(self.MOTOR_A_IN2, GPIO.HIGH)
            else:  # Stop
                GPIO.output(self.MOTOR_A_IN1, GPIO.LOW)
                GPIO.output(self.MOTOR_A_IN2, GPIO.LOW)
            
            self.pwm_a.ChangeDutyCycle(speed)
            
        elif motor == 'right':
            if direction == 1:  # Forward
                GPIO.output(self.MOTOR_B_IN3, GPIO.HIGH)
                GPIO.output(self.MOTOR_B_IN4, GPIO.LOW)
            elif direction == -1:  # Backward
                GPIO.output(self.MOTOR_B_IN3, GPIO.LOW)
                GPIO.output(self.MOTOR_B_IN4, GPIO.HIGH)
            else:  # Stop
                GPIO.output(self.MOTOR_B_IN3, GPIO.LOW)
                GPIO.output(self.MOTOR_B_IN4, GPIO.LOW)
            
            self.pwm_b.ChangeDutyCycle(speed)
    
    def _blink_led(self, pin, blink_flag_attr, interval=0.5):
        """Internal method to blink an LED on a given pin while the flag is True."""
        while getattr(self, blink_flag_attr):
            GPIO.output(pin, GPIO.HIGH)
            time.sleep(interval)
            GPIO.output(pin, GPIO.LOW)
            time.sleep(interval)
        GPIO.output(pin, GPIO.LOW)

    def _start_blinking_led(self, pin, blink_flag_attr, thread_attr, interval=0.5):
        with self.led_lock:
            setattr(self, blink_flag_attr, True)
            if getattr(self, thread_attr) is None or not getattr(self, thread_attr).is_alive():
                t = threading.Thread(target=self._blink_led, args=(pin, blink_flag_attr, interval))
                t.daemon = True
                setattr(self, thread_attr, t)
                t.start()

    def _stop_blinking_led(self, pin, blink_flag_attr, thread_attr):
        with self.led_lock:
            setattr(self, blink_flag_attr, False)
            GPIO.output(pin, GPIO.LOW)

    def _set_led(self, pin, state):
        GPIO.output(pin, GPIO.HIGH if state else GPIO.LOW)
    
    def move_forward(self, speed=None):
        """Move robot forward"""
        if speed is None:
            speed = self.MAX_SPEED
        self.set_motor_speed('left', speed, 1)
        self.set_motor_speed('right', speed, 1)
        # Turn both LEDs ON
        self._set_led(self.FRONT_LED_PIN, True)
        self._set_led(self.BACK_LED_PIN, True)
    
    def move_backward(self, speed=None):
        """Move robot backward"""
        if speed is None:
            speed = self.MAX_SPEED
        self.set_motor_speed('left', speed, -1)
        self.set_motor_speed('right', speed, -1)
        # Turn both LEDs ON
        self._set_led(self.FRONT_LED_PIN, True)
        self._set_led(self.BACK_LED_PIN, True)
    
    def turn_left(self, speed=None):
        """Turn robot left"""
        if speed is None:
            speed = self.MAX_SPEED
        self.set_motor_speed('left', speed, -1)
        self.set_motor_speed('right', speed, 1)
    
    def turn_right(self, speed=None):
        """Turn robot right"""
        if speed is None:
            speed = self.MAX_SPEED
        self.set_motor_speed('left', speed, 1)
        self.set_motor_speed('right', speed, -1)
    
    def stop_all(self):
        """Stop all motors"""
        with self.motor_lock:
            self.left_speed = 0
            self.right_speed = 0
            self.left_direction = 0
            self.right_direction = 0
            
            # Stop both motors
            self._control_motor('left', 0, 0)
            self._control_motor('right', 0, 0)
        # Turn both LEDs OFF
        self._set_led(self.FRONT_LED_PIN, False)
        self._set_led(self.BACK_LED_PIN, False)
    
    def set_joystick_control(self, left_x, left_y, right_x, right_y):
        """Control motors based on joystick input"""
        if self.emergency_stop:
            self.stop_all()
            return
        
        # Left joystick controls movement
        left_speed = abs(left_y) * self.MAX_SPEED
        left_direction = 1 if left_y > 0 else -1 if left_y < 0 else 0
        
        # Right joystick controls steering (differential drive)
        right_speed = abs(right_x) * self.MAX_SPEED
        right_direction = 1 if right_x > 0 else -1 if right_x < 0 else 0
        
        # Combine movement and steering
        if left_direction != 0:
            # Movement with steering
            left_motor_speed = left_speed
            right_motor_speed = left_speed
            
            if right_direction != 0:
                # Apply steering
                steering_factor = right_speed / self.MAX_SPEED
                if right_direction > 0:  # Turn right
                    right_motor_speed *= (1 - steering_factor)
                else:  # Turn left
                    left_motor_speed *= (1 - steering_factor)
            
            self.set_motor_speed('left', left_motor_speed, left_direction)
            self.set_motor_speed('right', right_motor_speed, left_direction)
        else:
            # Only steering (spot turn)
            if right_direction != 0:
                self.set_motor_speed('left', right_speed, -right_direction)
                self.set_motor_speed('right', right_speed, right_direction)
            else:
                self.stop_all()
    
    def emergency_stop_activate(self):
        """Activate emergency stop"""
        self.emergency_stop = True
        self.stop_all()
        print("EMERGENCY STOP ACTIVATED!")
    
    def emergency_stop_reset(self):
        """Reset emergency stop"""
        self.emergency_stop = False
        print("Emergency stop reset")
    
    def get_status(self):
        """Get current motor status"""
        return {
            'left_speed': self.left_speed,
            'right_speed': self.right_speed,
            'left_direction': self.left_direction,
            'right_direction': self.right_direction,
            'emergency_stop': self.emergency_stop
        }
    
    def cleanup(self):
        """Cleanup GPIO on shutdown"""
        self.stop_all()
        self.pwm_a.stop()
        self.pwm_b.stop()
        GPIO.output(self.FRONT_LED_PIN, GPIO.LOW)
        GPIO.output(self.BACK_LED_PIN, GPIO.LOW)
        GPIO.cleanup()
        print("Motor control cleaned up")

# Global motor control instance
motor_controller = None

def init_motor_control():
    """Initialize motor control"""
    global motor_controller
    try:
        motor_controller = MotorControl()
        return True
    except Exception as e:
        print(f"Error initializing motor control: {e}")
        return False

def get_motor_controller():
    """Get motor controller instance"""
    return motor_controller 