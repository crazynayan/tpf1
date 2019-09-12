import json
import os
from typing import Optional, Tuple

import gspread
from oauth2client.service_account import ServiceAccountCredentials

from config import config


def download_commands() -> None:
    # Use credentials to create a client to interact with the Google Drive API
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']

    credentials = ServiceAccountCredentials.from_json_keyfile_name(config.GAC_KEY_PATH, scope)
    client = gspread.authorize(credentials)

    # Open the work book
    sheet = client.open("tpf1").worksheet("commands")
    command_list = sheet.get_all_records()
    command_dict = dict()
    for command_item in command_list:
        command = command_item['command']
        for key, value in command_item.items():
            if key != 'command' and value != '':
                if command not in command_dict:
                    command_dict[command] = dict()
                command_dict[command][key] = value
    with open(os.path.join(config.ROOT_DIR, 'commands.json'), 'w') as json_file:
        json.dump(command_dict, json_file, ensure_ascii=False, sort_keys=True, indent=4)
    print(command_dict)
    print('File created.')


class _Command:
    # The _Command class is an internal class and should NOT be imported.
    # Import the instance of the class declared at the bottom.
    def __init__(self):
        try:
            with open(os.path.join(config.ROOT_DIR, 'commands.json')) as json_file:
                self._data = json.load(json_file)
        except FileNotFoundError:
            self._data = dict()

    def command_check(self, command: str) -> bool:
        """
        Check whether a command exits or not.
        :param command: It is the 1st level key in the json file
        :return: True if command exits else False
        """
        return True if command in self._data else False

    def get_commands(self, attribute: str, attribute_value: str) -> list:
        """
        Returns a list of commands with a matching attribute
        :param attribute: 2nd level key in the json file
        :param attribute_value: value of the attribute to match
        :return: a list of commands
        """
        return [command for command, attributes in self._data.items()
                if attribute in attributes and attributes[attribute] == attribute_value]

    def check(self, command: str, attribute: str) -> Optional[str]:
        """
        Return the attribute value for the command parameter provided.
        :param command: It is the 1st level key in the json file
        :param attribute: It is the 2nd level key in the json file
        :return: The attribute value from the json file for that command.
                 Return None, if command or attribute not found
        """
        try:
            return self._data[command][attribute]
        except KeyError:
            return None
        except TypeError:
            return None

    def get_text(self, command: str, condition: str, opposite: bool = False) -> Tuple[str, str]:
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

    def get_operator(self, condition: str, opposite: bool = False) -> str:
        if condition not in self._data:
            return ''
        if opposite and 'opposite' in self._data[condition] and self._data[condition]['opposite']:
            condition = self._data[condition]['opposite']
        return self._data[condition]['operator'] if 'operator' in self._data[condition] else ''


# This is the cmd object which needs to be imported by other applications.
cmd = _Command()


if __name__ == '__main__':
    download_commands()
