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
        if all(line[0] == lines[0][0] for line in lines):
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
        if line.continuation and "='" in file_line and file_line.count("'") % 2 != 0:
            # This is the case where 2 quotes are in separate lines for e.g. MSG='.... X and in next line ...'
            file_line = file_line + "'"
            words = re.findall(r"(?:'.*?'|\S)+", file_line)
            words[-1] = words[-1][:-1]
        else:
            # Split the line in words. Keep words within single quotes together.
            words = re.findall(r"(?:'.*?'|\S)+", file_line)
        if file_line[0] == ' ':
            # The label is None for lines with first character space (No label)
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
        prior_line = Line()
        main_line = None
        for file_line in file_lines:
            line = cls.from_line(file_line, prior_line.continuation)
            if not prior_line.continuation:
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
            if line.is_set_cc:
                try:
                    other_lines = list()
                    for check_line in lines[index + 1:]:
                        if check_line.is_check_cc:
                            lines_to_yield.extend(other_lines)
                            lines_to_yield.append(check_line)
                            other_lines = list()
                        else:
                            other_lines.append(check_line)
                        if check_line.stop_checking_for_conditions:
                            break
                except IndexError:
                    pass
            yield lines_to_yield
            yielded_lines = lines_to_yield
            lines_to_yield = list()

    def remove_suffix(self):
        self.label = next(iter(self.label.split('&'))) if self.label is not None else None
        return self

    @property
    def is_fall_down(self):
        return True if not cmd.check(self.command, 'no_fall_down') else False

    @property
    def is_set_cc(self):
        return True if cmd.check(self.command, 'set_cc') else False

    @property
    def is_first_pass(self):
        return True if cmd.check(self.command, 'first_pass') else False

    @property
    def is_assembler_directive(self):
        return True if cmd.check(self.command, 'directive') else False

    @property
    def is_check_cc(self):
        return True if cmd.check(self.command, 'check_cc') and \
                       (self.command not in ['BC', 'JC'] or self.operand[:2] not in ['15', '0,']) else False

    @property
    def stop_checking_for_conditions(self):
        return True if self.is_set_cc or not self.is_fall_down or self.label is not None \
                       or not cmd.command_check(self.command) else False

    @property
    def length(self):
        length = cmd.check(self.command, 'len')
        return 0 if length is None else length

    def split_operands(self):
        # Split operands separated by commas. Ignore commas enclosed in parenthesis.
        return re.split(r",(?![^()]*\))", self.operand)

    def __repr__(self):
        return f'{self.label}:{self.command}:{self.operand}'


class SymbolTable:
    def __init__(self, label, dsp, length, name, branch=False):
        self.label = label
        self.dsp = dsp
        self.length = length
        self.name = name        # Macro name or Segment name or Dsect name
        self.branch = branch    # True = This label is a branch label i.e. code branches to this label.

    def __repr__(self):
        return f'{self.label}:{self.dsp}:{self.length}:{self.name}:{self.branch}'


class Label:
    SEPARATOR = '.'

    def __init__(self, name, separator=None):
        self.name = name
        self.index = 0
        self.separator = self.SEPARATOR if separator is None else separator

    def __repr__(self):
        return self.name if self.index == 0 else f"{self.name}{self.separator}{self.index}"
