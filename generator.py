# Generator class

from map import *
from sda import *

# gen is the generation object, mostly likely an SDA.
# method is either "SDA" or "Random".
# If method is "Random", gen is ignored.
# If method is "SDA", then gen is the SDA which generates maps.
class Generator:
    def __init__(self, gen, method):
        self.gen = gen
        self.method = method

    # Get multiple bits for map generation
    def get_bits(self, n):
        if self.method == "SDA":
            return self.gen.get_bits(n)
        else:
            return [random.randint(0,1) for i in range(n)]

    # A wrapper around get_bits that coverts to an integer from 0 to 2^n-1
    def get_num(self,n):
        bits = self.get_bits(n)
        return sum([bits[i]*2**i for i in range(len(bits)) ])

    # Make the map
    # s is an SDA, method tells us how to generate the bits.
    # Options for method include "SDA", which uses the SDA, and "Random", which uses random bits
    # Other options might be added in the future
    # Note that if method is "Random", we will need a value for s, which could just as well be None.
    def generate_map(self):
        if self.method == "SDA":
            self.gen.reset()
        rooms = [0]*num_room_attempts
        rooms[0] = Room(-2,2,-2,2) # Initial room.
        num_rooms = 1

        # Attempt to add rooms. num_room_attempts is only the theoretical maximum number of rooms that will result.
        for i in range(num_room_attempts):
            # Step 1 in Part B.
            base_room = self.get_num(8) % num_rooms

            # Step 2 in Part B
            # [0,0] is left, [1,0] is right, [0,1] is down, [1,1] is up
            next_direction = self.get_bits(2)

            # Step 3 in Part B
            is_corridor = (self.get_num(3) == 0)

            # Step 4 in Part B
            dims = [0,0] # [Horizontal, Vertical]
            if (is_corridor and not next_direction[1]):
                dims = [max(4,self.get_num(4)),1]
            if (is_corridor and next_direction[1]):
                dims = [1,max(4,self.get_num(4))]
            if (not is_corridor):
                dims = [max(2,1+self.get_num(2)),max(2,1+self.get_num(2))]

            # Step 5: Offset
            # I don't see this described in the paper.
            offset_num = self.get_num(4)
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

    # Score by generating a map and scoring
    # Should not be used if method is "Random", as score will not be consistent.
    def evaluate(self):
        map_ = self.generate_map()
        return map_.evaluate()

    # Draw a map by generating it first
    def draw_map(self, filename):
        self.generate_map().draw_map(filename)
