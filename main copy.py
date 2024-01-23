import subprocess
import os
import openai
import shlex
import keyboard
from colorama import *
from termcolor import colored, cprint
import curses
import time
from translatetext import TextPredictionAPI

# Initialize the TextPredictionAPI
api = TextPredictionAPI()

# Global variable for tracking the working directory
workingdir = os.getcwd()
global checkmanmode
# Initialize colorama
init()

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

def write_data(file_path, input_string):
    with open(file_path, 'a') as file:
        file.write(input_string + '\n')

def auto_correct(input_string):
    """Function to auto-correct the input_string using TextPredictionAPI"""
    try:
        corrected = api.wordCompletion(input_string)[0]
        return corrected
    except:
        return input_string

def interactive_input(prompt):
    """Capture user input interactively and handle auto-correction on TAB press."""
    print(prompt, end='', flush=True)
    user_input = ""
    
    while True:
        # Capture key events
        if keyboard.is_pressed('TAB'):
            # Auto-correct the user's input
            corrected = auto_correct(user_input)
            # Clear the current line
            print('\r', end='', flush=True)
            print(' ' * (len(prompt) + len(user_input)), end='', flush=True)
            print('\r', end='', flush=True)
            print(prompt + corrected, end='', flush=True)
            user_input = corrected
            while keyboard.is_pressed('TAB'):  # wait until TAB is released
                pass
        elif keyboard.is_pressed('ENTER'):
            print()  # move to the next line
            return user_input
        else:
            char = keyboard.read_event(suppress=True).name
            if char.startswith('KEY_'):
                char = char[4:].lower()
            if len(char) == 1:
                user_input += char
                print(char, end='', flush=True)
            elif char == 'space':
                user_input += ' '
                print(' ', end='', flush=True)
            elif char == 'backspace':
                user_input = user_input[:-1]
                print('\r', end='', flush=True)
                print(' ' * (len(prompt) + len(user_input) + 1), end='', flush=True)
                print('\r', end='', flush=True)
                print(prompt + user_input, end='', flush=True)
            time.sleep(0.01)

