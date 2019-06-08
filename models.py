from firestore_model import FirestoreModel
from os import path


class Block(FirestoreModel):
    COLLECTION = 'block'
    DEFAULT = 'label'

    def __init__(self, label=None, name=None):
        super().__init__()
        self.label = label if label else 'LABEL_ERROR'
        self.doc_id = self.label
        self.name = name
        self.from_blocks = list()
        self.to_blocks = list()
        self.function_calls = list()

    def create(self):
        self.update(self.doc_id)

    def __repr__(self):
        return f'{self.label} -> {self.to_blocks}'

    def add_to_blocks(self, label):
        if label and label not in self.to_blocks:
            self.to_blocks.append(label)


class Path(FirestoreModel):
    COLLECTION = 'path'
    DEFAULT = 'name'

    def __init__(self, name=None, asm_path=None):
        super().__init__()
        self.name = name if name else 'ERROR PROGRAM'
        self.path = asm_path if asm_path else list()


class AssemblerLine:
    EXCLUDE_C1 = ['*']
    EXCLUDE_C5 = ['Check', 'RCS: ', 'VERS:', '=====', '*****']
    TRIM = {'0': 7}
    TRUE_LABELS = {'DS': '0H', 'EQU': '*'}
    FALSE_LABELS = ['DS', 'DC', 'EQU', 'DSECT', 'CSECT']
    TRUE_BRANCH = ['B', 'BE', 'BNE', 'BH', 'BNH', 'BL', 'BNL', 'BM', 'BNM', 'BP', 'BNP', 'BC', 'BO', 'BNO', 'BZ', 'BNZ',
                   'J', 'JE', 'JNE', 'JH', 'JNH', 'JL', 'JNL', 'JM', 'JNM', 'JP', 'JNP', 'JC', 'JO', 'JNO', 'JZ', 'JNZ']
    TRUE_BRANCH_CHAR = ['=']
    EXIT_COMMANDS = {'B', 'J', 'ENTNC', 'ENTDC', 'BR', 'EXITC'}
    FUNCTION_CALL = {'BAS', 'JAS', 'ENTRC'}

    def __init__(self, line):
        self.line = line
        self.label = None
        self.command = None

    def _split_words(self):
        """
        Split the assembler line
        :return: words split by spaces and commas
        """
        return [not_equals.strip()
                for not_spaces in self.line.split(' ')
                for not_commas in not_spaces.split(',')
                for not_equals in not_commas.split('=') if not_equals]

    def get_command(self):
        """
        Returns the assembler instruction or macro from an assembler line.
        :return: command i.e. the assembler instruction, directive or macro command.
        """
        words = self.line.split()
        if self.line[0] == ' ':
            return words[0].strip() if len(words) > 0 else None
        else:
            return words[1].strip() if len(words) > 1 else None

    def sanitize(self):
        """
        Remove comments and cvs version related line.
        :return: line of valid assembler code else None.
        """
        if len(self.line) < 5:
            return None
        if self.line[:5] in self.EXCLUDE_C5:
            return None
        if self.line[0] in self.TRIM:
            self.line = self.line[self.TRIM[self.line[0]]:]
        if self.line[0] in self.EXCLUDE_C1:
            return None
        self.label = self.get_label()
        self.command = self.get_command()
        return self

    def get_label(self):
        """
        Check whether the assembler line has a label.
        Sanitize the line before calling this function.
        :return: label if the line has label else return None.
        """
        if self.line[0] == ' ':
            return None
        words = self._split_words()
        if len(words) < 3:
            return None
        if words[1] in self.TRUE_LABELS and words[2] == self.TRUE_LABELS[words[1]]:
            return words[0]
        if words[1] in self.FALSE_LABELS:
            return None
        return words[0]

    def get_branch(self, labels, function_call=False):
        """
        Check whether assembler line is branching to a label.
        :param labels: list of valid labels.
        :param function_call: whether branches for commands that call a function (BAS, JAS, ENTRC) need to be returned
        :return: label where the code branches to.
        """
        if not labels:
            return None
        words = self._split_words()
        if len(words) < 2:
            return None
        if self.line[0] != ' ':
            words = words[1:]
            if len(words) < 2:
                return None
        for word in words[1:]:
            if word in labels:
                if self.command in self.TRUE_BRANCH:
                    return word
                if function_call and self.command in self.FUNCTION_CALL:
                    return word
                index = self.line.find(word)
                if index > 0 and self.line[index - 1] in self.TRUE_BRANCH_CHAR:
                    return word
        return None


