# Python Programs for Parsing Assembler Code

This document identifies the primary Python programs responsible for parsing TPF Assembler code in this repository.

## 1. Backend Parser (d21_backend)
The core parsing logic used by the Flask application is located within the `d21_backend` directory.

*   **`d21_backend/p1_utils/file_line.py`**: Handles low-level parsing of source files, including splitting lines into labels, commands, and operands. It also manages line continuations and comment removal.
*   **`d21_backend/p2_assembly/seg6_segment.py`**: The `Segment` class orchestrates the assembly process, implementing a two-pass parser to build symbol tables and process instructions.
*   **`d21_backend/p2_assembly/seg2_ins_operand.py`**: Contains the logic for parsing complex operands, such as base-displacement addresses and register specifications.

## 2. Consolidate Parser (p5_v3)
The `p5_v3` directory contains a newer, more modular parsing implementation.

*   **`p5_v3/p28_parser.py`**: The main entry point for the v3 parser, featuring `FileParser` and `StreamParser` classes.
*   **`p5_v3/p11_base_parser.py`**: Provides foundational parsing utilities and operand splitting logic.
*   **`p5_v3/p15_token_expression.py`**: Handles the parsing and evaluation of expressions and self-defined terms.

---

# Refactoring Recommendations for `p5_v3`

To enhance the maintainability and robustness of the `p5_v3` parser, the following refactorings are recommended:

1.  **Standardize Naming**: Remove the `pXX_` prefixes from filenames (e.g., `p28_parser.py` -> `parser.py`) to follow standard Python conventions.
2.  **Safe Expression Evaluation**: Replace the usage of `eval()` in `p15_token_expression.py` with a safer, dedicated expression evaluator to mitigate security risks and improve debuggability.
3.  **Adopt Grammar-Based Parsing**: Utilize the `pyparsing` library (already a project dependency) to define formal grammars for Assembler operands and expressions, replacing manual string-walking logic.
4.  **Enhance Error Reporting**: Improve `ParserError` to include contextual information like column offsets and the failing code snippet.
5.  **Decouple Components**: Abstract the instruction set and macro definitions to allow the parser to support multiple Assembler dialects more easily.
