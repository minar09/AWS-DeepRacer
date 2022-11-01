def reward_function(params):
    '''
    Example of rewarding the agent to stay inside the two borders of the track
    Example of rewarding the agent to follow center line
    Example of rewarding the agent to prevent zigzag

    '''

    # Read input parameters
    all_wheels_on_track = params['all_wheels_on_track']
    distance_from_center = params['distance_from_center']
    track_width = params['track_width']
    progress = params['progress']
    abs_steering = abs(params['steering_angle']) # Only need the absolute steering angle

    # Give a very low reward by default
    reward = 1e-3
    
    # Give a high reward if no wheels go off the track and
    # the agent is somewhere in between the track borders
    if all_wheels_on_track and (0.5*track_width - distance_from_center) >= 0.05:
        reward = 1.0
    elif not all_wheels_on_track:
        reward = -1
    else:
        reward = progress

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

    # Always return a float value
    return float(reward)
