import re

class Scanner:

    def __init__(self, input_text):
        self.data = input_text
        self.lines = input_text.split('\n')
        self.symbols = {}
        self.lexical_errors = {}

        # Init keyword symbols
        self.init_symbols()

        # Define the token names as constants
        self.ID = 'ID'
        self.NUM = 'NUM'
        self.KEYWORD = 'KEYWORD'
        self.SYMBOL = 'SYMBOL'
        self.COMMENT = 'COMMENT'

        # Regular expression patterns for each token type
        self.regex_patterns = [
            (r'\b(if|else|void|int|while|break|return)\b', self.KEYWORD),  # floating-point constant
            (r'[a-zA-Z]\w*', self.ID),  # identifier
            (r'\d+', self.NUM),  # integer constant
            (r'==|=|[;:,\[\]\(\)\{\}\+\-\*/<]', self.SYMBOL),  # string
            (r'/\*(.*?)\*/', self.COMMENT)  # plus
            ]

        # Combine all regex patterns into a single pattern
        self.combined_pattern = '|'.join(
            '(?P<{}>{})'.format(token_type, pattern) for pattern, token_type in self.regex_patterns)

    def scan_all(self):
        # Open files
        tokens_file = open("tokens.txt", "w")
        symbol_table_file = open("symbol_table.txt", "w")
        lexical_errors_file = open("lexical_errors.txt", "w")

        # Delete Comments and Errors
        self.delete_comments()
        self.find_and_delete_errors()

        # Tokens
        self.lines = self.data.split('\n')
        counter = 0
        for line in self.lines:
            counter += 1
            tokens = self.scan_line(line.strip())
            if len(tokens) != 0:
                tokens_file.write(f'{counter}.\t')
                for token in tokens:
                    tokens_file.write(f'({token[0].strip()}, {token[1].strip()}) ')
                    self.check_symbol(token)
                tokens_file.write('\n')

        # Symbol table
        for i in range(1, len(self.symbols) + 1):
            symbol_table_file.write(f'{i}.\t')
            symbol_list = list(self.symbols.items())
            symbol_table_file.write(f'{symbol_list[i - 1][0]}\n')

        # Lexical errors
        self.lexical_errors = dict(sorted(self.lexical_errors.items()))

        for i in self.lexical_errors.keys():
            self.lexical_errors[i].sort(key=lambda x: x[0])

        if len(self.lexical_errors) == 0:
            lexical_errors_file.write('There is no lexical error.')
        else:
            for line in self.lexical_errors:
                lexical_errors_file.write(f'{line}.\t')
                for item in self.lexical_errors[line]:
                    if len(item[1]) < 8:
                        lexical_errors_file.write(f'({item[1]}, {item[2]}) ')
                    else:
                        lexical_errors_file.write(f'({item[1][:7]}..., {item[2]}) ')
                lexical_errors_file.write('\n')

    def delete_comments(self):
        self.data = re.sub(r'/\*((.|\n)*?)\*/', '', self.data)
        self.lines = self.data.split('\n')

    def find_and_delete_errors(self):
        invalid_number_regex = r'\d+[a-zA-Z]'
        invalid_input_regex = r'[a-zA-Z*=]*[#!.£$%^&@]'

        # Unclosed comment
        if self.data.find('/*') != -1:
            position = self.data.find('/*')
            line = 1
            for i in range(position):
                if self.data[i] == '\n':
                    line += 1
            self.add_error(line, position, self.data[position:], 'Unclosed comment')
            self.data = self.data[:position]

        # Unmatched comment
        while self.data.find('*/') != -1:
            position = self.data.find('*/')
            line = 1
            for i in range(position):
                if self.data[i] == '\n':
                    line += 1
            self.add_error(line, position, '*/', 'Unmatched comment')
            self.data = self.data[:position] + ' ' + self.data[position + 2:]

        # Invalid number
        while re.search(invalid_number_regex, self.data):
            item = re.search(invalid_number_regex, self.data)
            position = item.span()[0]
            line = 1
            for i in range(position):
                if self.data[i] == '\n':
                    line += 1
            self.add_error(line, position, item.group(0), 'Invalid number')
            self.data = self.data[:item.span()[0]] + self.data[item.span()[1]:]

        # Invalid input
        while re.search(invalid_input_regex, self.data):
            item = re.search(invalid_input_regex, self.data)
            position = item.span()[0]
            line = 1
            for i in range(position):
                if self.data[i] == '\n':
                    line += 1
            if re.match(r'^/+$', item.group(0)):
                for _ in range(len(item.group(0))):
                    self.add_error(line, position, '/', 'Invalid input')
                    self.data = self.data.replace('/', '')
            elif re.match(r'^=/$', item.group(0)):
                self.add_error(line, position, '/', 'Invalid input')
                self.data = self.data.replace('/', '')
            else:
                self.add_error(line, position, item.group(0), 'Invalid input')
                self.data = self.data[:item.span()[0]] + self.data[item.span()[1]:]

    def add_error(self, error_line, error_position, error_data, error_type):
        if error_line in self.lexical_errors:
            self.lexical_errors[error_line].append((error_position, error_data, error_type))
        else:
            self.lexical_errors[error_line] = []
            self.lexical_errors[error_line].append((error_position, error_data, error_type))

    def scan_line(self, input_line):
        tokens = []
        for m in re.finditer(self.combined_pattern, input_line):
            token_type = m.lastgroup
            token_value = m.group(token_type)
            tokens.append((token_type, token_value))
        return tokens

    def add_symbol(self, name, value):
        self.symbols[name] = value

    def get_value(self, name):
        return self.symbols.get(name)

    def check_symbol(self, token):
        if token[0] == self.ID:
            self.add_symbol(token[1], 'id')

    def init_symbols(self):
        self.add_symbol('break', 1)
        self.add_symbol('else', 2)
        self.add_symbol('if', 3)
        self.add_symbol('int', 4)
        self.add_symbol('while', 5)
        self.add_symbol('return', 6)
        self.add_symbol('void', 7)
