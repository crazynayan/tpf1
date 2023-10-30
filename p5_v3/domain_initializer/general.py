from p5_v3.p22_format import MacroCallFormat
from p5_v3.p23_operation_code_format import OperationCodeFormat

# The client name and domain name should match the names of sub-folders where the source file are stored.
# The path should be <CLIENT_NAME>/<DOMAIN_NAME>

CLIENT_NAME = "general"  # Should start with alphabet. Should have only alphabets, numbers and underscore. Preferably lower case.
DOMAIN_NAME = "general"  # Should start with alphabet. Should have only alphabets, numbers and underscore. Preferably lower case.


# Add all custom formats inside the class
class UserDefinedOperationCodeFormat(OperationCodeFormat):
    PNRJR = MacroCallFormat
