import dis
import types
import sys
import inspect


class VirtualMachineError(Exception):
    pass


class Frame:
    def __init__(self, code_obj, global_names, local_names, previous_frame):
        self.code_obj = code_obj
        self.global_names = global_names
        self.local_names = local_names
        self.previous_frame = previous_frame
        self.stack = []

        if previous_frame:
            self.builtin_names = previous_frame.builtin_names
        else:
            self.builtin_names = local_names['__builtins__']
            if hasattr(self.builtin_names, '__dict__'):
                self.builtin_names = self.builtin_names.__dict__
        self.last_instruction = 0
        self.block_stack = []


class VirtualMachine:
    def __init__(self):
        self.frames = []  # the call stack for frames
        self.frame = None  # The current frame
        self.return_value = None
        self.last_exception = None

    def make_frame(self, code, call_args={}, global_names=None, local_names=None):
        if global_names is not None and local_names is not None:
            local_names = global_names
        elif self.frames:
            global_names = self.frame.global_names
            local_names = {}
        else:
            global_names = local_names = {
                '__builtins__': __builtins__,
                '__name__': '__main__',
                '__doc__': None,
                '__package__': None,
            }
        local_names.update(call_args)
        frame = Frame
        return frame

    def push_frame(self, frame):
        self.frames.append(frame)
        self.frame = frame

    def pop_frame(self):
        self.frames.pop()
        if self.frames:
            self.frame = self.frames[-1]
        else:
            self.frame = None

    # Data Stack manupilation
    def top(self):
        return self.frame.stack[-1]

    def pop(self):
        return self.frame.stack.pop()

    def push(self, *vals):
        self.frame.stack.extends(vals)

    def popn(self, n):
        """Pop a number of values from the value stack.
        A list of `n` values is returned, the deepest value first.
        """
        if n:
            ret = self.frame.stack[-n:]
            self.frame.stack[-n:] = []
            return ret
        else:
            return []

    def run_frame(self):
        pass

    def run_code(self, code, global_names=None, local_names=None):
        """An entry point into executing the code using VirtualMachine"""
        frame = self.make_frame(code, global_names=global_names, local_names=local_names)
        self.run_frame(frame)

    def parse_byte_and_args(self):
        f = self.frame
        opoffset = f.last_instruction
        byteCode = f.code_obj.co_code[opoffset]
        f.last_instruction += 1
        byte_name = dis.opname[byteCode]
        if byteCode >= dis.HAVE_ARGUMENT:
            arg = f.code_obj.co_code[f.last_instruction:f.last_instruction + 2]
            f.last_instruction += 2
            arg_val = arg[0] + (arg[1] * 256)
            if byteCode in dis.hasconst:  # Look up a constant
                arg = f.code_obj.co_code[arg_val]
            elif byteCode in dis.hasname:
                arg = f.code_obj.co_names[arg_val]
            elif byteCode in dis.haslocal:
                arg = f.code_obj.co_varnames[arg_val]
            elif byteCode in dis.hasjrel:
                arg = f.last_instruction + arg_val
            else:
                arg = arg_val
            argument = [arg]
        else:
            argument = []
        return byte_name, argument

    def dispatch(self, byte_name, argument):
        """ Dispatch by bytename to the corresponding methods.
                Exceptions are caught and set on the virtual machine."""

        # When later unwinding the block stack,
        # we need to keep track of why we are doing it.
        why = None
        try:
            bytecode_func = getattr(self, 'byte_%s' % byte_name, None)
            if bytecode_func is None:
                if byte_name.startswith('UNARY_'):
                    self.unaryOperator(byte_name[:6])
                elif byte_name.startswith('BINARY_'):
                    self.binaryOperator(byte_name[7:])
                else:
                    raise VirtualMachineError(
                        "unsupported bytecode type: %s" % byte_name
                    )
            else:
                why = bytecode_func(*argument)
        except:
            # deal with exceptions encountered while executing the op.
            self.last_exception = sys.exc_info()[:2] + (None,)
            why = 'exception'
        return why

    def run_frame(self, frame):
        """
        Executes a Frame object
        :param frame: Frame object
        :return:
        """
        self.push_frame(frame)
        while True:
            byte_name , argument = self.parse_byte_and_args()

            why = self.dispatch(byte_name, argument)

            while why and frame.block_stack:
                why = self.manage_block_stack(why)
            if why:
                break
        self.pop_frame()

        if why == 'exception':
            exc, val, tb = self.last_exception
            e = exc(val)
            e.__traceback__ = tb

            raise e
        return self.return_value

class Function:
    """
    create a realistic function object, defining the things the interpreter expects
    """
    __slots__ = [
        'func_code', 'func_name', 'func_defaults', 'func_globals',
        'func_locals', 'func_dict', 'func_closure',
        '__name__', '__dict__', '__doc__',
        '_vm', '_func',
    ]

    def __init__(self, name, code, globs, defaults, closure, vm):
        self._vm = vm
        self.func_code = code
        self.func_name = self.__name__ or code.co_name
        self.func_defaults = tuple(defaults)
        self.func_closure = closure
        self.func_globals = globs
        self.func_locals = self._vm.frame.f_locals
        self.__dict__ = {}
        self.doc = code.co_consts[0] if code.co_consts else None

        kw = {
            'argdefs': self.func_defaults,
        }

        if closure:
            kw['closure'] = tuple(make_cell(0) for _ in closure)
        self._func = types.FunctionType(code, globs, **kw)

    def __call__(self, *args, **kwargs):
        """When calling a function make a frame and run it"""
        call_args = inspect.getcallargs(self._func, *args, **kwargs)
        # Use callargs to provide a mapping of arguments: values to pass into the new
        # frame.
        frame = self._vm.make_frame(self.func_code, call_args, self.func_globals, {})
        return self._vm.run_frame(frame)

    def make_cell(value):
        """create a real python closure and creates a cell"""
        fn = (lambda x: lambda: x)(value)
        return fn.__closure__[0]
