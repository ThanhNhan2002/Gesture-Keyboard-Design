import tkinter as tk

import keyboard_design as kd
import recognizer
from template import Point, WordTemplates

# pNote
import tkinter.messagebox

class Application(tk.Frame):
    def __init__(self, window_width, window_height, master=None):
        super().__init__(master)  # Call tk.Frame.__init__(master)
        self.master = master  # Update the master object after tk.Frame() makes necessary changes to it
        frame_bottom_height = 200
        frame_middle_height = 50
        frame_top_height = window_height - frame_bottom_height - frame_middle_height

        # the top frame is used to show input words in the text
        frame_top = tk.Frame(self.master)
        frame_top.place(x=0, y=0, width=window_width, height=frame_top_height)

        self.text = tk.Text(frame_top, bg='white', borderwidth=2, relief='groove', font=('Arial', 20))
        self.text.place(x=0, y=0, width=window_width, height=frame_top_height)
        self.text.bind("<Triple-1>", self.mouse_left_triple)

        # the middle frame is used to list word candidates (four labels)
        frame_middle = tk.Frame(self.master)
        frame_middle.place(x=0, y=frame_top_height, width=window_width, height=frame_middle_height)

        word_candidate_num = 4
        self.label_word_candidates = []  # labels used to show word candidates
        for i in range(word_candidate_num):  # the values 0 to (word_candidate_num - 1)
            label_word = tk.Label(frame_middle, bg='white', borderwidth=2, relief='groove', font=15) #anchor='w',
            label_word.place(relx=i/word_candidate_num, relwidth=1/word_candidate_num, height=frame_middle_height)
            label_word.bind("<ButtonRelease-1>", self.select_word_candidate)
            print(i/word_candidate_num)
            self.label_word_candidates.append(label_word)

        # the bottom frame is used to show the keyboard
        frame_bottom = tk.Frame(self.master)
        frame_bottom.place(x=0, y=(frame_top_height + frame_middle_height), width=window_width,
                           height=frame_bottom_height)

        self.canvas_keyboard = tk.Canvas(frame_bottom, bg='light gray', borderwidth=2, relief='groove')
        self.canvas_keyboard.place(x=0, y=0, width=window_width, height=frame_bottom_height)

        self.keyboard = kd.Keyboard(self.canvas_keyboard)
        self.keyboard.keyboard_layout()

        # generate word templates
        templates = WordTemplates(self.keyboard.get_keys())

        # generate a recognizer
        self.word_recognizer = recognizer.Recognizer(templates.set_templates())
        self.gesture_points = []

        # mouse events on the canvas keyboard
        self.canvas_keyboard.bind("<ButtonPress-1>", self.mouse_left_button_press)
        self.canvas_keyboard.bind("<ButtonRelease-1>", self.mouse_left_button_release)
        self.canvas_keyboard.bind("<B1-Motion>", self.mouse_move_left_button_down)
        self.canvas_keyboard.bind("<Double-Button-1>", self.left_double_click)

        self.canvas_keyboard.bind("<ButtonPress-3>", self.mouse_right_button_press)
        self.canvas_keyboard.bind("<ButtonRelease-3>", self.mouse_right_button_release)
        self.canvas_keyboard.bind("<B3-Motion>", self.mouse_move_right_button_down)

        self.canvas_keyboard.bind("<Triple-1>", self.mouse_left_triple_keyboard)

        # store x, y, segment tag
        self.cursor_move_position_list = []

        # store the tag for each segment of the drawn gesture
        self.line_tag = []

        # pNote:
        self.command_mode_status = False
        self.possible_commands = ['copy', 'redo', 'undo', 'save']

        self.just_triple_click = False
        self.just_triple_click_letter = ''
        self.triple_click_done = False
        self.press_after_triple = False
    def left_double_click(self, event):
        key_pressed = self.keyboard.get_key_pressed()  # return pressed key in a string format
        if(key_pressed == 'Caps'):
            self.switch_command_mode_status()
        # else:
            # Label.cget() returns the old text in label 1 a string format
            # first_label = self.label_word_candidates[0].cget("text")
            # new_label = first_label + key_pressed  # old text + newly pressed key
            # new_label = key_pressed
            # self.label_word_candidates[0].config(text=new_label)

    def mouse_left_triple(self, event):
        self.switch_command_mode_status()

    def mouse_left_triple_keyboard(self, event):
        self.just_triple_click = True
        self.just_triple_click_letter = self.keyboard.get_key_pressed()
        self.triple_click_done = False

    def switch_command_mode_status(self):
        self.command_mode_status = True if (self.command_mode_status is False) else False
        print(f'Command mode: {self.command_mode_status}')
        if self.command_mode_status:
            self.clear_word_labels()

    def clear_word_labels(self):  # clear the content of all word labels
        for i in range(len(self.label_word_candidates)):  # clear the content of all word labels
            self.label_word_candidates[i].config(text='')

    def execute_command(self, command):
        message = ''
        if len(command) > 0 and command in self.possible_commands:
            # print(f'Command input: {command}')
            message = f'Command input: {command}'
            # tk.messagebox.showinfo(title="Message box", message=message)
        else:
            # print(f'Not a command')
            message = f'Not a command'
        tk.messagebox.showinfo(title="Message box", message=message)
        # tk.messagebox.showinfo(title="just_triple_click_letter", message=self.just_triple_click_letter)
        # tk.messagebox.showinfo(title="just_triple_click", message= self.just_triple_click)
        # print(f'triple-click-letter: {self.just_triple_click_letter}')
        # print(f'just_triple_click: {self.just_triple_click}')
        # print(f'triple_click_done: {self.triple_click_done}')

    # when users select a word candidate from the four labels in the middle frame
    def select_word_candidate(self, event):
        btn = event.widget  # event.widget is the widget that called the event
                            # pNote: here is the Label
        #self.label_show_text.config(text=btn.cget('text'))
        self.text.insert(tk.END, btn.cget('text') + " ") # show it to the text widget
        # pNote: text widget is in frame top

        self.clear_word_labels()

    # press mouse left button
    def mouse_left_button_press(self, event):
        self.cursor_move_position_list.append([event.x, event.y, 0])  # store x, y, segment tag
        self.keyboard.key_press(event.x, event.y)
        self.gesture_points.clear()
        if self.triple_click_done:
            self.press_after_triple = True;
        #self.gesture_points.append(Point(event.x, event.y))

    # release mouse left button
    def mouse_left_button_release(self, event):
        if (len(self.cursor_move_position_list) > 0):
            previous_x = self.cursor_move_position_list[-1][0]
            previous_y = self.cursor_move_position_list[-1][1]
            line_tag = self.canvas_keyboard.create_line(previous_x, previous_y, event.x, event.y)
            self.cursor_move_position_list.append([event.x, event.y, line_tag])

            self.keyboard.key_release(event.x, event.y)
        # if it is in this stage, then a letter has been pressed 3 times and and the 3rd release has been done
        # then, we must consider that the progress of triple-clicking a letter has been finished
        if self.just_triple_click and not self.triple_click_done:  # self.triple_click_done = false
            self.triple_click_done = True

        result = self.word_recognizer.recognize(self.gesture_points)  # pNote: result of the pattern
        key = self.keyboard.get_key_pressed()  # pNote: last pressed key
        print(f'result: {result}')
        if not self.command_mode_status:
            if len(result) > 0:  # pNote: valid result, system returns some recommendation
                print(f'result > 0')
                print('called from inside if self.just_triple_click')
                print(f'is triple click done: {self.triple_click_done}')
                if self.press_after_triple:
                    # pNote: if users just have drawn a pattern after triple-clicking a letter,
                    # check if it is the beginning of a command
                    # e.g. if triple-clicked letter 's', then the command must be 'save'
                    # triple-clicked letter 's' and then entering command 'undo' is not accepted
                    print(f'first letter of the result: {result[0][1][0].upper()}')
                    print(f'triple-clicked letter: { self.just_triple_click_letter.upper()}')
                    if result[0][1] in self.possible_commands and result[0][1][0].upper() == self.just_triple_click_letter.upper():
                        self.execute_command(result[0][1])
                    else:
                        self.execute_command('Not a command')
                    self.just_triple_click = False
                    self.just_triple_click_letter = ''
                    self.triple_click_done = False
                    self.press_after_triple = False
                # elif self.just_triple_click and not self.triple_click_done:  # self.triple_click_done = false
                #     self.triple_click_done = True
                elif self.just_triple_click and not self.press_after_triple:
                    self.clear_word_labels()

                else:  # then it's not a request for command input, show the suggestions
                    for i in range(len(result)):
                        if i < len(self.label_word_candidates):
                            self.label_word_candidates[i].config(text=result[i][1])
                        else:
                            break
            else:  # pNote: invalid result, aka only 1 button is pressed, not a pattern
                if key == '<--':  # remove the final character from the text
                    length = len(self.text.get("1.0", 'end-1c'))
                    if length > 0:
                        self.text.delete("end-2c") # remove the last character
                elif key == 'Cmd':
                    self.switch_command_mode_status()
                '''
                else:  # not the delete key ("<--")
                    characters = self.label_word_candidates[0].cget("text")
                    characters += self.keyboard.get_key_pressed().lower()  # convert to lowercase
                    self.label_word_candidates[0].config(
                        text=characters)  # only one key was pressed
                '''
        else: # pNote: this means that command mode is on
            if len(result) > 0:
                self.execute_command(result[0][1])
            else:
                if key == 'Cmd':
                    self.switch_command_mode_status()

        if len(self.cursor_move_position_list) > 1:  # delete cursor trajectory
            for x in self.cursor_move_position_list[1:]:
                self.canvas_keyboard.delete(x[2])
            self.cursor_move_position_list = []

    # users drag the mouse cursor on the keyboard while pressing the left button: drawing gestures on the keyboard
    def mouse_move_left_button_down(self, event):
        if (len(self.cursor_move_position_list) > 0):
            previous_x = self.cursor_move_position_list[-1][0]
            previous_y = self.cursor_move_position_list[-1][1]

            line_tag = self.canvas_keyboard.create_line(previous_x, previous_y, event.x, event.y)  # draw a line
            self.cursor_move_position_list.append([event.x, event.y, line_tag])

        self.keyboard.mouse_move_left_button_down(event.x, event.y)
        self.gesture_points.append(Point(event.x, event.y))  # store all cursor movement points





















    #right mouse button
    def mouse_right_button_press(self, event):
        self.cursor_move_position_list.append([event.x, event.y, 0])  # store x, y, segment tag
        self.keyboard.key_press(event.x, event.y)
        self.gesture_points.clear()

        # self.gesture_points.append(Point(event.x, event.y))

    # release mouse right button
    def mouse_right_button_release(self, event):
        if (len(self.cursor_move_position_list) > 0):
            previous_x = self.cursor_move_position_list[-1][0]
            previous_y = self.cursor_move_position_list[-1][1]
            line_tag = self.canvas_keyboard.create_line(previous_x, previous_y, event.x, event.y)
            self.cursor_move_position_list.append([event.x, event.y, line_tag])

        self.keyboard.key_release(event.x, event.y)
        result = self.word_recognizer.recognize(self.gesture_points)
        if (len(result) > 0):
            print('command input triggered by right mouse button')
            self.execute_command(result[0][1])

        if len(self.cursor_move_position_list) > 1:  # delete cursor trajectory
            for x in self.cursor_move_position_list[1:]:
                self.canvas_keyboard.delete(x[2])

    # users drag the mouse cursor on the keyboard while pressing the left button: drawing gestures on the keyboard
    def mouse_move_right_button_down(self, event):
        if (len(self.cursor_move_position_list) > 0):
            previous_x = self.cursor_move_position_list[-1][0]
            previous_y = self.cursor_move_position_list[-1][1]

            line_tag = self.canvas_keyboard.create_line(previous_x, previous_y, event.x, event.y)  # draw a line
            self.cursor_move_position_list.append([event.x, event.y, line_tag])

        self.keyboard.mouse_move_left_button_down(event.x, event.y)
        self.gesture_points.append(Point(event.x, event.y))  # store all cursor movement points










if __name__ == '__main__':
    master = tk.Tk()
    window_width = 500
    window_height = 600
    master.geometry(str(window_width) + 'x' + str(window_height))  # master.geometry('500x600')
    master.resizable(0, 0)  # can not change the size of the window
    app = Application(window_width, window_height, master=master)
    app.mainloop()  # mainloop() tells Python to run the Tkinter event loop. This method listens for events, such as button clicks or keypresses, and blocks any code that comes after it from running until the window it's called on is closed.
