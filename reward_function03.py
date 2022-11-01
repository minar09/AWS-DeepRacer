def reward_function(params):
    '''
    Example of rewarding the agent to stay inside the two borders of the track
    Example of rewarding the agent to follow center line
    Example of rewarding the agent to prevent zigzag
    Example of rewarding the agent to stay inside two borders
    and penalizing getting too close to the objects in fr

    '''

    # Read input parameters
    all_wheels_on_track = params['all_wheels_on_track']
    distance_from_center = params['distance_from_center']
    track_width = params['track_width']
    progress = params['progress']
    abs_steering = abs(params['steering_angle']) # Only need the absolute steering angle
    objects_location = params['objects_location']
    agent_x = params['x']
    agent_y = params['y']
    _, next_object_index = params['closest_objects']
    objects_left_of_center = params['objects_left_of_center']
    is_left_of_center = params['is_left_of_center']

    # Give a very low reward by default
    reward = 1e-3
    
    # Give a high reward if no wheels go off the track and
    # the agent is somewhere in between the track borders
    if all_wheels_on_track and (0.5*track_width - distance_from_center) >= 0.05:
        reward = 1.0
        reward_lane = 1.0
    elif not all_wheels_on_track:
        reward = -1
    else:
        reward = progress
        reward_lane = 1e-3

    # Calculate 3 markers that are at varying distances away from the center line
    marker_1 = 0.1 * track_width
    marker_2 = 0.25 * track_width
    marker_3 = 0.5 * track_width

    # Give higher reward if the car is closer to center line and vice versa
    if distance_from_center <= marker_1:
        reward *= 1.0
    elif distance_from_center <= marker_2:
        reward *= 0.5
    elif distance_from_center <= marker_3:
        reward *= 0.1
    else:
        reward = 1e-3  # likely crashed/ close to off track

    # Steering penality threshold, change the number based on your action space setting
    ABS_STEERING_THRESHOLD = 15 
    # Penalize reward if the car is steering too much
    if abs_steering > ABS_STEERING_THRESHOLD:
        reward *= 0.8
        
    # Give higher reward if the car completes the track
    if progress > 0.7:
        reward = 3.0
    elif progress = 1:
        reward = 10
    else:
        reward = 1e-3  # completion % is not good
        
    ############### from example 04 ####################
        
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
