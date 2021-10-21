from typing import List

from firestore_ci import FirestoreDocument

from p1_utils.file_line import File
from p2_assembly.seg6_segment import seg_collection, Segment


class ListingLine(FirestoreDocument):

    def __init__(self):
        super().__init__()
        self.seg_name: str = str()  # 4 char name of the listing. Cannot be empty.
        # stmt: 6 digit id from listing with leading spaces. For continuing lines, it will have the same id followed by
        # a dot and 3 digit index with leading zeroes. Cannot be empty.
        self.stmt: str = str()
        self.line: str = str()  # The complete line from the listing. Cannot be empty.
        self.source_stmt: str = str()  # Only for generated line. Empty for normal line.
        self.master_stmt: str = str()  # Only for continuing line. Empty for non-continuing line.

    def __repr__(self):
        return f"{self.stmt:10}:{self.source_stmt:6}:{self.master_stmt:6}:{self.line}:{self.seg_name}"

    @property
    def label(self) -> str:
        if not self.line or len(self.line) < 51 or self.line[50] == " ":
            return str()
        return self.line[50:].split()[0]

    @property
    def label_dsp(self) -> int:
        if not self.label:
            return 0
        if self.line[1:9] != 8 * " ":
            return int(self.line[1:9], 16)
        if self.line[25:33] != 8 * " ":
            return int(self.line[25:33], 16)
        return 0

    @property
    def command(self) -> str:
        if len(self.line) < 52:
            return str()
        words = self.line[50:].strip().split()
        if self.line[50] == " ":
            return words[0] if len(words) >= 1 else str()
        return words[1] if len(words) >= 2 else str()

    @property
    def is_continuation(self) -> bool:
        return len(self.line) > 121 and self.line[121] != " "

    @property
    def is_comment(self) -> bool:
        return len(self.line) > 50 and self.line[50] in {".", "*"}

    @property
    def is_generated(self) -> bool:
        return len(self.line) > 49 and self.line[49] == "+"

    @property
    def is_valid_assembler(self) -> bool:
        if not self.line.strip():
            return False
        if len(self.line) > 9 and self.line[3:6] in {"Act", "Loc"}:
            return False
        if len(self.line) > 15 and self.line[11:15] == self.seg_name:
            return False
        if self.is_generated:
            words = self.line.strip().split()
            if len(words) > 2 and words[0] == "+" and words[1] == ",":
                return False
        return True

    def set_line_stmt(self, line, seg_name) -> None:
        self.line = line.rstrip()
        self.seg_name = seg_name
        stmt: str = line[43:49] if len(line) > 49 else str()
        stripped_stmt: str = stmt.strip()
        if stmt and stmt[-1].isdigit() and stripped_stmt.isdigit() and int(stripped_stmt) != 0:
            self.stmt = stmt

    def update_master_and_stmt(self, index: int, master_stmt: str) -> None:
        if not index:
            return
        self.stmt = f"{master_stmt}.{index:03}"
        self.master_stmt = master_stmt


ListingLine.init("listing_lines")


def create_listing_lines(seg_name: str) -> List[ListingLine]:
    seg: Segment = seg_collection.get_seg(seg_name)
    if not seg:
        print(f"{seg_name} not found.")
        return list()
    lines = File.open_file(seg.file_name)
    listing_lines: List[ListingLine] = list()
    source_stmt: str = str()
    master_stmt: str = str()
    continuing_comment: bool = False
    continuing_index: int = 0
    macro_mend_skip: bool = False
    for line in lines:
        listing_line = ListingLine()
        listing_line.set_line_stmt(line, seg_name)
        if not listing_line.is_valid_assembler:
            continue
        if not listing_line.stmt and not master_stmt:
            continue
        if listing_line.command == "MACRO":
            macro_mend_skip = True
        if macro_mend_skip:
            if listing_line.command == "MEND":
                macro_mend_skip = False
            continue
        if listing_line.is_comment or continuing_comment:
            continuing_comment = True if listing_line.is_continuation else False
            continue
        # Setup master_stmt for continuation lines
        if listing_line.is_continuation or master_stmt:
            if not master_stmt:
                master_stmt = listing_line.stmt
            listing_line.update_master_and_stmt(continuing_index, master_stmt)
            continuing_index += 1
            if not listing_line.is_continuation:
                master_stmt = str()
                continuing_index = 0
        # Setup source_stmt for generated lines
        if not listing_line.is_generated:
            source_stmt = listing_line.stmt
        else:
            listing_line.source_stmt = source_stmt
        listing_lines.append(listing_line)
    with open(f"{seg_name}.txt", "w") as fh:
        fh.writelines(f"{str(line)}\n" for line in listing_lines)
    return listing_lines
