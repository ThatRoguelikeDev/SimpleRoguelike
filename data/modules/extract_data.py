################
#
# Parser Module
#
################

# Imports.
import libtcodpy as roguelib

# Dictionaries that hold all the info parsed from the data file.
tile_data = {}

# Listener.
CURRENT_PROPERTIES = []


class Listener:
    """ Grabs values from parser. """

    def new_struct(self, struct, name):
        """ Grabs all scructs. """

        return True

    def new_flag(self, name):
        """ Grabs all flags. """

        print('new flag named ', name)
        return True

    def new_property(self,name, typ, value):
        """ Grabs all properties. """

        type_names = ['NONE', 'BOOL', 'CHAR', 'INT', 'FLOAT', 'STRING',
                      'COLOR', 'DICE']

        if typ == roguelib.TYPE_COLOR:
            print('new property named ', name, ' type ', type_names[typ], ' value ', value.r, value.g, value.b)

        elif typ == roguelib.TYPE_DICE:
            print('new property named ', name, ' type ', type_names[typ], ' value ', value.nb_rolls,
                  value.nb_faces, value.multiplier, value.addsub)

        else:

            # Add property to properties list.
            CURRENT_PROPERTIES.append({name: value})

        return True

    def end_struct(self, struct, name):
        """ End of struct, adds data to appropriate dictionary. """

        global CURRENT_PROPERTIES

        # If struct name is 'tile'.
        if roguelib.struct_get_name(struct) == b'tile':

            # Create dictionary.
            tile_data[name] = {}

            # Add properties to dictionary.
            for i in range(len(CURRENT_PROPERTIES)):

                keys = CURRENT_PROPERTIES[i].keys()
                values = CURRENT_PROPERTIES[i].values()

                for key in keys:

                    for value in values:

                        tile_data[name][key] = value

    def error(self, msg):
        """ Reads out errors. """

        print('error : ', msg)

        return True


# Parser.
# Create parser.
parser = roguelib.parser_new()

# Create structs
tile_type_struct = roguelib.parser_new_struct(parser, b'tile')

# Add properties.
# Tile properties.
roguelib.struct_add_property(tile_type_struct, b'IMAGE', roguelib.TYPE_CHAR, True)
roguelib.struct_add_property(tile_type_struct, b'SOLID', roguelib.TYPE_BOOL, True)
roguelib.struct_add_property(tile_type_struct, b'BLOCKS_SIGHT', roguelib.TYPE_BOOL, True)
roguelib.struct_add_property(tile_type_struct, b'ALWAYS_VISIBLE', roguelib.TYPE_BOOL, True)
roguelib.struct_add_property(tile_type_struct, b'COLOR', roguelib.TYPE_STRING, True)
roguelib.struct_add_property(tile_type_struct, b'DESCRIPTION', roguelib.TYPE_STRING, True)

# Run parser.
roguelib.parser_run(parser, b'data\game_data.txt', Listener())

# Delete parser.
roguelib.parser_delete(parser)

