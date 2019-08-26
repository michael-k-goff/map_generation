from sda import *

# Hyperparameters related to the map.
num_room_attempts = 100 # Number of times we try to place a room in generating the map.

# A single room in the map
class Room:
    def __init__(self,l,r,b,t):
        self.border = [l,r,b,t]
    # Check for overlap
    # Return True if no overlap, False if overlap
    def check_conflict(self, new_room):
        return self.border[0] >= new_room.border[1] or self.border[1] <= new_room.border[0] or self.border[2] >= new_room.border[3] or self.border[3] <= new_room.border[2]
    
# Make the map
# s is an SDA, method tells us how to generate the bits.
# Options for method include "SDA", which uses the SDA, and "Random", which uses random bits
# Other options might be added in the future
# Note that if method is "Random", we will need a value for S, which could just as well be None.
def generate_map(s,method):
    if method == "SDA":
        s.reset()
    rooms = [0]*num_room_attempts
    rooms[0] = Room(-2,2,-2,2) # Initial room.
    num_rooms = 1
    
    # Attempt to add rooms. num_room_attempts is only the theoretical maximum number of rooms that will result.
    for i in range(num_room_attempts):
        # Step 1 in Part B.
        base_room = get_num(8,s,method) % num_rooms
        
        # Step 2 in Part B
        # [0,0] is left, [1,0] is right, [0,1] is down, [1,1] is up
        next_direction = get_bits(2,s,method)
        
        # Step 3 in Part B
        is_corridor = (get_num(3,s,method) == 0)
        
        # Step 4 in Part B
        dims = [0,0] # [Horizontal, Vertical]
        if (is_corridor and not next_direction[1]):
            dims = [max(4,get_num(4,s,method)),1]
        if (is_corridor and next_direction[1]):
            dims = [1,max(4,get_num(4,s,method))]
        if (not is_corridor):
            dims = [max(2,1+get_num(2,s,method)),max(2,1+get_num(2,s,method))]
            
        # Step 5: Offset
        # I don't see this described in the paper.
        offset_num = get_num(4,s,method)
        if (not next_direction[1]):
            offset_min, offset_max = 1-dims[1], rooms[base_room].border[3]-rooms[base_room].border[2]
        if (next_direction[1]):
            offset_min, offset_max = 1-dims[0], rooms[base_room].border[1]-rooms[base_room].border[0]
        offset = offset_num % (offset_max-offset_min) + offset_min
        
        # With all the parameters set, figure out the location of the new room.
        next_border = [0,0,0,0]
        if (not next_direction[1]):
            next_border[2] = rooms[base_room].border[2]+offset
            next_border[3] = next_border[2] + dims[1]
            if (not next_direction[0]):
                next_border[1] = rooms[base_room].border[0]
                next_border[0] = next_border[1]-dims[0]
            else:
                next_border[0] = rooms[base_room].border[1]
                next_border[1] = next_border[0]+dims[0]
        if (next_direction[1]):
            next_border[0] = rooms[base_room].border[0]+offset
            next_border[1] = next_border[0] + dims[0]
            if (not next_direction[0]):
                next_border[3] = rooms[base_room].border[2]
                next_border[2] = next_border[3]-dims[1]
            else:
                next_border[2] = rooms[base_room].border[3]
                next_border[3] = next_border[2]+dims[1]
        new_room = Room(next_border[0], next_border[1], next_border[2], next_border[3])
        
        # Check if there is a conflict with previous rooms
        is_overlap = False
        for j in range(num_rooms):
            if not rooms[j].check_conflict(new_room):
                is_overlap = True
        
        # Add the new room only if there is no conflict.
        if not is_overlap:
            rooms[num_rooms] = new_room
            num_rooms += 1
    return rooms[:num_rooms]
    
# Map and SDA evaluation

# Get, in map blocks, the left, right, bottom, and top extremes of the map
def get_envelope(rooms):
    if len(rooms) == 0:
        return [0,0,0,0] # Should not happen because there should be at least one room by construction
    else:
        l = min([rooms[i].border[0] for i in range(len(rooms))])
        r = max([rooms[i].border[1] for i in range(len(rooms))])
        b = min([rooms[i].border[2] for i in range(len(rooms))])
        t = max([rooms[i].border[3] for i in range(len(rooms))])
        return [l,r,b,t]
    
# Sum total of the areas of all rooms.
def get_area(rooms):
    return sum([(rooms[i].border[1]-rooms[i].border[0])*(rooms[i].border[3]-rooms[i].border[2]) for i in range(len(rooms))])

# Score a map. We have several scoring functions

# Favor compact maps with lots of rooms. This is the evaluation function used in the paper.
def evaluate_map_compact(rooms):
    # Calculate a score of the fitness of the map
    env = get_envelope(rooms)
    return get_area(rooms)**2 / float((env[1]-env[0])*(env[3]-env[2]))

# Favor sprawling maps
def evaluate_map_sprawl(rooms):
    env = get_envelope(rooms)
    return (env[1]-env[0])*(env[3]-env[2])

def evaluate_map(rooms):
    # Change depending on what kind of maps we want to build
    return evaluate_map_compact(rooms)

# Score an SDA by generating a map from it and scoring the map
def evaluate_sda(s):
    rooms = generate_map(s,"SDA")
    return evaluate_map(rooms)