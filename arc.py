import sys
import re
from ast import literal_eval
import pprint

# 32 registors
registers = [0] * 32
# Holds memory location of labels
symbol_table = dict()
# Holds memory
execution_table = dict()
# Program counter initialized at first pass
program_counter = 0
# Instead of using flags just going to make it previous value
program_status_reg = 0

def main():
    
    with open(sys.argv[1], 'r') as f:
        commands = [(line.split()) for line in f.readlines()]

    # Create Symbol and Execution(Memory) Table
    first_pass(commands)
    # Evaluate Instructions
    second_pass()

    print("Finished!\n")
    print(f'Registers:\n\n {registers}')
    print("\nSymbol Table:\n")
    pprint.pprint(symbol_table)
    print("\nMemory Table:\n")
    pprint.pprint(execution_table)
    

def first_pass(commands):

    global program_counter
    global  execution_table
    global symbol_table

    location_counter = 0
    begin_index = 0

    for i in range(len(commands)):
        if commands[i][0] == '.org':
            location_counter = literal_eval(commands[i][1])
            program_counter = location_counter 
            begin_index = i+1
            break
            
    for command in commands[begin_index:]:
        if ':' in command[0]:
            symbol_table[command[0][:-1]] = location_counter
            execution_table[location_counter] = command[1:]
            location_counter+=4 # Only increment for instructions
        elif '.equ' in command:
            symbol_table[command[0]] = literal_eval(command[2])
        elif command[0] == '.org':
            if command[1].isdigit() or command[1][0] == '0': # Check for base 10 and base 16
                location_counter = literal_eval(command[1])
            else:
                location_counter = symbol_table[command[1]]
        else:
            execution_table[location_counter] = command
            location_counter+=4 # Only increment for instructions

        

def second_pass():

    global registers
    global program_counter
    global execution_table
    global program_status_reg

    while(execution_table[program_counter][0] != '.end'):
        curr_command = execution_table[program_counter]
        
        # Memory Instructions        
        if curr_command[0] == 'ld':
            mem_location = symbol_table[curr_command[1][1]]
            reg_num = int(re.findall(r'\d+' ,curr_command[2])[0])
            registers[reg_num] = literal_eval(execution_table[mem_location][0])
        elif curr_command[0] == 'st':
            reg_num = int(re.findall(r'\d+' ,curr_command[1])[0])
            mem_location = symbol_table[curr_command[2][1]]
            execution_table[mem_location] = [registers[reg_num]]
        # Branch
        elif curr_command[0] == 'be':
            # Check if equal to 0
            if program_status_reg == 0:
                mem_location = symbol_table[curr_command[1]]
                # Subtracting 4 because it gets incremented by 4 later
                program_counter = mem_location-4
        elif curr_command[0] == 'bneg':
            # Check if negative
            if program_status_reg < 0:
                mem_location = symbol_table[curr_command[1]]
                # Subtracting 4 because it gets incremented by 4 later
                program_counter = mem_location-4
        elif curr_command[0] == 'bvs':
            # Check if V is 1
            if program_status_reg > (2**32 - 1):
                mem_location = symbol_table[curr_command[1]]
                # Subtracting 4 because it gets incremented by 4 later
                program_counter = mem_location-4
        elif curr_command[0] == 'ba':
            mem_location = symbol_table[curr_command[1]]
            # Subtracting 4 because it gets incremented by 4 later
            program_counter = mem_location-4
        # Call/Jump
        elif curr_command[0] == 'call':
            mem_location = symbol_table[curr_command[1]]
            registers[15] = program_counter # Set link register to current PC
            # Subtracting 4 because it gets incremented by 4 later
            program_counter = mem_location-4
        elif curr_command[0] == 'jmpl':
            # Jump to is not in current memory so stop
            if registers[15] not in execution_table.keys():
                break
            program_counter = registers[15] # Jump back to call
        # Logic/Arithmetic
        elif curr_command[0] == 'addcc':
            logic_aritmetic(curr_command, lambda x,y: x + y)
        elif curr_command[0] == 'subcc':
            logic_aritmetic(curr_command, lambda x,y: x - y)
        elif curr_command[0] == 'andcc':
            logic_aritmetic(curr_command, lambda x,y : x & y)
        elif curr_command[0] == 'orcc':
            logic_aritmetic(curr_command, lambda x,y : x | y)
        elif curr_command[0] == 'srl':
            logic_aritmetic(curr_command, lambda x,y : x >> y)
        elif curr_command[0] == 'sethi':
            if curr_command[1].isdigit() or curr_command[1][0] == '0': # Check for base 10 and base 16
                rs1 = literal_eval(curr_command[1])
            else:
                rs1 = symbol_table[curr_command[1]]
            
            rsd = int(re.findall(r'\d+' ,curr_command[2])[0])
            registers[rsd] = rs1 << 10
            

        program_counter += 4

# Perform logic/aritmetic instruction
def logic_aritmetic(curr_command, func):

    global registers
    global program_status_reg

    rs1 = registers[int(re.findall(r'\d+' ,curr_command[1])[0])]
    if curr_command[2][0] == '%':
        rs2 = registers[int(re.findall(r'\d+' ,curr_command[2])[0])]
    else:
        rs2 = literal_eval(re.findall(r'\d+' ,curr_command[2])[0])
    rsd = int(re.findall(r'\d+' ,curr_command[3])[0])

    program_status_reg = func(rs1, rs2)
    if rsd != 0:
        registers[rsd] = program_status_reg


if __name__ == '__main__':
    main()
