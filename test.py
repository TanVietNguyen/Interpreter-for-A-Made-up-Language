import os
from interpreterv2 import Interpreter

# Directory with .br files
directory = './fails'

# Loop through all .br files in the specified directory
for filename in os.listdir(directory):
    if filename.endswith('.br'):
        file_path = os.path.join(directory, filename)
        print(f"Processing file: {file_path}")

        with open(file_path, 'r') as file:
            content = file.read()

            # Extract expected output between *OUT* markers if present
            expected_output = None
            if '/*' in content and '*OUT*' in content:
                expected_output = content.split('*OUT*')[1].strip().split('\n')[0]

            # Run the interpreter on the file content
            try:
                interpreter = Interpreter()
                actual_output = interpreter.run(content)

                # Compare actual output to expected output
                if expected_output:
                    if str(actual_output).strip() == expected_output:
                        print(f"{filename}: PASS")
                    else:
                        print(f"{filename}: FAIL")
                        print(f"Expected: {expected_output}, but got: {actual_output}")
                else:
                    print(f"{filename}: No expected output to verify against.")
            except Exception as e:
                print(f"{filename}: Error encountered - {e}")
