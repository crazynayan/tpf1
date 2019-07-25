import json


class _Command:
    # The _Command class is an internal class and should NOT be imported.
    # Import the instance of the class declared at the bottom.
    def __init__(self):
        try:
            with open('v1/commands.json') as json_file:
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

    def get_text(self, command, condition, opposite=False):
        """
        Return the text of a condition
        :param command: The compare command (CLC, SR, OI) which has a condition
        :param condition: The condition associated with the command (BZ, JNZ)
        :param opposite: If True then return the text for its opposite condition
        :return: text for the condition and the operator for math instruction
        """
        if command not in self._data or condition not in self._data:
            return '', ''
        if opposite and 'opposite' in self._data[condition] and self._data[condition]['opposite']:
            condition = self._data[condition]['opposite']
        text_condition = self._data[condition]['text'] if self._data[condition]['text'] else ''
        text_operator = ''
        if 'branch_type' in self._data[command]:
            if self._data[command]['branch_type'] in self._data[condition]:
                text_condition = self._data[condition][self._data[command]['branch_type']]
            if self._data[command]['branch_type'] in self._data[command]:
                text_operator = self._data[command][self._data[command]['branch_type']]
        return text_condition, text_operator

    def get_operator(self, condition, opposite=False):
        if condition not in self._data:
            return ''
        if opposite and 'opposite' in self._data[condition] and self._data[condition]['opposite']:
            condition = self._data[condition]['opposite']
        return self._data[condition]['operator'] if 'operator' in self._data[condition] else ''


# This is the cmd object which needs to be imported by other applications.
cmd = _Command()
