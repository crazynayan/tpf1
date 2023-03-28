plan_for_future = """
Comments on service
===================
All user request should be via service. Each service has the following response
message : dict with fixed keys, values can be empty
    success : str
    warning : str
    error : str
    error_fields : dict 
data : list
Some services
1) Upload file
2) Assemble file

Comments on new assembly design
===============================
PHASE I
Read file and combine separate lines into single line. Remove comments
For listing, only keep asm lines,  keep displacement
For asm remove unnecessary lines like cvs 
For macro remove unnecessary lines like cvs 

PHASE II
Split lines into token
Each line will have offset, label, command, operands and type (machine instruction, assembler directive, macro)

Each operand is of different types
For machine instruction 
-----------------------
Fields use db (displacement base and other stuff)
db can be of 4 formats
db = expression;
db = expression '(' ',' expression ')';
db = expression '(' expression ')';
db = expression '(' expression ',' expression ')';

expression has 2 things
expression_string : str
expression_value: int
evaluation_done: bool

expression can have
    register - this needs to be evaluated now
    digits only - this needs to be evaluated now
    arithmetic operators (with digits or register) - this needs to evaluated now
    one or more symbols (other than register) - this needs to be evaluated later
    literal - this needs to be evaluated later 
    contain a '*' which is the current location counter/offset  - this needs to be evaluated later

For assembler directives DS / DC use self_defining_terms
--------------------------------------------------------
self_defining_term = duplication_factor TYPE length values

duplication_factor can be
    empty
    decimal_digits
    '(' expression ')'
TYPE is fixed
length can be same as duplication_factor
values = value, value, ... [0 to n]
value can be
    ' data '
    '(' expressions ')'
expressions = expression, expression, ... [1 to n]

For real time or user defined macro calls
-----------------------------------------
macro_call = key_value, key_value ... [0 to n]
key_value
    key: string
    value can be
        empty
        string
        db
        '(' key_value, key_value [1 to n] ')'


PHASE III
Evaluate symbol in expression
Evaluate expression containing symbol and location counter
Convert value to register for applicable machine instruction


Design of Token
a node is the smallest unit
it can contain symbol (fields), punctuation marks, as-is string, 
has properties like value: int, is_digit(), is_symbol(), is_location_counter(), is_arithmetic_operator(), is_data(),
is_enclosing_operator()

So a 
 DC 2XL5'ABC'
 self_defining_term = 2XL(5+FLD)'ABC'
    duplication_facter = '2' = 2
        expression = '2' = 2
            token = '2' = 2
    data_type = 'X'
    length = L(5+2) = 7
        token = 'L'
        token = '('
        expression = '5+FLD' = 7
            token = '5' = 5
            token = '+'
            token = 'FLD' = 2 (after lookup)
        token = ')'
    opening_enclosure = '
    closing_enclosure = '
    values = empty
    value = ABC
        token = \'ABC


L'ANC(#ABC,R10)
 db = L'ANC-1(#ABC,R10+1)
    expression1 = L'ANC = 2
        token = L'ANC  = symbol = 3
        token = '-' = arithmetic_operator
        token = '1' = digit
    expression2 = #ABC
        token = #ABC = symbol = 23 
    expression3 = 'R10+1' = 11
        token = R10 = register = 10
        token = '+' = arithmetic_operator
        token = '1' = digit = 1

db = X'10'(R1)
    expression1 = X'10' = 16
        tokens = empty
        self_defining_term = X'10' = 16
            duplication_factor = empty
            data_type = 'X'
            length = empty
            opening_enclosure = '
            value = '10
            values = empty
            closing_enclose = '
    token1 = '('
    expression2 = R1 = 1
        token = R1 = register = 1
    token2 = ')'
    expression3 = empty
    token3 = empty

Parser
    DS/DC is SelfDefinedTerm based on number of operands
    EQU is Expression based on number of operands
    ORG is Expression based on number of operands
    DSECT ignore all operands
    CSECT ignore all operands
    RR = Expression, Expression
    RX = Expression, BaseDisplacement
    SS = BaseDisplacement, BaseDisplacement
    RS = Expression,Expression, BaseDisplacement
    SI = BaseDisplacement, Expression
    RI = Expression, Expression
    RSL = BaseDisplacement
    Macro = KeyValue based on number of operands
    

"""
