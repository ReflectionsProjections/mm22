import physics


class GameMap:

    def __init__(self):

        # List of line segements that define walls in the game
        self.walls = []

    def in_vision_of(self, character_1, character_2):
        """ Determines if two characters can see each other
        :param character_1: One of the characters
        :param character_2: The other character
        :return: True if yes, False is no
        """


