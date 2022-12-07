import os
import sys

if "__main__" == __name__:
    argument_path = os.path.abspath(sys.argv[1])
    if os.path.isdir(argument_path):
        files_to_assemble = [
            os.path.join(argument_path, filename)
            for filename in os.listdir(argument_path)]
    else:
        files_to_assemble = [argument_path]
    for input_path in files_to_assemble:
        filename, extension = os.path.splitext(input_path)

        output_path = filename + ".xml"
        with open(input_path, 'r') as input_file, \
                open(output_path, 'w') as output_file:
            input = input_file.read().splitlines()
            a=[]
            for line in input:
                b=line.strip(" ")
                a.append(b)
                print(b)
            input_file=a


