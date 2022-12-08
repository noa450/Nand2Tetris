"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing
import sys
import os


class JackTokenizer:
    """Removes all comments from the input stream and breaks it
    into Jack language tokens, as specified by the Jack grammar.
    
    # Jack Language Grammar

    A Jack file is a stream of characters. If the file represents a
    valid program, it can be tokenized into a stream of valid tokens. The
    tokens may be separated by an arbitrary number of whitespace characters, 
    and comments, which are ignored. There are three possible comment formats: 
    /* comment until closing */ , /** API comment until closing */ , and 
    // comment until the line’s end.

    - ‘xxx’: quotes are used for tokens that appear verbatim (‘terminals’).
    - xxx: regular typeface is used for names of language constructs 
           (‘non-terminals’).
    - (): parentheses are used for grouping of language constructs.
    - x | y: indicates that either x or y can appear.
    - x?: indicates that x appears 0 or 1 times.
    - x*: indicates that x appears 0 or more times.

    ## Lexical Elements

    The Jack language includes five types of terminal elements (tokens).

    - keyword: 'class' | 'constructor' | 'function' | 'method' | 'field' | 
               'static' | 'var' | 'int' | 'char' | 'boolean' | 'void' | 'true' |
               'false' | 'null' | 'this' | 'let' | 'do' | 'if' | 'else' | 
               'while' | 'return'
    - symbol: '{' | '}' | '(' | ')' | '[' | ']' | '.' | ',' | ';' | '+' | 
              '-' | '*' | '/' | '&' | '|' | '<' | '>' | '=' | '~' | '^' | '#'
    - integerConstant: A decimal number in the range 0-32767.
    - StringConstant: '"' A sequence of Unicode characters not including
                      double quote or newline '"'
    - identifier: A sequence of letters, digits, and underscore ('_') not 
                  starting with a digit. You can assume keywords cannot be
                  identifiers, so 'self' cannot be an identifier, etc'.

    ## Program Structure

    A Jack program is a collection of classes, each appearing in a separate 
    file. A compilation unit is a single class. A class is a sequence of tokens 
    structured according to the following context free syntax:
    
    - class: 'class' className '{' classVarDec* subroutineDec* '}'
    - classVarDec: ('static' | 'field') type varName (',' varName)* ';'
    - type: 'int' | 'char' | 'boolean' | className
    - subroutineDec: ('constructor' | 'function' | 'method') ('void' | type) 
    - subroutineName '(' parameterList ')' subroutineBody
    - parameterList: ((type varName) (',' type varName)*)?
    - subroutineBody: '{' varDec* statements '}'
    - varDec: 'var' type varName (',' varName)* ';'
    - className: identifier
    - subroutineName: identifier
    - varName: identifier

    ## Statements

    - statements: statement*
    - statement: letStatement | ifStatement | whileStatement | doStatement | 
                 returnStatement
    - letStatement: 'let' varName ('[' expression ']')? '=' expression ';'
    - ifStatement: 'if' '(' expression ')' '{' statements '}' ('else' '{' 
                   statements '}')?
    - whileStatement: 'while' '(' 'expression' ')' '{' statements '}'
    - doStatement: 'do' subroutineCall ';'
    - returnStatement: 'return' expression? ';'

    ## Expressions
    
    - expression: term (op term)*
    - term: integerConstant | stringConstant | keywordConstant | varName | 
            varName '['expression']' | subroutineCall | '(' expression ')' | 
            unaryOp term
    - subroutineCall: subroutineName '(' expressionList ')' | (className | 
                      varName) '.' subroutineName '(' expressionList ')'
    - expressionList: (expression (',' expression)* )?
    - op: '+' | '-' | '*' | '/' | '&' | '|' | '<' | '>' | '='
    - unaryOp: '-' | '~' | '^' | '#'
    - keywordConstant: 'true' | 'false' | 'null' | 'this'
    
    Note that ^, # correspond to shiftleft and shiftright, respectively.
    """

    def __init__(self, input_stream: typing.TextIO) -> None:
        """Opens the input stream and gets ready to tokenize it.

        Args:
            input_stream (typing.TextIO): input stream.
        """
        # Your code goes here!
        # A good place to start is to read all the lines of the input:
        self.input_lines = input_stream.read().splitlines()
        self.clean_comments()
        self.curr_line_ind = -1
        self.num_lines = len(self.input_lines)
        self.curr_command = ''
        self.curr_token = ''
        self.curr_token_ind = -1
        self.keyword_arr = ['class', 'constructor', 'function', 'method', 'field',
                            'static', 'var', 'int', 'char', 'boolean', 'void', 'true',
                            'false', 'null', 'this', 'let', 'do', 'if', 'else',
                            'while', 'return']

        self.symbol_arr = ['{', '}', '(', ')', '[', ']', '.', ',', ';', '+',
                           '-', '*', '/', '&', '|', '<', '>', '=', '~', '^', '#']
        self.integerConstant_arr = [str(i) for i in range(0, 32768)]

    def has_more_tokens(self) -> bool:
        """Do we have more tokens in the input?

        Returns:
            bool: True if there are more tokens, False otherwise.
        """
        # if it's not the last line- return true
        if self.curr_line_ind < len(self.input_lines) - 1:
            return True

        # TODO: check if it's true
        else:
            if self.curr_token_ind < len(self.curr_command) - 1:
                return True
        return False

    def advance(self) -> None:
        """Gets the next token from the input and makes it the current token.
        This method should be called if has_more_tokens() is true.
        Initially there is no current token.
        """
        # Your code goes here!
        while self.has_more_tokens():
            ind = self.curr_token_ind + 1
            command_str = ''

            while ind < len(self.curr_command):
                if self.curr_command[ind]=="\t":
                    ind+=1
                    continue
                command_str += self.curr_command[ind]

                if command_str == '"':
                    command_str = ""
                    while '"' not in command_str:
                        ind += 1
                        command_str += self.curr_command[ind]
                    command_str = command_str[:-1]

                if command_str == " ":
                    command_str = ""
                    ind += 1
                    continue

                elif self.curr_command[ind] == " ":
                    self.curr_token = command_str[:-1]
                    self.curr_token_ind = ind
                    return

                elif self.curr_command[ind] in self.symbol_arr:
                    if len(command_str) == 1:
                        self.curr_token = command_str
                        self.curr_token_ind = ind

                    else:
                        self.curr_token = command_str[:-1]
                        self.curr_token_ind = ind - 1
                    return
                ind += 1
            self.curr_token_ind = -1
            self.curr_line_ind += 1
            self.curr_command = self.input_lines[self.curr_line_ind]
            if command_str!="":
                self.curr_token = command_str
                return


    def token_type(self) -> str:
        """
        Returns:
            str: the type of the current token, can be
            "KEYWORD", "SYMBOL", "IDENTIFIER", "INT_CONST", "STRING_CONST"
        """
        if self.curr_token in self.symbol_arr:
            return 'SYMBOL'

        elif self.curr_token in self.keyword_arr:
            return 'KEYWORD'

        elif self.curr_token in self.integerConstant_arr:
            return 'INT_CONST'
        elif self.input_lines[self.curr_line_ind][self.curr_token_ind][0] == '"' and \
                self.input_lines[self.curr_line_ind][self.curr_token_ind][-1] == '"':
            return 'STRING_CONST'
        else:
            return 'IDENTIFIER'

    def keyword(self) -> str:
        """
        Returns:
            str: the keyword which is the current token.
            Should be called only when token_type() is "KEYWORD".
            Can return "CLASS", "METHOD", "FUNCTION", "CONSTRUCTOR", "INT",
            "BOOLEAN", "CHAR", "VOID", "VAR", "STATIC", "FIELD", "LET", "DO",
            "IF", "ELSE", "WHILE", "RETURN", "TRUE", "FALSE", "NULL", "THIS"
        """
        # Your code goes here!
        return self.curr_token.upper()

    def symbol(self) -> str:
        """
        Returns:
            str: the character which is the current token.
            Should be called only when token_type() is "SYMBOL".
            Recall that symbol was defined in the grammar like so:
            symbol: '{' | '}' | '(' | ')' | '[' | ']' | '.' | ',' | ';' | '+' |
              '-' | '*' | '/' | '&' | '|' | '<' | '>' | '=' | '~' | '^' | '#'
        """
        return self.curr_token

    def identifier(self) -> str:
        """
        Returns:
            str: the identifier which is the current token.
            Should be called only when token_type() is "IDENTIFIER".
            Recall that identifiers were defined in the grammar like so:
            identifier: A sequence of letters, digits, and underscore ('_') not
                  starting with a digit. You can assume keywords cannot be
                  identifiers, so 'self' cannot be an identifier, etc'.
        """
        return self.curr_token

    def int_val(self) -> int:
        """
        Returns:
            str: the integer value of the current token.
            Should be called only when token_type() is "INT_CONST".
            Recall that integerConstant was defined in the grammar like so:
            integerConstant: A decimal number in the range 0-32767.
        """
        return self.curr_token

    def string_val(self) -> str:
        """
        Returns:
            str: the string value of the current token, without the double
            quotes. Should be called only when token_type() is "STRING_CONST".
            Recall that StringConstant was defined in the grammar like so:
            StringConstant: '"' A sequence of Unicode characters not including
                      double quote or newline '"'
        """
        return self.curr_token[1:-1]

    def go_to_non_comment_line(self, curr_line_ind):

        in_comment = True
        while curr_line_ind < len(self.input_lines):
            # when we finish a comment block
            if self.input_lines[curr_line_ind] == "":
                curr_line_ind += 1
                continue
            if is_end_of_comment(self.input_lines[curr_line_ind]):
                in_comment = False
            elif in_comment == False:
                break
            curr_line_ind += 1

            continue

        return curr_line_ind

    # TODO: need to call this func in the main, before all
    def clean_comments(self):
        curr_ind = 0
        input_lines_without_comments = []
        while curr_ind < len(self.input_lines):
            # when there is a beginning of comment block
            self.input_lines[curr_ind] = self.input_lines[curr_ind].strip()
            self.input_lines[curr_ind] = self.input_lines[curr_ind].split("//")[0]
            if self.input_lines[curr_ind] == "":
                curr_ind += 1
                continue
            if is_beginning_of_comment(self.input_lines[curr_ind]):
                curr_ind = self.go_to_non_comment_line(curr_ind)
                continue


            # when it's a one line comment
            elif self.input_lines[curr_ind][0] == "/":
                if self.input_lines[curr_ind][1] == "/":
                    curr_ind += 1
                    continue

            # otherwise, it's a command
            input_lines_without_comments.append(self.input_lines[curr_ind])
            curr_ind += 1

        self.input_lines = input_lines_without_comments


def is_beginning_of_comment(curr_command):
    if curr_command[0] == "/":
        if (curr_command[1] == "*") or (curr_command[1] == "*" and curr_command[2] == "*"):
            return True
    return False


def is_end_of_comment(curr_command):
    curr_command=curr_command.strip(" ")
    if curr_command[-1] == "/":
        if curr_command[-2] == "*":
            return True
    return False


if "__main__" == __name__:

    if not len(sys.argv) == 2:
        sys.exit("Invalid usage, please use: JackAnalyzer <input path>")
    argument_path = os.path.abspath(sys.argv[1])
    if os.path.isdir(argument_path):
        files_to_assemble = [
            os.path.join(argument_path, filename)
            for filename in os.listdir(argument_path)]
    else:
        files_to_assemble = [argument_path]
    for input_path in files_to_assemble:
        filename, extension = os.path.splitext(input_path)
        if extension.lower() != ".jack":
            continue
        output_path = filename + ".xml"
        with open(input_path, 'r') as input_file, \
                open(output_path, 'w') as output_file:
            a = JackTokenizer(input_file)
            while a.has_more_tokens():
                a.advance()
                print(a.keyword())
