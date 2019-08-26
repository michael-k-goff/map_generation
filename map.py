import png

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
