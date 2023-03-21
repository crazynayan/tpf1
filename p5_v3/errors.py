class ParserError(Exception):
    pass


class SourceFileNotFound(ParserError):
    pass


class SymbolNotFoundError(ParserError):
    pass
