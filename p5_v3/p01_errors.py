class ParserError(Exception):
    pass


class SourceFileNotFound(ParserError):
    pass


class SymbolNotFoundError(ParserError):
    pass


class SymbolTableError(ParserError):
    pass


class MacroArgumentError(Exception):
    pass


class UsingError(ParserError):
    pass


class DomainError(Exception):
    pass
