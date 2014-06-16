####################
#
# Simple Roguelike
#
# Version 0.4
#
# 2/18/14
#
####################

# Imports, add a path to stored modules.
import sys
import textwrap

sys.path.append('data/modules/')
import libtcodpy as roguelib
import widgets
import extract_data as parser


# Load parsed data
TILE_DATA = parser.tile_data
SETTING_DATA = parser.setting_data

# Constants.
# Screen/Map constants.
SCREEN_WIDTH = 90
SCREEN_HEIGHT = 60
MAP_WIDTH = 90
MAP_HEIGHT = 46

# GUI constants.
CONSOLE_GUI_HEIGHT = 5
CONSOLE_GUI_Y = SCREEN_HEIGHT - CONSOLE_GUI_HEIGHT
BAR_WIDTH = 20
MESSAGE_CONSOLE_HEIGHT = 13
MESSAGE_CONSOLE_WIDTH = 65
MESSAGE_CONSOLE_Y = SCREEN_HEIGHT - MESSAGE_CONSOLE_HEIGHT

# FOV constants.
TORCH_RADIUS = SETTING_DATA[b"Game Settings"][b"TORCH_RADIUS"]
FOV_LIGHT_WALLS = True
FOV_ALGO = roguelib.FOV_BASIC

# Dungeon building constants.
ROOM_MIN_SIZE = SETTING_DATA[b"Game Settings"][b"ROOM_MIN_SIZE"]
ROOM_MAX_SIZE = SETTING_DATA[b"Game Settings"][b"ROOM_MAX_SIZE"]
MAX_ROOMS = SETTING_DATA[b"Game Settings"][b"MAX_ROOMS"]

# Game Save Data.
LEVELS = {}

# Classes
# Object Classes.
class Object():
    def __init__(self, x, y, name, image, color, solid, blocks_sight, explored=False, alive=False):
        """ Initiates the class. """

        self.x = x
        self.y = y
        self.name = name
        self.image = image
        self.color = color
        self.solid = solid
        self.blocks_sight = blocks_sight
        self.explored = explored
        self.alive = alive


class Alive():
    def __init__(self, hp, maxhp, energy, maxenergy):
        """ Initiates the class. """

        self.hp = hp
        self.maxhp = maxhp
        self.energy = energy
        self.maxenergy = maxenergy


# Dungeon Building Classes.
class Rect():
    """ A rectangle that represents a room. """

    def __init__(self, x, y, w, h):
        """ Initiates the class. """

        self.x1 = x
        self.y1 = y
        self.x2 = x + w
        self.y2 = y + h

    def center(self):
        """ Finds the center of the room coords and returns the value. """

        center_x = (self.x1 + self.x2) / 2
        center_y = (self.y1 + self.y2) / 2
        return int(center_x), int(center_y)

    def intersect(self, other):
        """ Returns true if this room intersects with another. """

        return (self.x1 <= other.x2 and self.x2 >= other.x1 and
                self.y1 <= other.y2 and self.y2 >= other.y1)


