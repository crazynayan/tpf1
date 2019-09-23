from execution.state import State
from v2.instruction_type import KeyValue


class UserDefinedDbMacro(State):
    def pdred(self, node: KeyValue) -> str:
        return self.next_label(node)


class RealTimeDbMacro(State):
    pass


class TpfdfMacro(State):
    pass


class DbMacro(UserDefinedDbMacro, RealTimeDbMacro, TpfdfMacro):
    pass
