import json


class _Command:
    # The _Command class is an internal class and should NOT be imported.
    # Import the instance of the class declared at the bottom.
    def __init__(self):
        try:
            with open('commands.json') as json_file:
                self._data = json.load(json_file)
        except FileNotFoundError:
            self._data = None

    def check(self, command, attribute):
        """
        Return the attribute value for the command parameter provided.
        :param command: It is the 1st level key in the json file
        :param attribute: It is the 2nd level key in the json file
        :return: The attribute value from the json file for that command.
                 Return False, if command or attribute not found
        """
        if command not in self._data:
            return False
        if attribute not in self._data[command]:
            return False
        return self._data[command][attribute]


# This is the cmd object which needs to be imported by other applications.
cmd = _Command()