class AssemblerProgram:
    EXT = {'.asm', '.txt'}

    def __init__(self, name):
        self.name = name
        self.root_label = '$$' + name + '$$'
        self.file_name = None
        self.lines = list()
        self.labels = list()
        self.blocks = dict()
        self.paths = list()

    def set_file_name(self, file_path=None):
        """
        Sets the file_name of the source assembler file by verifying whether such file exists.
        :param file_path: A path to the assembler file name.
        :return: True if file_name set and it exists else False
        """
        if file_path:
            if path.isfile(file_path):
                self.file_name = file_path
                return True
            if file_path[-1] != '/':
                file_path += '/'
            for ext in self.EXT:
                file_name = file_path + ext
                if path.isfile(file_name):
                    self.file_name = file_name
                    return True
        for ext in self.EXT:
            file_name = self.name + ext
            if path.isfile(file_name):
                self.file_name = file_name
                return True
        return False

    def read_file(self):
        """
        Read the file and initialize assembler lines
        :return: True if assembler lines initialize else false
        """
        if not self.file_name and not self.set_file_name():
            return False
        try:
            with open(self.file_name, 'r', errors='replace') as file:
                lines = file.readlines()
        except FileNotFoundError:
            return False
        for line in lines:
            sanitize_line = AssemblerLine(line).sanitize()
            if sanitize_line:
                self.lines.append(sanitize_line)
        return True

    def first_pass(self):
        if self.labels:
            return True
        if not self.lines and not self.read_file():
            return False
        self.labels = [line.label for line in self.lines if line.label]
        return True

    def create_blocks(self):
        """
        Create code blocks and save it to the database
        :return: True if blocks created else false
        """
        if not self.labels and not self.first_pass():
            return False
        blocks = dict()
        current_label = self.root_label
        exit_command = False
        blocks[current_label] = Block(current_label, self.name)
        for assembler_line in self.lines:
            label = assembler_line.label
            if label:
                blocks[label] = Block(label, self.name)
                if not exit_command:
                    blocks[current_label].add_to_blocks(label)
                current_label = label
                exit_command = False
            if assembler_line.command in AssemblerLine.EXIT_COMMANDS:
                exit_command = True
            if assembler_line.command in AssemblerLine.FUNCTION_CALL:
                branch = assembler_line.get_branch(self.labels, function_call=True)
                if branch:
                    blocks[current_label].function_calls.append(branch)
            branch = assembler_line.get_branch(self.labels)
            if branch:
                blocks[current_label].add_to_blocks(branch)
        self.blocks = blocks
        for key in blocks:
            blocks[key].create()
        return True

    def create_paths(self, save=False):
        if not self.blocks:
            self.blocks = Block.query(dict_type=True, name=self.name)
        if not self.blocks:
            return False
        self._build_path(self.blocks[self.root_label])
        function_call_blocks = [self.blocks[key] for key in self.blocks if self.blocks[key].function_calls]
        done_labels = set()
        for block in function_call_blocks:
            for label in block.function_calls:
                if label not in done_labels:
                    self._build_path(self.blocks[label])
                done_labels.add(label)
        if save:
            for asm_path in self.paths:
                Path(self.name, asm_path).create()

    def _build_path(self, block, asm_path=None):
        if asm_path:
            asm_path.append(block.label)
        else:
            asm_path = [block.label]
        for label in block.to_blocks:
            if label not in asm_path:
                self._build_path(self.blocks[label], asm_path.copy())
        if not block.to_blocks:
            self.paths.append(asm_path)
        return






