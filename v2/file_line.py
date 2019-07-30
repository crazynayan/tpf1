import re

from v2.command import cmd


class File:
    CVS_C2 = {'Ch', 'RC', 'VE', '==', '**', 'ng', '/u', '1.'}
    TRIM = {'0': 7, ' ': 1}
    COMMENT_C1 = {'*', '.'}

    @classmethod
    def open(cls, file_name):
        # Open the file
        try:
            with open(file_name, 'r', errors='replace') as file:
                lines = file.readlines()
        except FileNotFoundError:
            return list()
        # Remove the CVS header if present
        index = 0
        for line in lines:
            if line[:2] not in cls.CVS_C2:
                break
            index += 1
        lines = lines[index:] if index < len(lines) else list()
        # Remove empty lines and trailing new line character
        lines = [line.strip('\n') for line in lines if line.strip()]
        if not lines:
            return list()
        # Find the character that is added by CVS on each line
        char = ''
        if all(line[0] == lines[0][0] for line in lines if line.strip):
            char = lines[0][0]
        # Remove (TRIM) the character from each line
        if char in cls.TRIM:
            lines = [line[cls.TRIM[char]:] for line in lines]
        # Remove comments
        lines = [line for line in lines if line[0] not in cls.COMMENT_C1]
        return lines


class Line:
    def __init__(self):
        self.label = None
        self.command = None
        self.operand = None
        self.continuation = False

    @classmethod
    def from_line(cls, file_line, continuing=False):
        # Create a line object from a single file line.
        line = cls()
        if len(file_line) > 71 and file_line[71] != ' ':
            line.continuation = True
            file_line = file_line[:71]
        words = re.findall(r"(?:[^L]'.*?'|\S)+", file_line)
        if file_line[0] == ' ':
            # The label is None since there is no label
            words.insert(0, None)
        if continuing:
            # The command is None for continued lines
            words.insert(0, None)
        line.label = words[0]
        line.command = words[1] if len(words) > 1 else None
        line.operand = words[2] if len(words) > 2 else None
        return line

    @classmethod
    def from_file(cls, file_lines):
        # Create a list of Line objects. Also combines multiple continuing lines in a single line object.
        lines = list()
        prior_line = None
        main_line = None
        for file_line in file_lines:
            continuing = True if prior_line is not None and prior_line.continuation else False
            line = cls.from_line(file_line, continuing)
            if not continuing:
                lines.append(line)
                main_line = line
            else:
                main_line.operand = main_line.operand + line.operand if main_line.operand is not None else line.operand
            prior_line = line
        return lines

    @classmethod
    def yield_lines(cls, lines):
        lines_to_yield = list()
        yielded_lines = list()
        for index, line in enumerate(lines):
            if line in yielded_lines:
                continue
            lines_to_yield.append(line)
            if line.is_conditional:
                try:
                    for check_line in lines[index + 1:]:
                        if check_line.is_check_condition:
                            lines_to_yield.append(check_line)
                            break
                        if check_line.stop_checking_for_conditions:
                            break
                        lines_to_yield.append(check_line)
                except IndexError:
                    pass
            yield lines_to_yield
            yielded_lines = lines_to_yield
            lines_to_yield = list()

    def remove_suffix(self):
        self.label = next(iter(self.label.split('&'))) if self.label is not None else None
        return self

    @property
    def is_conditional(self):
        return True if cmd.check(self.command, 'set_cc') else False

    @property
    def is_check_condition(self):
        return cmd.check(self.command, 'check_cc')

    @property
    def stop_checking_for_conditions(self):
        return True if cmd.check(self.command, 'set_cc') or cmd.check(self.command, 'exit') or self.label is not None \
            or not cmd.command_check(self.command) else False

    def __repr__(self):
        return f'{self.label}:{self.command}:{self.operand}'
