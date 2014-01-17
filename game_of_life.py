from graphics import *
import random
import cProfile, pstats, StringIO

## Written by Sarina Canelake & Kelly Casteel, August 2010
## Revised January 2011

############################################################
# GLOBAL VARIABLES
############################################################
    
BLOCK_SIZE = 10
BLOCK_OUTLINE_WIDTH = 2
BOARD_WIDTH = 50
BOARD_HEIGHT = 50
count = 0

toad_blocklist = [(4,4), (3,5), (3,6), (5,7), (6,5), (6,6)]
beacon_blocklist = [(2,3), (2,4), (3,3), (3,4), (4,5), (4,6), (5,5), (5,6)]
glider_blocklist = [(1,2), (2,3), (3,1), (3,2), (3,3)]
pulsar_blocklist = [(2,4), (2,5), (2,6), (4,2), (4,7), (5,2), (5,7),
                    (6,2), (6,7), (7,4), (7,5), (7,6), ]
# for diehard, make board at least 25x25, might need to change block size
diehard_blocklist = [(5,7), (6,7), (6,8), (10,8), (11,8), (12,8), (11,6)]

############################################################
# BLOCK CLASS (Read through and understand this part!)
############################################################

class Block(Rectangle):
    ''' Block class:
        Implement a block for a tetris piece
        Attributes: x - type: int
                    y - type: int
        specify the position on the board
        in terms of the square grid
    '''

    def __init__(self, pos, color):
        '''
        pos: a Point object specifing the (x, y) square of the Block (NOT in pixels!)
        color: a string specifing the color of the block (eg 'blue' or 'purple')
        '''
        self.x = pos.x
        self.y = pos.y
        
        p1 = Point(pos.x*BLOCK_SIZE,
                   pos.y*BLOCK_SIZE)
        p2 = Point(p1.x + BLOCK_SIZE, p1.y + BLOCK_SIZE)

        Rectangle.__init__(self, p1, p2)
        self.setWidth(BLOCK_OUTLINE_WIDTH)
        self.setFill(color)
        self.status = 'dead'
        self.new_status = 'None'
        self.live_neighbor_count = 0
        
    def get_coords(self):
        return (self.x, self.y)

    def set_live(self, canvas):
        '''
        Sets the block status to 'live' and draws it on the grid.
        Be sure to do this on the canvas!
        '''
        if self.status=='dead':
          self.status = 'live'
          self.draw(canvas)

    def set_dead(self):
        '''
        Sets the block status to 'dead' and undraws it from the grid.
        '''
        if self.status=='live':
          self.status = 'dead'
          self.undraw()

    def is_live(self):
        '''
        Returns True if the block is currently 'live'. Returns False otherwise.
        '''
        if self.status == 'live':
            return True
        return False

    def reset_status(self, canvas):
        '''
        Sets the new_status to be the current status
        '''
        if self.new_status=='dead':
            self.set_dead()
        elif self.new_status=='live':
            self.set_live(canvas)
        self.live_neighbor_count = 0

    def set_new_status(self):
        if self.status == 'live':
            if 2 <= self.live_neighbor_count <= 3:
                self.new_status = 'live'
            else: self.new_status = 'dead'
        else:
            if self.live_neighbor_count == 3:
                self.new_status = 'live'
            else: self.new_status = 'dead'
        

###########################################################
# BOARD CLASS (Read through and understand this part!)
# Print out and turn in this section.
# Name:
# Recitation:
###########################################################

class Board(object):
    ''' Board class: it represents the Game of Life board

        Attributes: width - type:int - width of the board in squares
                    height - type:int - height of the board in squares
                    canvas - type:CanvasFrame - where the blocks will be drawn
                    block_list - type:Dictionary - stores the blocks for a given position
    '''
    
    def __init__(self, win, width, height):
        self.width = width
        self.height = height
        self.win = win
        # self.delay is the number of ms between each simulation. Change to be
        # shorter or longer if you wish!
        self.delay = 5

        # create a canvas to draw the blocks on
        self.canvas = CanvasFrame(win, self.width * BLOCK_SIZE,
                                       self.height * BLOCK_SIZE)
        self.canvas.setBackground('white')

        # initialize grid lines
        for x in range(1,self.width):
            self.draw_gridline(Point(x, 0), Point(x, self.height))

        for y in range(1,self.height):
            self.draw_gridline(Point(0, y), Point(self.width, y))

        self.block_list = {}

        for x in range(self.width):
            for y in range(self.height):
                self.block_list[(x, y)] = Block(Point(x, y), 'blue')

        ####### YOUR CODE HERE ######
