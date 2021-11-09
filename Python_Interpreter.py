"""
A simple python interpreter (very minimalistic approach)
"""


class Interpreter:
    def __init__(self):
        self.stack = []

    def LOAD_VALUES(self, number):
        self.stack.append(number)

    def PRINT_ANSWER(self):
        answer = self.stack.pop()
        print(answer)

    def ADD_TWO_VALUES(self):
        first = self.stack.pop()
        sec = self.stack.pop()
        result = first + sec
        self.stack.append(result)

    def run_code(self, what_to_exec):
        instructions = what_to_exec["instructions"]
        numbers = what_to_exec["numbers"]
        for each_step in instructions:
            instruction, argument = each_step
            if instruction == "LOAD_VALUE":
                number = numbers[argument]
                self.LOAD_VALUES(number)
            elif instruction == 'ADD_TWO_VALUES':
                self.ADD_TWO_VALUES()
            elif instruction == 'PRINT_ANSWER':
                self.PRINT_ANSWER()

interpreter = Interpreter()

what_to_execute = {
    "instructions" : [
        ("LOAD_VALUE", 0),
        ("LOAD_VALUE", 1),
        ("ADD_TWO_VALUES", None),
        ("LOAD_VALUE", 2),
        ("ADD_TWO_VALUES", None),
        ("PRINT_ANSWER", None)
    ],
    "numbers" : [7,5,8]
}
interpreter.run_code(what_to_execute)
