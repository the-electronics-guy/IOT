#!/usr/bin/env python3
"""
Simple motor test script for Raspberry Pi robot
Run this to test if your motor connections are working correctly
"""

import RPi.GPIO as GPIO
import time

# Motor control pins
ENA = 17  # Enable A
IN1 = 27  # Input 1
IN2 = 22  # Input 2

ENB = 18  # Enable B  
IN3 = 23  # Input 3
IN4 = 24  # Input 4

def setup():
    """Setup GPIO pins"""
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    
    # Setup motor pins
    GPIO.setup(ENA, GPIO.OUT)
    GPIO.setup(IN1, GPIO.OUT)
    GPIO.setup(IN2, GPIO.OUT)
    GPIO.setup(ENB, GPIO.OUT)
    GPIO.setup(IN3, GPIO.OUT)
    GPIO.setup(IN4, GPIO.OUT)
    
    # Initialize PWM for speed control
    pwm_a = GPIO.PWM(ENA, 100)
    pwm_b = GPIO.PWM(ENB, 100)
    pwm_a.start(0)
    pwm_b.start(0)
    
    return pwm_a, pwm_b

def forward(pwm_a, pwm_b, speed=50):
    """Move forward"""
    print(f"Moving forward at {speed}% speed")
    pwm_a.ChangeDutyCycle(speed)
    pwm_b.ChangeDutyCycle(speed)
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.HIGH)
    GPIO.output(IN4, GPIO.LOW)

def backward(pwm_a, pwm_b, speed=50):
    """Move backward"""
    print(f"Moving backward at {speed}% speed")
    pwm_a.ChangeDutyCycle(speed)
    pwm_b.ChangeDutyCycle(speed)
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.HIGH)
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.HIGH)

def left(pwm_a, pwm_b, speed=50):
    """Turn left"""
    print(f"Turning left at {speed}% speed")
    pwm_a.ChangeDutyCycle(speed)
    pwm_b.ChangeDutyCycle(speed)
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.HIGH)
    GPIO.output(IN3, GPIO.HIGH)
    GPIO.output(IN4, GPIO.LOW)

def right(pwm_a, pwm_b, speed=50):
    """Turn right"""
    print(f"Turning right at {speed}% speed")
    pwm_a.ChangeDutyCycle(speed)
    pwm_b.ChangeDutyCycle(speed)
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.HIGH)

def stop(pwm_a, pwm_b):
    """Stop all motors"""
    print("Stopping all motors")
    pwm_a.ChangeDutyCycle(0)
    pwm_b.ChangeDutyCycle(0)
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.LOW)

def cleanup(pwm_a, pwm_b):
    """Cleanup GPIO"""
    pwm_a.stop()
    pwm_b.stop()
    GPIO.cleanup()

def main():
    print("Raspberry Pi Robot Motor Test")
    print("=============================")
    print("This script will test your motor connections.")
    print("Make sure your robot is on a safe surface!")
    print()
    
    try:
        pwm_a, pwm_b = setup()
        
        print("Starting motor test sequence...")
        print("Press Ctrl+C to stop")
        
        while True:
            # Test forward
            forward(pwm_a, pwm_b, 30)
            time.sleep(2)
            stop(pwm_a, pwm_b)
            time.sleep(1)
            
            # Test backward
            backward(pwm_a, pwm_b, 30)
            time.sleep(2)
            stop(pwm_a, pwm_b)
            time.sleep(1)
            
            # Test left turn
            left(pwm_a, pwm_b, 30)
            time.sleep(2)
            stop(pwm_a, pwm_b)
            time.sleep(1)
            
            # Test right turn
            right(pwm_a, pwm_b, 30)
            time.sleep(2)
            stop(pwm_a, pwm_b)
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nTest stopped by user")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cleanup(pwm_a, pwm_b)
        print("Motor test completed")

if __name__ == "__main__":
    main() 