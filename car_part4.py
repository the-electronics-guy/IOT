import pygame
from pygame.locals import *
import random

# Initialize Pygame
pygame.init()

# Create the game window
width = 500
height = 500
screen_size = (width, height)
screen = pygame.display.set_mode(screen_size)
pygame.display.set_caption('Car Game')

# Colors
gray = (100, 100, 100)
green = (76, 208, 56)
yellow = (255, 232, 0)
white = (255, 255, 255)
red = (200, 0, 0)

# Road and marker sizes
road_width = 300
marker_width = 10
marker_height = 50

# Lane coordinates
left_lane = 150
center_lane = 250
right_lane = 350

# lanes
lanes = [left_lane, center_lane, right_lane]

# Road and edge markers
road = (100, 0, road_width, height)
left_edge_marker = (95, 0, marker_width, height)
right_edge_marker = (395, 0, marker_width, height)

# Load the player's car image
player_car_image = pygame.image.load('images/car.png')
player_car_image = pygame.transform.scale(player_car_image, (50, 100))
player_x = center_lane
player_y = 400
current_lane_index = 1  # Start in the center lane

# Load opponent vehicle images
vehicle_images = ['images/pickup_truck.png', 'images/taxi.png', 'images/van.png']
opponent_images = [pygame.image.load(image) for image in vehicle_images]

# Scale opponent vehicles to fit the lanes
opponent_images = [pygame.transform.scale(image, (50, 100)) for image in opponent_images]

# List to hold opponent vehicles
opponents = []

# Clock for managing frame rate
clock = pygame.time.Clock()
fps = 60

# Speed settings
speed = 2

# Scoring and game states
score = 0
game_over = False
font = pygame.font.Font(None, 36)

# Main game loop
running = True
while running:
    clock.tick(fps)

    # Event handling
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        if game_over and event.type == KEYDOWN:
            if event.key == K_y:  # Restart game
                game_over = False
                score = 0
                speed = 2
                opponents = []
                player_x = center_lane
                player_y = 400
                current_lane_index = 1
            elif event.key == K_n:  # Quit game
                running = False
        if not game_over and event.type == KEYDOWN:
            if event.key == K_LEFT and current_lane_index > 0:
                current_lane_index -= 1
                player_x = lanes[current_lane_index]
            if event.key == K_RIGHT and current_lane_index < 2:
                current_lane_index += 1
                player_x = lanes[current_lane_index]

    # Skip the rest of the loop if the game is over
    if game_over:
        continue

    # Draw the grass
    screen.fill(green)

    # Draw the road
    pygame.draw.rect(screen, gray, road)

    # Draw the edge markers
    pygame.draw.rect(screen, yellow, left_edge_marker)
    pygame.draw.rect(screen, yellow, right_edge_marker)
    
    # Draw lane markers
    lane_marker_move_y = (pygame.time.get_ticks() // 10) % (marker_height * 2)
    for y in range(-marker_height * 2, height, marker_height * 2):
        pygame.draw.rect(screen, white, (left_lane + 45, y + lane_marker_move_y, marker_width, marker_height))
        pygame.draw.rect(screen, white, (center_lane + 45, y + lane_marker_move_y, marker_width, marker_height))


    # Draw the player's car
    player_rect = player_car_image.get_rect(center=(player_x, player_y))
    screen.blit(player_car_image, player_rect)

    # Add a new opponent vehicle
    if len(opponents) < 3 and random.randint(1, 50) == 1:  # Random chance to spawn vehicles
        lane = random.choice(lanes)
        opponent_image = random.choice(opponent_images)
        opponent_rect = opponent_image.get_rect(center=(lane, -50))  # Start above the screen
        opponents.append((opponent_image, opponent_rect))

    # Move opponent vehicles
    for vehicle in opponents[:]:
        vehicle_image, vehicle_rect = vehicle
        vehicle_rect.y += speed  # Move down the screen

        # Remove vehicles that move off-screen and increase score
        if vehicle_rect.top > height:
            opponents.remove(vehicle)
            score += 1  # Increment score for avoiding the vehicle

            # Increase game speed every 5 points
            if score % 5 == 0:
                speed += 1

        # Detect collision
        if player_rect.colliderect(vehicle_rect):
            game_over = True

        # Draw the opponent vehicles
        screen.blit(vehicle_image, vehicle_rect)

    # Display the score
    score_text = font.render(f'Score: {score}', True, white)
    screen.blit(score_text, (10, 10))

    # Check if the game is over
    if game_over:
        # Display Game Over message
        pygame.draw.rect(screen, red, (50, 200, 400, 100))
        game_over_text = font.render('Game Over! Play Again? (Y/N)', True, white)
        screen.blit(game_over_text, (70, 240))

    # Update the display
    pygame.display.update()

# Quit Pygame
pygame.quit()
