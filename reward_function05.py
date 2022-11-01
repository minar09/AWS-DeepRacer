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
    '''

    # Read input parameters
    all_wheels_on_track = params['all_wheels_on_track']
    distance_from_center = params['distance_from_center']
    track_width = params['track_width']
    progress = params['progress']
    steps = params['steps']
    speed = params['speed']
    abs_steering = abs(params['steering_angle']) # Only need the absolute steering angle
    objects_location = params['objects_location']
    agent_x = params['x']
    agent_y = params['y']
    _, next_object_index = params['closest_objects']
    objects_left_of_center = params['objects_left_of_center']
    is_left_of_center = params['is_left_of_center']

    # Give a very low reward by default
    # Initialize reward with a small number but not zero
    # because zero means off-track or crashed
    reward = 1e-3
    
    # Steering penality threshold, change the number based on your action space setting
    ABS_STEERING_THRESHOLD = 15 
    
    # Set the speed threshold based your action space
    SPEED_THRESHOLD = 1.0
    
    # Total num of steps we want the car to finish the lap, it will vary depends on the track length
    TOTAL_NUM_STEPS = 300
    
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
        reward = reward + 0.5
    else:
        # High reward if the car stays on track and goes fast
        reward = reward + 1.0

    # Calculate 5 marks father away from the center line
    marker_1 = 0.1 * track_width
    marker_2 = 0.20 * track_width
    marker_3 = 0.30 * track_width
    marker_4 = 0.40 * track_width
    marker_5 = 0.5 * track_width

    # Give higher reward if the car is closer to center line 
    if distance_from_center <= marker_1 and all_wheels_on_track:
        reward = 3.0
    elif distance_from_center <= marker_2 and all_wheels_on_track:
        reward = 2.5
    elif distance_from_center <= marker_3 and all_wheels_on_track:
        reward = 1.5
    elif distance_from_center <= marker_4 and all_wheels_on_track:
        reward = 1
    elif distance_from_center <= marker_5 and all_wheels_on_track:
        reward = 0.5
    else:
        reward = 1e-3  # likely crashed/ close to off track

    # Penalize reward if the car is steering too much
    if abs_steering > ABS_STEERING_THRESHOLD:
        reward *= 0.8
        
    # Give higher reward if the car completes the track
    if progress > 0.7:
        reward = 3.0
    elif progress == 1:
        reward = 10
    else:
        reward = 1e-3  # completion % is not good
        
    # Give additional reward if the car pass every 100 steps faster than expected
    if (steps % 100) == 0 and progress > (steps / TOTAL_NUM_STEPS) * 100 :
        reward += 10.0
        
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

    # Always return a float value
    return float(reward)
