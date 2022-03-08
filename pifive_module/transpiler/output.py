import sys

class Output:
    def __init__(self, output_file=sys.stdout):
        self.output_file = output_file

    def write(self, text):
        print(text, file=self.output_file, end="")

    def writeln(self, text):
        print(text, file=self.output_file)