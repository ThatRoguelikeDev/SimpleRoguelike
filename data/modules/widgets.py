################
#
# Widget Module
#
################

class Button:
    """ A button widget. """
    def __init__(self, x, y, text, color, action):

        self.x = x
        self.y = y
        self.text = text
        self.w = x+len(text)/2
        self.h = y+1
        self.color = color
        self.action = action

    def selected(self, mouse):
        """ Detects if the mouse is hovered over the button, if so, returns true. """

        if mouse.cx >= self.x-(len(self.text)/2)-1 and mouse.cx <= self.w and mouse.cy >= self.y-1 and mouse.cy <= self.h:

            self.color[0] = self.color[2]
            return True

        else:

            self.color[0] = self.color[1]
            return False

    def detect_click(self, mouse):
        """ Detects mouse click then actives the buttons action. """

        if self.selected(mouse) and mouse.lbutton_pressed:

            return True