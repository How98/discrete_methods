DESCRIPTION OF THE SCRIPT

the script math_logic.py has an input of a logical expression in a string form and has three options to operate with it:

-Evaluate: with this option you can evaluate the logical expression with specific values requested as a new input

-TruthTable: with this option you can evaluate all the possible outputs of the expression in a dataframe

-Debugging: this option shows the debugging output, showing the steps in the process and additional logs giving information omited in the previous steps

EXECUTION METHOD:

this script comes with a requirements.txt file to install the virtual environment it should work for python 3.10 forwards. It doesn't require many libraries but in case
it doesn't work at the for the first time you can install the requirements with the following code:
    pip install -r requirements.txt
detail: you have to use this command with the virtual environment activated. To activate it on the terminal you can use the following command (on linux, in windows it might change a little):
    source environmentFolderPath/Bin/activate

After activateing the virtual environment you can execute the script with the following command:
    python math_logic.py

IMPORTANT INFORMATION:

The script doesn't have much error handling, so in case of error execute it again with the correct expression, operators availabre are shownat the beginning of the script