def execute_command(cmd):
    try:
        global workingdir
        write_data('Big.txt', cmd)
        if cmd.startswith('clrwindow'):
            clear_console()
            return 0
        if cmd.startswith('exit') or cmd.startswith('quit'):
            exit()
        if cmd.startswith('cd '):
            path = cmd.split(' ', 1)[1]
            # If the path is surrounded by quotes, remove them
            if path.startswith('"') and path.endswith('"'):
                path = path[1:-1]
            if path == '..':
                workingdir = os.path.dirname(workingdir)
            elif '..' in path:
                levels_up = path.count('..')
                workingdir = os.path.normpath(workingdir + '/' + '/'.join(['..'] * levels_up))
            else:
                potential_path = os.path.join(workingdir, path)
                if os.path.isabs(path):
                    potential_path = path
                if os.path.exists(potential_path):
                    workingdir = potential_path
                else:
                    raise Exception("The system cannot find the path specified: '"+potential_path+"'")
            return 0
        else:
            cmd = shlex.split(cmd)
            p = subprocess.Popen(cmd, cwd=workingdir, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            while True:
                output = p.stdout.readline().decode('utf-8')
                if output == '' and p.poll() is not None:
                    break
                if output:
                    print(colored(output.strip(), 'light_grey'))
            rc = p.poll()
            return rc
    except Exception as e:
        print('An error occurred in running the interpreter: ' + str(e))
        return 1

try:
    openai.api_key = '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'

    messages = [
        {"role": "system", "content": f'You are Alpilaz Compute-Line (version 1.2.0 made by Kevin Dalli), a helpful Command line interpreter tool. you have direct access to the users command line, when the user inputs a command in standard english, for example "create a new file" then you will execute the command in standard command line notation depending on the users system type, this data will be given to you together with the first command request.\nfor example:\nuser: "create a text file"\nassistant: "echo. > text.txt"\nyou can also use context from previous executed commands to understand what the user is implying.\nif you want to output something in the channel for the user to see (like a reminder or a note, or a response to a users question) you can type printcmd"whatever you want to be seen in channel" USE THIS FOR ALL NORMAL CONVERSATIONAL TASKS. everything you type in chat will be interpreted as a command, so if you want to ask for permission or confirmation for something use printcmd"input" as described above, if you want to print multiple lines use the standard backslash n newline character.\nremember NEVER say anything normally, if you want to tell the user something use the command specified. If you want to clear the users command line window, then use clrwindow command. You cannot run multiple commands together, like clrwindow and printcmd and run system commands, only one at a time. you must follow these rules to the point. reply with "Understood" if you understand these instructions.\nThe users current system is running:\n{os.name}'}
    ]
except Exception as e:
    print('An error occured in initializing OpenAI: ' + str(e))
    checkmanmode = 'manmode'

def gen():
    while True:
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=messages
            )
            assistant_message = response['choices'][0]['message']['content']
            if assistant_message != 'Understood' and not assistant_message.startswith('printcmd'):
                print('\n' + Fore.LIGHTBLACK_EX + "<<INT>> : ", assistant_message)
            print(colored('\-----------------------------------------------------------/', 'red'))
            if assistant_message.startswith('printcmd'):
                assistant_message = assistant_message[8:].strip('\"').replace(r'\\n', '\n')
                lines = assistant_message.split(r'\n')
                for line in lines:
                    print(line)
            elif assistant_message.startswith('Understood'):
                print('Initiating Command Line Interpreter...')
            else:
                rc = execute_command(assistant_message)    
                if rc != 0:
                    print(f'Error: Command "{assistant_message}" exited with return code {rc}')
            
            user_message = interactive_input(Fore.WHITE + "|" + Fore.LIGHTYELLOW_EX + "--" + Fore.YELLOW + "\\" + Fore.LIGHTRED_EX + "[" + Fore.RED + "|ALPILAZ COMPUTE-LINE|" + Fore.LIGHTRED_EX + "]" + Fore.YELLOW + "\\" + Fore.LIGHTYELLOW_EX + "-" + Fore.WHITE + "@~ " + workingdir + Fore.LIGHTBLACK_EX + " > >  ")
        
            # Check if the TAB key is pressed for auto-correction
            if keyboard.is_pressed('TAB'):
                user_message = auto_correct(user_message)

            if user_message == 'manmode':
                return 'manmode'
            messages.append({"role": "user", "content": user_message})
        except Exception as e:
            print('An error occured in backend startup... ' + str(e))
            return True

def man():
    print(colored("Initiating Command Line Interpreter in MANUAL MODE...\n", 'black', 'on_red'))
    while True:
        print(Fore.RED + r'\-----------------------------------------------------------/')
        user_message = interactive_input(Fore.WHITE + "|" + Fore.LIGHTYELLOW_EX + "--" + Fore.YELLOW + "\\" + Fore.LIGHTRED_EX + "[" + Fore.RED + "|ALPILAZ COMPUTE-LINE|" + Fore.LIGHTRED_EX + "]" + Fore.YELLOW + "\\" + Fore.LIGHTYELLOW_EX + "-" + Fore.WHITE + "@~ " + workingdir + " " + colored(r"-[DM]-", 'black', 'on_red') + Fore.LIGHTBLACK_EX + " > >  ")

        # Check if the command is 'manmode'
        if user_message == 'manmode':
            print("You are already in MANUAL MODE.")
            continue

        rc = execute_command(user_message)
        if rc != 0:
            print(f'Error: Command "{user_message}" exited with return code {rc}')
        
        if user_message == 'automode':
            return 'automode'
        
        if user_message == 'exit':
            return 'exit'

def main():
    mode = 'gen'  # Start with the automated mode by default
    while True:
        if mode == 'gen':
            mode = gen()  # It will return either 'manmode' or 'exit'
        elif mode == 'manmode':
            mode = man()  # It will return either 'automode' or 'exit'
        elif mode == 'automode':
            mode = 'gen'  # Switch back to the automated mode
        elif mode == 'exit':
            break
        
if __name__ == '__main__':
    main()