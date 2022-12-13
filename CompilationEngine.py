"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


class CompilationEngine:
    """Gets input from a JackTokenizer and emits its parsed structure into an
    output stream.
    """

    def __init__(self, input_stream: "JackTokenizer", output_stream) -> None:
        """
        Creates a new compilation engine with the given input and output. The
        next routine called must be compileClass()
        :param input_stream: The input stream.
        :param output_stream: The output stream.
        """
        self.output_file = output_stream
        self.tokenizer = input_stream

    def compile_class(self) -> None:
        """Compiles a complete class."""
        self.output_file.write("<class>\n")
        self.tokenizer.advance()
        # class
        self.write_keyword()
        # class name
        self.write_identifier()
        # {
        self.write_symbol()
        while self.tokenizer.curr_token == "static" or self.tokenizer.curr_token == "field" or self.tokenizer.curr_token == "constructor" or \
                self.tokenizer.curr_token == "method" or self.tokenizer.curr_token == "function":
            if self.tokenizer.curr_token == "static" or self.tokenizer.curr_token == "field":
                self.compile_class_var_dec()
            elif self.tokenizer.curr_token == "constructor" or \
                    self.tokenizer.curr_token == "method" or self.tokenizer.curr_token == "function":
                self.compile_subroutine()
        # }
        self.write_symbol()
        self.output_file.write("</class>\n")

    def compile_class_var_dec(self) -> None:
        """Compiles a static declaration or a field declaration."""
        self.output_file.write("<classVarDec>\n")
        # static/field
        self.write_keyword()
        # var type
        if self.tokenizer.token_type() == "IDENTIFIER":
            self.write_identifier()
        else:
            self.write_keyword()
        while self.tokenizer.curr_token != ';':
            if self.tokenizer.token_type() == 'IDENTIFIER':
                # var name
                self.write_identifier()
            else:
                # ,
                self.write_symbol()
        # ;
        self.write_symbol()
        self.output_file.write("</classVarDec>\n")

    def compile_subroutine(self) -> None:
        """
        Compiles a complete method, function, or constructor.
        You can assume that classes with constructors have at least one field,
        you will understand why this is necessary in project 11.
        """
        self.output_file.write("<subroutineDec>\n")
        if self.tokenizer.curr_token == "constructor":
            # constructor
            self.write_keyword()
            self.write_identifier()
            self.write_identifier()
        if self.tokenizer.curr_token == "function" or self.tokenizer.curr_token == "method":
            self.write_keyword()
            if self.tokenizer.token_type() == "KEYWORD":
                self.write_keyword()
            elif self.tokenizer.token_type() == "IDENTIFIER":
                self.write_identifier()
            self.write_identifier()
        # (
        self.write_symbol()
        self.compile_parameter_list()
        self.output_file.write("</parameterList>\n")
        # )
        self.write_symbol()
        self.output_file.write("<subroutineBody>\n")
        self.write_symbol()

        # defines variables
        while self.tokenizer.curr_token == "var":
            self.compile_var_dec()
        self.compile_statements()
        # }
        self.write_symbol()
        self.output_file.write("</subroutineBody>\n")
        self.output_file.write("</subroutineDec>\n")

    def compile_parameter_list(self) -> None:
        """Compiles a (possibly empty) parameter list, not including the 
        enclosing "()".
        """
        self.output_file.write("<parameterList>\n")
        while self.tokenizer.curr_token != ")":
            if self.tokenizer.token_type() == "KEYWORD":
                self.write_keyword()
            if self.tokenizer.token_type() == "IDENTIFIER":
                self.write_identifier()
            if self.tokenizer.curr_token == ',':
                self.write_symbol()

    def compile_var_dec(self) -> None:
        """Compiles a var declaration."""
        self.output_file.write("<varDec>\n")
        self.write_keyword()
        if self.tokenizer.token_type() == "IDENTIFIER":
            self.write_identifier()
        elif self.tokenizer.token_type() == "KEYWORD":
            self.write_keyword()
        while self.tokenizer.curr_token != ";":
            if self.tokenizer.token_type() == "SYMBOL":
                self.write_symbol()
            else:
                self.write_identifier()
        self.write_symbol()
        self.output_file.write("</varDec>\n")

    def compile_statements(self) -> None:
        """Compiles a sequence of statements, not including the enclosing 
        "{}".
        """
        self.output_file.write("<statements>\n")
        while self.tokenizer.token_type() == "KEYWORD":

            if self.tokenizer.curr_token == "do":
                self.compile_do()
            if self.tokenizer.curr_token == "let":
                self.compile_let()
            if self.tokenizer.curr_token == "while":
                self.compile_while()
            if self.tokenizer.curr_token == "return":
                self.compile_return()
            if self.tokenizer.curr_token == "if":
                self.compile_if()
        self.output_file.write("</statements>\n")

    def compile_do(self) -> None:
        """Compiles a do statement."""
        self.output_file.write("<doStatement>\n")
        # do
        self.write_keyword()
        # func name
        self.write_identifier()
        if self.tokenizer.curr_token == ".":
            self.write_symbol()
            self.write_identifier()
        # ( ) ;
        self.write_symbol()
        self.compile_expression_list()
        self.write_symbol()
        self.write_symbol()
        self.output_file.write("</doStatement>\n")

    def compile_let(self) -> None:
        """Compiles a let statement."""
        self.output_file.write("<letStatement>\n")
        # let
        self.write_keyword()
        # name
        self.write_identifier()
        if self.tokenizer.curr_token == '[':
            self.write_symbol()
            self.compile_expression()
            self.write_symbol()
        # =
        self.write_symbol()
        self.compile_expression()
        # ;
        self.write_symbol()
        self.output_file.write("</letStatement>\n")

    def compile_while(self) -> None:
        self.output_file.write("<whileStatement>\n")
        # while
        self.write_keyword()
        # (
        self.write_symbol()
        self.compile_expression()
        # )
        self.write_symbol()
        # {
        self.write_symbol()
        self.compile_statements()
        # }
        self.write_symbol()

        self.output_file.write("</whileStatement>\n")

    def compile_return(self) -> None:
        """Compiles a return statement."""
        self.output_file.write("<returnStatement>\n")
        self.write_keyword()
        while self.tokenizer.curr_token != ";":
            self.compile_expression()
        self.write_symbol()
        self.output_file.write("</returnStatement>\n")

    def compile_if(self) -> None:
        """Compiles a if statement, possibly with a trailing else clause."""
        self.output_file.write("<ifStatement>\n")
        # if
        self.write_keyword()
        # (
        self.write_symbol()
        self.compile_expression()
        # )
        self.write_symbol()
        # {
        self.write_symbol()
        self.compile_statements()
        # }
        self.write_symbol()
        if self.tokenizer.curr_token == "else":
            # else
            self.write_keyword()
            # {
            self.write_symbol()
            self.compile_statements()
            # }
            self.write_symbol()
        self.output_file.write("</ifStatement>\n")

    def compile_expression(self) -> None:
        """Compiles an expression."""
        self.output_file.write("<expression>\n")
        exp = ["+", "-", "*", '/', '&', '|', '<', '>', '=']
        self.compile_term()
        while self.tokenizer.curr_token in exp:
            if self.tokenizer.token_type() == "SYMBOL":
                self.write_symbol()
            if self.tokenizer.token_type() != "SYMBOL" or self.tokenizer.curr_token == "(":
                self.compile_term()

        self.output_file.write("</expression>\n")

    def compile_term(self) -> None:
        """Compiles a term. 
        This routine is faced with a slight difficulty when
        trying to decide between some of the alternative parsing rules.
        Specifically, if the current token is an identifier, the routing must
        distinguish between a variable, an array entry, and a subroutine call.
        A single look-ahead token, which may be one of "[", "(", or "." suffices
        to distinguish between the three possibilities. Any other token is not
        part of this term and should not be advanced over.
        """

        self.output_file.write("<term>\n")
        if self.tokenizer.token_type() == "INT_CONST":
            self.write_int_const()
        if self.tokenizer.token_type() == "STRING_CONST":
            self.write_str_const()
        if self.tokenizer.token_type() == "KEYWORD":
            self.write_keyword()
        if self.tokenizer.token_type() == "IDENTIFIER":
            self.write_identifier()
            if self.tokenizer.curr_token == '(':
                # (
                self.write_symbol()
                self.compile_expression_list()
                # self.tokenizer.advance()
                # )
                self.write_symbol()
            if self.tokenizer.curr_token == '[':
                # [
                self.write_symbol()
                self.compile_expression()
                # self.tokenizer.advance()
                # ]
                self.write_symbol()
            if self.tokenizer.curr_token == '.':
                # .
                self.write_symbol()
                # name
                self.write_identifier()
                # (
                self.write_symbol()
                self.compile_expression_list()
                # )
                self.write_symbol()

        if self.tokenizer.curr_token == '(':
            # (
            self.write_symbol()
            self.compile_expression()
            # )
            self.write_symbol()
        if self.tokenizer.curr_token == "~":
            self.write_symbol()
            self.compile_term()
        self.output_file.write("</term>\n")

    # TODO: check implamantation!
    def compile_expression_list(self) -> None:
        """Compiles a (possibly empty) comma-separated list of expressions."""
        self.output_file.write("<expressionList>\n")
        if self.tokenizer.curr_token != ")":
            self.compile_expression()
        while self.tokenizer.curr_token == ",":
            self.write_symbol()
            self.compile_expression()

        self.output_file.write("</expressionList>\n")

    def write_keyword(self):
        str_write = "<keyword>" + self.tokenizer.curr_token + "</keyword>\n"
        self.output_file.write(str_write)
        self.tokenizer.advance()

    def write_identifier(self):
        str_write = "<identifier>" + self.tokenizer.curr_token + "</identifier>\n"
        self.output_file.write(str_write)
        self.tokenizer.advance()

    def write_symbol(self):
        token = self.tokenizer.curr_token
        if self.tokenizer.curr_token == "&":
            token = "&amp;"
        if self.tokenizer.curr_token == "<":
            token = "&lt;"
        if self.tokenizer.curr_token == ">":
            token = "&gt;"
        str_write = "<symbol>" + token + "</symbol>\n"
        self.output_file.write(str_write)
        self.tokenizer.advance()

    def write_int_const(self):
        str_write = "<integerConstant>" + self.tokenizer.curr_token + "</integerConstant>\n"
        self.output_file.write(str_write)
        self.tokenizer.advance()

    def write_str_const(self):
        str_write = "<stringConstant>" + self.tokenizer.curr_token + "</stringConstant>\n"
        self.output_file.write(str_write)
        self.tokenizer.advance()
