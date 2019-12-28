class CodeGenerator:
    def __init__(self):
        self._out = []
        self._indent = 0

    def generate_dto(self, data, name: str):
        self._out = ['class ' + name + ':']
        self._push()
        self._add_line('def __init__(self):')

        for key, value in data.items():
            line = 'self.' + key + ' = '
            if isinstance(value, str):
                line += "''  # Example: " + value
            elif isinstance(value, bool):
                line += 'False'
            elif isinstance(value, int) or \
                    isinstance(value, float):
                line += '0  # Example: ' + str(value)
            else:
                line += 'None  # Unknown type: ' + str(value)

            self._add_line(line)

        return '\n'.join(self._out)

    def _push(self):
        self._indent += 1

    def _add_line(self, line):
        self._out.append(' ' * (4 * self._indent) + line)
