import curses
import time
from translatetext import TextPredictionAPI

# Initialize the API
api = TextPredictionAPI()

def main(stdscr):
    user_input = ""
    while True:
        c = stdscr.getch()

        if c == ord('\n'):  # The 'Enter' key was pressed
            if user_input == 'exit':
                break
            stdscr.addstr('incorrect: ' + user_input + '\n')

            # Reset the user input
            user_input = ""

        elif c == ord('`'):  # The '`' key was pressed
            stdscr.addstr('Function executed!\n')
            correct = api.wordCompletion(user_input)[0]
            stdscr.addstr('correct: ' + correct + '\n')

        else:  # Any other character was entered
            # Append the character to the user input
            user_input += chr(c)

        # Sleep for a bit to reduce CPU usage
        time.sleep(0.01)

curses.wrapper(main)