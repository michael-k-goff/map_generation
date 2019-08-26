import png
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

class Map:
    def __init__(self,rooms):
        self.rooms = rooms

    # Get the range (far left, right, bottom, top) that the map covers
    def get_envelope(self):
        if len(self.rooms) == 0:
            return [0,0,0,0] # Should not happen because there should be at least one room by construction
        else:
            l = min([self.rooms[i].border[0] for i in range(len(self.rooms))])
            r = max([self.rooms[i].border[1] for i in range(len(self.rooms))])
            b = min([self.rooms[i].border[2] for i in range(len(self.rooms))])
            t = max([self.rooms[i].border[3] for i in range(len(self.rooms))])
            return [l,r,b,t]
    def get_area(self):
        return sum([(self.rooms[i].border[1]-self.rooms[i].border[0])*(self.rooms[i].border[3]-self.rooms[i].border[2]) for i in range(len(self.rooms))])

    # Evaluation functions

    # Favor compact maps with lots of rooms. This is the evaluation function used in the paper.
    def evaluate_compact(self):
        # Calculate a score of the fitness of the map
        env = self.get_envelope()
        return self.get_area()**2 / float((env[1]-env[0])*(env[3]-env[2]))

    # Favor sprawling maps
    def evaluate_sprawl(self):
        env = self.get_envelope()
        return (env[1]-env[0])*(env[3]-env[2])

    # Overall evaluations function
    def evaluate(self):
        # Change depending on what kind of maps we want to build
        return self.evaluate_compact()

    # Same the map to a file
    def draw_map(self,filename):
        envelope = self.get_envelope()
        if envelope[1]-envelope[0] > 100 or envelope[3]-envelope[2] > 100:
            print("Too big")
            return
        pixels = [[255]*(30*(envelope[1]-envelope[0])) for i in range(10*(envelope[3]-envelope[2]))]

        # Set up the grid
        for i in range(envelope[3]-envelope[2]):
            for j in range(envelope[1]-envelope[0]):
                for k in range(10):
                    pixels[10*i+0][30*j+0+3*k] = 0
                    pixels[10*i+0][30*j+1+3*k] = 0
                    pixels[10*i+0][30*j+2+3*k] = 0

                    pixels[10*i+9][30*j+0+3*k] = 0
                    pixels[10*i+9][30*j+1+3*k] = 0
                    pixels[10*i+9][30*j+2+3*k] = 0

                    pixels[10*i+k][30*j+0] = 0
                    pixels[10*i+k][30*j+1] = 0
                    pixels[10*i+k][30*j+2] = 0

                    pixels[10*i+k][30*j+27] = 0
                    pixels[10*i+k][30*j+28] = 0
                    pixels[10*i+k][30*j+29] = 0

        # Draw the rooms
        for i in range(len(self.rooms)):
            minx = 10*(self.rooms[i].border[0] - envelope[0])+1
            maxx = 10*(self.rooms[i].border[1] - envelope[0])-1
            miny = 10*(self.rooms[i].border[2] - envelope[2])+1
            maxy = 10*(self.rooms[i].border[3] - envelope[2])-1
            for x in range(minx,maxx):
                for y in range(miny,maxy):
                    if i == 0:
                        pixels[y][3*x+0] = 255
                        pixels[y][3*x+1] = 0
                        pixels[y][3*x+2] = 0
                    elif (self.rooms[i].border[1] == self.rooms[i].border[0]+1 or self.rooms[i].border[3] == self.rooms[i].border[2]+1):
                        pixels[y][3*x+0] = 0
                        pixels[y][3*x+1] = 255
                        pixels[y][3*x+2] = 0
                    else:
                        pixels[y][3*x+0] = 0
                        pixels[y][3*x+1] = 0
                        pixels[y][3*x+2] = 255
        # Set up for writing the file
        for i in range(len(pixels)):
            pixels[i] = tuple(pixels[i])
        with open(filename,"wb") as f:
            w = png.Writer(10*(envelope[1]-envelope[0]), 10*(envelope[3]-envelope[2]))
            w.write(f, pixels)


# Make the map
# s is an SDA, method tells us how to generate the bits.
# Options for method include "SDA", which uses the SDA, and "Random", which uses random bits
# Other options might be added in the future
# Note that if method is "Random", we will need a value for s, which could just as well be None.
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
    return Map(rooms[:num_rooms])

# Score an SDA by generating a map from it and scoring the map
def evaluate_sda(s):
    map_ = generate_map(s,"SDA")
    return map_.evaluate()
