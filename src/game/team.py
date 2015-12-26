

class Team:

    def __init__(teamName, classes):
        """ Init a team based off a team id and classes
        :param teamName: (string) name of team
        :param classes: (list) list of class ids for team
        """

        self.teamName = teamName
        self.characters = [ Character(classId) for classId in classes ]

    def toJson():
        """ Returns information about the team as a json
        :return json: (json) 
        """

        json = {}
        for character in self.characters:
            json[character.characterId] = character.toJson()

        return json
