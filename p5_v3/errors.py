class AssemblyError(Exception):
    pass


class SourceFileNotFound(AssemblyError):
    pass


class ParserError(AssemblyError):
    pass