# Dungeon Building Functions
def make_dungeon():
    """ Makes a dungeon level. """

    # Set globals.
    global dstairs, astairs

    # Fills dungeon with walls.
    for x in range(MAP_WIDTH + 1):

        for y in range(MAP_HEIGHT - CONSOLE_GUI_HEIGHT + 1):
            objects.append(Object(x, y + CONSOLE_GUI_HEIGHT, "Stone Wall",
                                  TILE_DATA[b'Stone Wall'][b'IMAGE'], eval(TILE_DATA[b'Stone Wall'][b'COLOR']),
                                  TILE_DATA[b'Stone Wall'][b'SOLID'], TILE_DATA[b'Stone Wall'][b'BLOCKS_SIGHT']))

    # Loops until MAX_ROOMS is met.
    rooms = []
    num_rooms = 0
    for r in range(MAX_ROOMS):

        # Gets size and coords of new room.
        w = roguelib.random_get_int(0, ROOM_MIN_SIZE, ROOM_MAX_SIZE)
        h = roguelib.random_get_int(0, ROOM_MIN_SIZE, ROOM_MAX_SIZE)
        x = roguelib.random_get_int(0, 1, MAP_WIDTH - w - 1)
        y = roguelib.random_get_int(0, CONSOLE_GUI_HEIGHT + 1, MAP_HEIGHT - h - 1)

        # Create room.
        new_room = Rect(x, y, w, h)

        # First room.
        if len(rooms) == 0:

            # Place player in first room.
            player.x, player.y = new_room.center()

            # Create room.
            make_room(new_room)
            rooms.append(new_room)

            # Increase room count.
            num_rooms += 1

        # Not the first room.
        else:

            # Check if new room intersects with any other current rooms.
            failed = False
            for other_room in rooms:

                if new_room.intersect(other_room):
                    failed = True
                    break

            # If new room doesn't intersect with any other rooms.
            if not failed:

                # Create room.
                make_room(new_room)

                # Get center coords of new room.
                new_x, new_y = new_room.center()

                # Get center coords of the last created room.
                prev_x, prev_y = rooms[num_rooms - 1].center()

                # Flip a coin to choose whether to create a horizontal or vertical tunnel first.
                if roguelib.random_get_int(0, 0, 1) == 1:

                    # Create a horizontal tunnel first.
                    create_h_tunnel(prev_x, new_x, prev_y)
                    create_v_tunnel(prev_y, new_y, new_x)

                else:

                    # Create a vertical tunnel first.
                    create_v_tunnel(prev_y, new_y, prev_x)
                    create_h_tunnel(prev_x, new_x, new_y)

                # Add room to list and increase number of rooms.
                rooms.append(new_room)
                num_rooms += 1

    # Place ascending stairs in first room created at a random position if not on the first floor.
    if depth > 1:

        x = roguelib.random_get_int(0, rooms[0].x1, rooms[0].x2 - 1)
        y = roguelib.random_get_int(0, rooms[0].y1, rooms[0].y2 - 1)
        if not is_blocked(x, y):
            astairs = Object(x, y, "Stairs Up", TILE_DATA[b'Stairs Up'][b'IMAGE'],
                             eval(TILE_DATA[b'Stairs Up'][b'COLOR']),
                             TILE_DATA[b'Stairs Up'][b'SOLID'], TILE_DATA[b'Stairs Up'][b'BLOCKS_SIGHT'])
            objects.append(astairs)

    # Place descending stairs in last room created at a random position.
    x = roguelib.random_get_int(0, rooms[len(rooms) - 1].x1, rooms[len(rooms) - 1].x2 - 1)
    y = roguelib.random_get_int(0, rooms[len(rooms) - 1].y1, rooms[len(rooms) - 1].y2 - 1)
    if not is_blocked(x, y):
        dstairs = Object(x, y, "Stairs Down", TILE_DATA[b'Stairs Down'][b'IMAGE'],
                         eval(TILE_DATA[b'Stairs Down'][b'COLOR']),
                         TILE_DATA[b'Stairs Down'][b'SOLID'], TILE_DATA[b'Stairs Down'][b'BLOCKS_SIGHT'])
        objects.append(dstairs)


def make_room(room):
    """ Hollows out a room at the given coords. """

    for x in range(room.x1, room.x2):

        for y in range(room.y1, room.y2):

            for obj in objects:

                if obj.x == x and obj.y == y:
                    obj.name = "Dirt Floor"
                    obj.image = TILE_DATA[b'Dirt Floor'][b'IMAGE']
                    obj.color = eval(TILE_DATA[b'Dirt Floor'][b'COLOR'])
                    obj.blocks_sight = TILE_DATA[b'Dirt Floor'][b'BLOCKS_SIGHT']
                    obj.solid = TILE_DATA[b'Dirt Floor'][b'SOLID']


def create_h_tunnel(x1, x2, y):
    """ Creates a horizontal tunnel at the given coords. """

    for x in range(min(x1, x2), max(x1, x2) + 1):

        for obj in objects:

            if obj.x == x and obj.y == y:
                obj.name = "Dirt Floor"
                obj.image = TILE_DATA[b'Dirt Floor'][b'IMAGE']
                obj.color = eval(TILE_DATA[b'Dirt Floor'][b'COLOR'])
                obj.blocks_sight = TILE_DATA[b'Dirt Floor'][b'BLOCKS_SIGHT']
                obj.solid = TILE_DATA[b'Dirt Floor'][b'SOLID']


def create_v_tunnel(y1, y2, x):
    """ Creates a vertical tunnel at the given coords. """

    for y in range(min(y1, y2), max(y1, y2) + 1):

        for obj in objects:

            if obj.x == x and obj.y == y:
                obj.name = "Dirt Floor"
                obj.image = TILE_DATA[b'Dirt Floor'][b'IMAGE']
                obj.color = eval(TILE_DATA[b'Dirt Floor'][b'COLOR'])
                obj.blocks_sight = TILE_DATA[b'Dirt Floor'][b'BLOCKS_SIGHT']
                obj.solid = TILE_DATA[b'Dirt Floor'][b'SOLID']


