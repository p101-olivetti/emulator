# Permission to use, copy, modify, and distribute this software and its
# documentation for any purpose and without fee is hereby granted.
"""
Olivetti's 101 emulator. Based on PEP 282 and comments
thereto in comp.lang.python.
"""

import numpy as np

__author = 'Giovanni Mocellin, Matteo Poletto, Federico Rubbi'
__status__ = 'developing'
__version__ = '1.5'
__date__ = '29 March 2021'


# Registers max length.
REG_LEN_MAX = 24  # 22 digits, float position and sign


# Previous key pressed.
previous_key = ''
previous_key_backup = ''

n_digits = 0


class Register:
    """
    Register class.
    """

    def __init__(self):
        """
        Initialize register attributes.
        """
        # Initialize register representation as np.array.
        self.reg = np.zeros((REG_LEN_MAX), dtype='short')
        # Set flag to check if float is active in the register.
        self.float_active = False

    @property
    def float_pos(self):
        """
        Number of digits after the floating point.
        """
        return self.reg[22]

    @float_pos.setter
    def float_pos(self, pos):
        self.reg[22] = pos

    @property
    def sign(self):
        """
        Sign of the register. Default is +.
        """
        return '+' if not self.reg[23] else '-'

    @sign.setter
    def sign(self, value):
        """
        Set register sign. 1 corresponds to -.
        """
        self.reg[23] = 1 if value == '-' else 0

    def is_full(self):
        """
        Return True if register is full.
        """
        return not (self.reg[21] == 0 and self.float_pos != 21)

    def shift(self):
        """
        Shift all digits in a register right by 1.
        """
        for i in range(REG_LEN_MAX-3, 0, -1):
            self.reg[i] = self.reg[i-1]
        if self.float_active:
            self.float_pos += 1
            
    def erase(self):
        """
        Erase a register.
        """
        self.reg = np.zeros((REG_LEN_MAX), dtype='short')
        self.float_active = False
        self.sign = '+'

    def read_register(self):
        """
        Convert register array to the corresponding value.
        """
        # Convert array representation to string.
        reg_value = ''.join([str(x) for x in list(self.reg[:22])])
        # Add sign and reverse it.
        reg_value = (reg_value + self.sign)[::-1]
        if self.float_active:  # add floating point
            reg_value = f'{reg_value[:-self.float_pos]}.'\
                        f'{reg_value[-self.float_pos:]}'
            return float(reg_value)
        else:
            return int(reg_value)

    def write_register(self, value):
        """
        Convert value to register array representation.
        """
        try:
            value = str(value)  # convert to string
            self.sign = value[0]  # add sign if needed
            if not value[0].isdigit():  # remove sign if any
                value = value[1:]
            if '.' in value:
                self.float_pos = value[::-1].find('.')
                if self.float_pos > n_digits:
                    value = value[:-self.float_pos+n_digits]  # truncate
                    self.float_pos = n_digits
                self.float_active = True  # set float_active flag
                value = value.replace('.', '')  # remove float point
                
            # Write each digit at the matching index in the register.
            for (i, x) in enumerate(value[::-1]):
                self.reg[i] = int(x)
        except IndexError:  # if more than 22 digits
            raise Exception("Value too big for register.")


# Registers instances.
M = Register()
A = Register()
R = Register()
B = Register()
C = Register()
D = Register()
E = Register()
F = Register()
# P1 = Register()
# P2 = Register()


def print_registers():
    """
    Print the content of all the registers.
    """
    print('M:', M.reg)
    print('A:', A.reg)
    print('R:', R.reg)
    print('B:', B.reg)
    print('C:', C.reg)
    print('D:', D.reg)
    print('E:', E.reg)
    print('F:', F.reg)


def print_result(value):
    """
    Print result and fill zeros.
    """
    print(f"{value}{''.join(['0' for _ in range(n_digits-str(value)[::-1].find('.'))])}")


def loop():
    """
    Main loop.
    """
    global previous_key
    global previous_key_backup
    global n_digits
    
    while True:
        # Get input key from user.
        pressed_key = input()
        if len(pressed_key) != 1:  # skip invalid input
            continue

        # Process key: 0, 1, 2, 3, 4, 5, 6, 7, 8, 9.
        if pressed_key in '0123456789':
            if previous_key in '0123456789,':
                if not M.is_full():  # add digit to M register
                    M.shift()
                    M.reg[0] = int(pressed_key)
                else:
                    print('error: M.reg is full')
            else:
                M.erase()  # erase M register
                M.reg[0] = int(pressed_key)
                
        # Process key: ,.
        elif pressed_key == ',':
            if previous_key in '0123456789':
                M.float_active = True
            else:  # ignore key
                continue

        # Process key: sign -.
        elif pressed_key == '_':
            M.sign = '-'

        # Process key: +.
        elif pressed_key == '+':
            value = M.read_register() + A.read_register()
            A.write_register(value)

        # Process key: operator -.
        elif pressed_key == '-':
            value = M.read_register() - A.read_register()
            A.write_register(value)

        # Process key: ×.
        elif pressed_key == '×':
            # Compute product.
            value = M.read_register() * A.read_register()
            # Write registers A and R and print result.
            A.write_register(value)
            R.write_register(value)
            print_result(value)

        # Process key: ÷.
        elif pressed_key == '÷':
            try:
                value = M.read_register() / A.read_register()
                if not n_digits:
                    R.write_register(M.read_register() % A.read_register())
            except ZeroDivisionError:
                print('error: division by zero')
                continue
            A.write_register(value)
            print_result(value)

        # Process key: √.
        elif pressed_key == '√':
            value = M.read_register()
            if value < 0:
                print('error: squared root of negative number')
                continue
            # Compute squared root.
            value = value ** 0.5
            # Write A and M registers and print result.
            A.write_register(value)
            M.write_register(2 * value)
            print_result(value)
            
        # Process key: ◊.
        elif pressed_key == '◊':
            if previous_key in 'BCDEF':  # print selected register
                exec(f'print({previous_key}.read_register())')
            else:  # print M register by default
                print_result(M.read_register())

        # Process key: *.
        elif pressed_key == '*':
            if previous_key in 'ARBCDEF':  # print selected register
                exec(f'print({previous_key}.read_register())')
                if pressed_key != 'R':  # erase register if not R
                    exec(f'{pressed_key}.erase()')
            else:
                print_result(M.read_register())

        # Process key: r.
        elif pressed_key == 'r':
            M.erase()
            A.erase()
            R.erase()
            B.erase()
            C.erase()
            D.erase()
            E.erase()
            F.erase()

        # Process key: r.
        elif pressed_key == 'u':
            previous_key = previous_key_backup

        # Process key: ↓.
        elif pressed_key == '↓':
            A.reg = M.reg

        # Process key: ↑.
        elif pressed_key == '↑' and previous_key in 'BCDEF':
            exec(f'{previous_key}.reg = M.reg')

        # Precess key: ↕.
        elif pressed_key == '↕':
            if previous_key == 'A':
                A.write_register(abs(A.read_register()))
            elif previous_key in 'BCDEF':
                value = A.read_register()
                exec(f'A.write_register({previous_key}.read_register())\n'
                     f'{previous_key}.write_register(value))')

        # Process key d.
        elif pressed_key == 'd':
            n_digits = input()

        # Debug key.
        elif pressed_key == 'P':
            print_registers()
            breakpoint()
        
        previous_key = pressed_key  # update previous key
        previous_key_backup = previous_key


if __name__ == "__main__":
    loop()
