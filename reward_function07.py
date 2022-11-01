# Place import statement outside of function (supported libraries: math, random, numpy, scipy, and shapely)
# Example imports of available libraries
#
# import math
# import random
# import numpy
# import scipy
# import shapely

import math


def reward_function(params):
    '''
    Example of rewarding the agent to stay inside the two borders of the track
    Example of rewarding the agent to follow center line
    Example of rewarding the agent to prevent zigzag
    Example of rewarding the agent to stay inside two borders
    and penalizing getting too close to the objects in front
    Example of using waypoints and heading to make the car point in the right direction
    '''

    ################## INPUT PARAMETERS ###################
    # Read input parameters
    all_wheels_on_track = params['all_wheels_on_track']
    distance_from_center = params['distance_from_center']
    track_width = params['track_width']
    progress = params['progress']
    steps = params['steps']
    speed = params['speed']
    is_offtrack=params['is_offtrack']
    abs_steering = abs(params['steering_angle']) # Only need the absolute steering angle
    objects_location = params['objects_location']
    agent_x = params['x']
    agent_y = params['y']
    _, next_object_index = params['closest_objects']
    objects_left_of_center = params['objects_left_of_center']
    is_left_of_center = params['is_left_of_center']
    waypoints = params['waypoints']
    closest_waypoints = params['closest_waypoints']
    heading = params['heading']

    ############################Initialization#########################################
    # Give a very low reward by default
    # Initialize reward with a small number but not zero
    # because zero means off-track or crashed
    # reward = 1e-3
    reward = 1
    
    # Steering penality threshold, change the number based on your action space setting
    ABS_STEERING_THRESHOLD = 20
    
    # Set the speed threshold based your action space
    SPEED_THRESHOLD = 1.0
    SPEED_THRESHOLD_1 = 1.8
    SPEED_THRESHOLD_2 = 1.3
    DIRECTION_THRESHOLD = 3.0
    
    benchmark_time=11.7
    benchmark_steps=173
    straight_waypoints=[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,43,44,45,46,47,48,49,50,56,57,58,59,60,61,62,63,64,71,72,73,74,75,76,77,78,89,90,91,92,93,94,95,96,97,98,99,100,101,102,103,112,113,114,115,116,117]
    
    # Total num of steps we want the car to finish the lap, it will vary depends on the track length
    TOTAL_NUM_STEPS = 300
    
    ##################################Let's go#############################################
    # Give a high reward if no wheels go off the track and
    # the agent is somewhere in between the track borders
    if all_wheels_on_track and (0.5*track_width - distance_from_center) >= 0.05:
        reward = 1.0
    elif not all_wheels_on_track:
        # Penalize if the car goes off track
        reward = 1e-3
    else:
        reward = progress
        
    # check speed
    if speed < SPEED_THRESHOLD:
        # Penalize if the car goes too slow
        reward += 0.5
    else:
        # High reward if the car stays on track and goes fast
        reward += 1.0

    # Calculate 5 marks father away from the center line
    marker_1 = 0.1 * track_width
    marker_2 = 0.20 * track_width
    marker_3 = 0.30 * track_width
    marker_4 = 0.40 * track_width
    marker_5 = 0.5 * track_width

    # Give higher reward if the car is closer to center line 
    if distance_from_center <= marker_1 and all_wheels_on_track:
        reward += 3.0
    elif distance_from_center <= marker_2 and all_wheels_on_track:
        reward += 2.5
    elif distance_from_center <= marker_3 and all_wheels_on_track:
        reward += 1.5
    elif distance_from_center <= marker_4 and all_wheels_on_track:
        reward += 1
    elif distance_from_center <= marker_5 and all_wheels_on_track:
        reward += 0.5
    else:
        reward -= 1  # likely crashed/ close to off track

    # Penalize reward if the car is steering too much
    if abs_steering > ABS_STEERING_THRESHOLD:
        reward *= 0.8
        
    # Give higher reward if the car completes the track
    if progress > 70:
        reward += 5.0
    elif progress == 100:
        reward += 10
    else:
        reward *= 0.8  # completion % is not good
        
    # Give additional reward if the car pass every 100 steps faster than expected
    # if (steps % 100) == 0 and progress > (steps / TOTAL_NUM_STEPS) * 100 :
        # reward += 10.0
        
    # Give additional reward if the car pass every 50 steps faster than expected
    if (steps % 50) == 0 and progress >= (steps / benchmark_steps) * 100 :
        reward += 10.0
    # Penalize if the car cannot finish the track in less than benchmark_steps
    elif (steps % 50) == 0 and progress < (steps / benchmark_steps) * 100 :
        reward -= 5.0
        
    ######################################################################
    # Reward if the agent stays inside the two borders of the track
    if all_wheels_on_track and (0.5 * track_width - distance_from_center) >= 0.05:
        reward_lane = 1.0
    else:
        reward_lane = 1e-3
        
    # Penalize if the agent is too close to the next object
    reward_avoid = 1.0
    
    # Distance to the next object
    next_object_loc = objects_location[next_object_index]
    distance_closest_object = math.sqrt((agent_x - next_object_loc[0])**2 + (agent_y - next_object_loc[1])**2)
    
    # Decide if the agent and the next object is on the same lane
    is_same_lane = objects_left_of_center[next_object_index] == is_left_of_center
    if is_same_lane:
        if 0.5 <= distance_closest_object < 0.8:
            reward_avoid *= 0.5
        elif 0.3 <= distance_closest_object < 0.5:
            reward_avoid *= 0.2
        elif distance_closest_object < 0.3:
            reward_avoid = 1e-3  # Likely crashed
            
    # Calculate reward by putting different weights on
    # the two aspects above
    reward += 1.0 * reward_lane + 4.0 * reward_avoid
    
    #####################################################################
    # Calculate the direction of the center line based on the closest waypoints
    next_point = waypoints[closest_waypoints[1]]
    prev_point = waypoints[closest_waypoints[0]]

    # Calculate the direction in radius, arctan2(dy, dx), the result is (-pi, pi) in radians
    track_direction = math.atan2(next_point[1] - prev_point[1], next_point[0] - prev_point[0])
    
    # Convert to degree
    track_direction = math.degrees(track_direction)

    # Calculate the difference between the track direction and the heading direction of the car
    direction_diff = abs(track_direction - heading)
    if direction_diff > 180:
        direction_diff = 360 - direction_diff

    # Penalize the reward if the difference is too large
    # DIRECTION_THRESHOLD = 10.0
    DIRECTION_THRESHOLD = 3.0

    # if direction_diff > DIRECTION_THRESHOLD:
        # reward *= 0.5

    # Penalize the reward if the difference is too large
    direction_bonus=1
  
    if direction_diff > DIRECTION_THRESHOLD or not all_wheels_on_track:

        direction_bonus=1-(direction_diff/15)
        if direction_bonus<0 or direction_bonus>1:
            direction_bonus = 0
        reward *= direction_bonus
    else:
        if next_point in (straight_waypoints):
            if speed>=SPEED_THRESHOLD_1:
                reward+=max(speed,SPEED_THRESHOLD_1)
            else:
                reward+=1e-3
        else:
            if speed<=SPEED_THRESHOLD_2:
                reward+=max(speed,SPEED_THRESHOLD_2)
            else:
                reward+=1e-3
        
    ###################################################################
    # Calculate the distance from each border
    distance_from_border = 0.5 * track_width - distance_from_center

    # Reward higher if the car stays inside the track borders
    if distance_from_border >= 0.05:
        reward += 1.0
    else:
        reward -= 1.0    # Low reward if too close to the border or goes off the track

    # Always return a float value
    return float(reward)