def is_blocked(x, y):
    """ Returns True if the given coords are blocked. """

    for obj in objects:

        if obj.solid and obj.x == x and obj.y == y:
            return True

    return False


# Rendering Functions.
def render_all():
    """ Renders everything on screen. """

    # Set globals.
    global fov_recompute

    # Clear root console.
    roguelib.console_clear(0)

    # Display mouse location if in FOV.
    mouse, key = check_for_key_events()
    if roguelib.map_is_in_fov(fov_map, mouse.cx, mouse.cy):
        roguelib.console_put_char_ex(0, mouse.cx, mouse.cy, " ", None, eval(SETTING_DATA[b"Mouse Highlight"][b"COLOR"]))

    # Display objects.
    for obj in objects:

        visible = roguelib.map_is_in_fov(fov_map, obj.x, obj.y)

        # Out of FOV.
        if not visible:

            if obj.explored:

                roguelib.console_set_default_foreground(0, obj.color[1])
                roguelib.console_put_char(0, obj.x, obj.y, obj.image, roguelib.BKGND_NONE)

        # In FOV.
        else:

            roguelib.console_set_default_foreground(0, obj.color[0])
            roguelib.console_put_char(0, obj.x, obj.y, obj.image, roguelib.BKGND_NONE)
            obj.explored = True

    # Recompute FOV if fov_recompute is True.
    if fov_recompute:

        fov_recompute = False
        roguelib.map_compute_fov(fov_map, player.x, player.y, TORCH_RADIUS, FOV_LIGHT_WALLS, FOV_ALGO)

    # Display player.
    roguelib.console_set_default_foreground(0, roguelib.white)
    roguelib.console_put_char(0, player.x, player.y, player.image, roguelib.BKGND_NONE)

    # Render the gui.
    render_gui()

    # Flush the root console.
    roguelib.console_flush()


def render_bar(console, x, y, total_width, name, value, maximum, bar_color, back_color, text_color):
    """ Renders a bar, such as a health bar. """

    # Calculate bar width.
    bar_width = int(float(value) / maximum * total_width)

    # Display background of bar.
    roguelib.console_set_default_background(console, back_color)
    roguelib.console_rect(console, x, y, total_width, 1, False, roguelib.BKGND_SCREEN)

    # Display bar.
    roguelib.console_set_default_background(console, bar_color)
    roguelib.console_rect(console, x, y, bar_width, 1, False, roguelib.BKGND_SCREEN)

    # Display text over bar.
    roguelib.console_set_default_foreground(console, text_color)
    roguelib.console_print_ex(console, int(x + total_width / 2), y, roguelib.BKGND_NONE, roguelib.CENTER,
                              name + ':' + str(value) + "/" + str(maximum))


def render_window(console, x, y, w, h, color):
    """ Renders a border around the given area. """

    # Set color for printing.
    roguelib.console_set_default_foreground(console, color)

    # Corners
    roguelib.console_print(console, x, y, chr(201))
    roguelib.console_print(console, x + w, y, chr(187))
    roguelib.console_print(console, x, y + h, chr(200))
    roguelib.console_print(console, x + w, y + h, chr(188))

    # The rest.
    for xx in range(w - 1):
        roguelib.console_print(console, x + xx + 1, y, chr(205))
        roguelib.console_print(console, x + xx + 1, y + h, chr(205))

    for yy in range(h - 1):
        roguelib.console_print(console, x, y + yy + 1, chr(186))
        roguelib.console_print(console, x + w, y + yy + 1, chr(186))