#        raise Exception("__init__ not implemented")


    def draw_gridline(self, startp, endp):
        ''' Parameters: startp - a Point of where to start the gridline
                        endp - a Point of where to end the gridline
            Draws two straight 1 pixel lines next to each other, to create
            a nice looking grid on the canvas.
        '''
        line = Line(Point(startp.x*BLOCK_SIZE, startp.y*BLOCK_SIZE), \
                    Point(endp.x*BLOCK_SIZE, endp.y*BLOCK_SIZE))
        line.draw(self.canvas)
        
        line = Line(Point(startp.x*BLOCK_SIZE-1, startp.y*BLOCK_SIZE-1), \
                    Point(endp.x*BLOCK_SIZE-1, endp.y*BLOCK_SIZE-1))
        line.draw(self.canvas)


    def random_seed(self, percentage):
        ''' Parameters: percentage - a number between 0 and 1 representing the
                                     percentage of the board to be filled with
                                     blocks
            This method activates the specified percentage of blocks randomly.
        '''
        for block in self.block_list.values():
            if random.random() < percentage:
                block.set_live(self.canvas)

    def seed(self, block_coords):
        '''
        Seeds the board with a certain configuration.
        Takes in a list of (x, y) tuples representing block coordinates,
        and activates the blocks corresponding to those coordinates.
        '''

        for block in block_coords:
            self.block_list[block].set_live(self.canvas)

    def get_block_neighbors(self, block):
        '''
        Given a Block object, returns a list of neighboring blocks.
        Should not return itself in the list.
        '''

        x, y = block.get_coords()
        for x_offset in [-1, 0, 1]:
            for y_offset in [-1, 0, 1]:
                if (x+x_offset, y+y_offset) in self.block_list.keys() and (x_offset != 0 or y_offset != 0):
                    yield self.block_list[x+x_offset, y+y_offset]
        
    def get_live_neighbor_count(self, neighbors):
        live_count = 0
        for block in neighbors:
           if block.status == 'live':
                live_count += 1
        return live_count

    def get_live_neighbor_count(self, block):
        live_count = 0
        x, y = block.get_coords()
        for x_offset in [-1, 0, 1]:
            for y_offset in [-1, 0, 1]:
                if (x+x_offset, y+y_offset) in self.block_list.keys() and (x_offset != 0 or y_offset != 0):
                    if self.block_list[x+x_offset, y+y_offset].status == 'live':
                        live_count += 1
        return live_count

    def update_live_block_neighbors(self):
        blocks = self.block_list.values()
        for block in blocks:
            if block.status == 'live':
                for neighbor in self.get_block_neighbors(block):
                    neighbor.live_neighbor_count += 1
        for block in blocks:
            block.set_new_status()
        for block in blocks:
            block.reset_status(self.canvas)

    def simulate(self):
        '''
        Executes one turn of Conways Game of Life using the rules
        listed in the handout. Best approached in a two-step strategy:
        
        1. Calculate the new_status of each block by looking at the
           status of its neighbors.

        2. Set blocks to 'live' if their new_status is 'live' and their
           status is 'dead'. Similarly, set blocks to 'dead' if their
           new_status is 'dead' and their status is 'live'. Then, remember
           to call reset_status(self.canvas) on each block.
        '''

        self.update_live_block_neighbors()



    def animate(self):
        '''
        Animates the Game of Life, calling "simulate"
        once every second
        '''
        self.simulate()
        global count
        count += 1
        if count < 100:
            self.win.after(self.delay, self.animate)
        else:
            self.canvas.close()



################################################################
# RUNNING THE SIMULATION
################################################################

if __name__ == '__main__':    
    # Initalize board
    win = Window("Conway's Game of Life")
    board = Board(win, BOARD_WIDTH, BOARD_HEIGHT)
   
    pr = cProfile.Profile()
    pr.enable()

    board.random_seed(.15)
    board.animate()    
    win.mainloop()

    pr.disable()
    s = StringIO.StringIO()
    sortby = 'cumulative'
    ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
    ps.print_stats()
    print s.getvalue()