def render_gui():
    """ Renders just the gui. """

    # Set globals.
    global turns, game_messages

    # Clear console before drawing on it.
    roguelib.console_set_default_background(console_gui, roguelib.black)
    roguelib.console_clear(console_gui)

    # Display health and energy bars for player.
    render_bar(console_gui, 1, 1, BAR_WIDTH, "HP", player.alive.hp, player.alive.maxhp, roguelib.dark_flame,
               roguelib.dark_grey, roguelib.white)
    render_bar(console_gui, 1, 3, BAR_WIDTH, "Energy", player.alive.energy, player.alive.maxenergy, roguelib.dark_green,
               roguelib.dark_grey, roguelib.white)

    # Prints number of turns and dungeon level on screen.
    roguelib.console_set_default_foreground(console_gui, eval(SETTING_DATA[b"Text Color"][b"COLOR"]))
    roguelib.console_print(console_gui, SCREEN_WIDTH - 15, 2, "Turns:" + str(turns))
    roguelib.console_print(console_gui, SCREEN_WIDTH // 2, 2, "Depth:" + str(depth))

    # Display messages in message box.
    y = 1
    for (line, color) in game_messages:
        roguelib.console_set_default_foreground(console_message, color)
        roguelib.console_print_ex(console_message, 0, y, roguelib.BKGND_NONE, roguelib.LEFT, line)
        y += 1

    # Blit contents of consoles to screen.
    roguelib.console_blit(console_gui, 0, 0, SCREEN_WIDTH, CONSOLE_GUI_HEIGHT, 0, 0, 0)
    roguelib.console_blit(console_message, 0, 0, SCREEN_WIDTH, MESSAGE_CONSOLE_HEIGHT, 0, 0, MESSAGE_CONSOLE_Y)


def create_message(message, color):
    """ Creates a message to be displayed in the message box. """

    # Set globals.
    global game_messages

    new_message = textwrap.wrap("- " + message, MESSAGE_CONSOLE_WIDTH)

    for line in reversed(new_message):

        if len(game_messages) > MESSAGE_CONSOLE_HEIGHT:
            del game_messages[0]

        game_messages.insert(0, (line, color))


def compute_fov():
    """ Computes FOV. """

    # Set globals.
    global fov_recompute, fov_map

    fov_recompute = True

    # Create FOV map.
    fov_map = roguelib.map_new(MAP_WIDTH, MAP_HEIGHT + 1)
    for obj in objects:
        roguelib.map_set_properties(fov_map, obj.x, obj.y, not obj.blocks_sight, not obj.solid)


def descend():
    """ Decends down the stairs, creating a new map and saving the old one. """

    # Set globals.
    global objects, depth, dstairs, astairs

    # Save current depth's objects.
    LEVELS[depth] = objects

    # Clear objects in current dungeon.
    objects = []

    # Increase the depth
    depth += 1

    # If player has been to this depth before, reload old dungeon.
    try:

        # Grab saved objects from dungeon.
        objects = LEVELS[depth]

        # Reset stair positions.
        for obj in objects:

            if obj.name == dstairs.name:
                dstairs = obj

            if obj.name == astairs.name:
                astairs = obj

        # Set the player's position close to the descending stairs.
        while True:

            # Get random position near stairs.
            x = astairs.x + roguelib.random_get_int(0, -1, 1)
            y = astairs.y + roguelib.random_get_int(0, -1, 1)

            # If position is free, move player there and break the loop.
            if not is_blocked(x, y) and x != astairs.x and y != astairs.y:
                player.x = x
                player.y = y
                break

    # If player has not been to this depth yet, create a new dungeon.
    except KeyError:

        make_dungeon()

    # Compute new FOV.
    compute_fov()


def ascend():
    """ Ascends up the stairs, recreating a saved map. """

    # Set globals.
    global objects, depth, dstairs, astairs

    # Save current depth's objects.
    LEVELS[depth] = objects

    # Clear objects in current dungeon.
    objects = []

    # Decrease the depth.
    depth -= 1

    # Load previous dungeon's objects.
    objects = LEVELS[depth]

    # Reset stair positions.
    for obj in objects:

        if obj.name == dstairs.name:
            dstairs = obj

        if obj.name == astairs.name:
            astairs = obj

    # Set the player's position close to the descending stairs.
    while True:

        # Get random position near stairs.
        x = dstairs.x + roguelib.random_get_int(0, -1, 1)
        y = dstairs.y + roguelib.random_get_int(0, -1, 1)

        # If position is free, move player there and break the loop.
        if not is_blocked(x, y) and x != dstairs.x and y != dstairs.y:
            player.x = x
            player.y = y
            break

    # Compute new FOV.
    compute_fov()


# Player functions.
def check_for_key_events():
    """ Check for all key events. """

    # Set mouse and keys.
    mouse = roguelib.Mouse()
    key = roguelib.Key()

    # Check for events.
    roguelib.sys_check_for_event(roguelib.EVENT_KEY_PRESS | roguelib.EVENT_MOUSE, key, mouse)

    # Return events.
    return mouse, key


def handle_input():
    """ Responds to input from player. """

    # Get key control events.
    mouse, key = check_for_key_events()

    if mouse.lbutton_pressed:

        if roguelib.map_is_in_fov(fov_map, mouse.cx, mouse.cy):
            move_player(mouse.cx, mouse.cy)

    # Movement.
    if key.vk == roguelib.KEY_KP8:

        move_player(player.x, player.y - 1)

    elif key.vk == roguelib.KEY_KP7:

        move_player(player.x - 1, player.y - 1)

    elif key.vk == roguelib.KEY_KP9:

        move_player(player.x + 1, player.y - 1)

    elif key.vk == roguelib.KEY_KP2:

        move_player(player.x, player.y + 1)

    elif key.vk == roguelib.KEY_KP1:

        move_player(player.x - 1, player.y + 1)

    elif key.vk == roguelib.KEY_KP3:

        move_player(player.x + 1, player.y + 1)

    elif key.vk == roguelib.KEY_KP4:

        move_player(player.x - 1, player.y)

    elif key.vk == roguelib.KEY_KP6:

        move_player(player.x + 1, player.y)

    # Clear screen, exit back to main menu.
    if key.vk == roguelib.KEY_ESCAPE:

        roguelib.console_clear(0)
        return True


def move_player(x, y):
    # Set globals.
    global turns, fov_recompute

    # Create path.
    player_path = roguelib.path_new_using_map(fov_map, 1.41)

    # Compute path to walk.
    roguelib.path_compute(player_path, player.x, player.y, x, y)

    while not roguelib.path_is_empty(player_path):

        xx, yy = roguelib.path_walk(player_path, True)

        if not is_blocked(xx, yy):
            # Move player.
            player.x = xx
            player.y = yy

            # Increase turns.
            turns += 1

            # Recompute FOV.
            fov_recompute = True

def run_game():
    """ Starts the game. """

    # Set globals.
    global player, objects, turns, depth, game_messages, fov_map, console_gui, console_message

    # Create player.
    player_alive = Alive(10, 10, 10, 10)
    player = Object(20, 10, "Player", "@", [roguelib.white, roguelib.dark_grey], True, False, alive=player_alive)

    # Create objects list.
    objects = []

    # Set global turns.
    turns = 0
    depth = 1
    game_messages = []
    create_message("Welcome to the Simple Roguelike.", roguelib.red)

    # Generate dungeon.
    make_dungeon()

    # Create FOV.
    compute_fov()

    # Create top and bottom gui consoles.
    console_gui = roguelib.console_new(SCREEN_WIDTH, CONSOLE_GUI_HEIGHT)
    console_message = roguelib.console_new(SCREEN_WIDTH, MESSAGE_CONSOLE_HEIGHT)

    # Create loop for the game to run.
    while not roguelib.console_is_window_closed():

        # Render graphics.
        render_all()

        # If player is on stairs, descend or ascend.
        if player.x == dstairs.x and player.y == dstairs.y:
            descend()

        if depth > 1:

            if player.x == astairs.x and player.y == astairs.y:
                ascend()

        # If leave_game is raised, exit game.
        leave_game = handle_input()
        if leave_game:

            break

def main_menu():
    """ Runs the main menu of the game. """

    # Create buttons.
    widgets_list = [widgets.Button(int(SCREEN_WIDTH/2), 15, "Start Game",
                                   eval(SETTING_DATA[b"Button Color"][b"COLOR"]), "run_game()"),
                    widgets.Button(int(SCREEN_WIDTH/2), 18, "Exit",
                                   eval(SETTING_DATA[b"Button Color"][b"COLOR"]), "exit()")]

    # Create loop for the menu to run.
    while not roguelib.console_is_window_closed():

        title = SETTING_DATA[b"Title Text"][b"TEXT"]

        # Display title+widgets.
        roguelib.console_set_default_foreground(0, eval(SETTING_DATA[b"Title Color"][b"COLOR"]))
        roguelib.console_print_ex(0, int(SCREEN_WIDTH / 2), 5,
                                  roguelib.BKGND_NONE, roguelib.CENTER, title)

        for widget in widgets_list:

            roguelib.console_set_default_foreground(0, widget.color[0])
            roguelib.console_print_ex(0, widget.x, widget.y, roguelib.BKGND_NONE,
                                      roguelib.CENTER, widget.text)

        roguelib.console_flush()

        # Get key control events.
        mouse, key = check_for_key_events()

        # Check for widget actions.
        for widget in widgets_list:

            widget.selected(mouse)
            if widget.detect_click(mouse):

                eval(widget.action)

        # If enter is pressed, start game.
        if key.vk == roguelib.KEY_ENTER:

            run_game()
            break

        # If escape is pressed, exit game.
        if key.vk == roguelib.KEY_ESCAPE:

            break

# Set font.
font = b"data\\fonts\\terminal12x12_gs_ro.png"
roguelib.console_set_custom_font(font, roguelib.FONT_LAYOUT_ASCII_INROW)

# Initiate game window.
roguelib.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, SETTING_DATA[b"Title Text"][b"TEXT"], False, roguelib.RENDERER_SDL)

# Set fps.
roguelib.sys_set_fps(SETTING_DATA[b"Game Settings"][b"FPS"])

# Start game.
main_menu()