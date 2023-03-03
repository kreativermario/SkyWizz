import tkinter as tk
import sys
import os
from functions.airport_functions import airport_status

# Add parent directory to Python path
parent_dir = os.path.abspath(os.path.join(os.getcwd(), '..'))
sys.path.append(parent_dir)


class SkyWizz:
    def __init__(self, master):
        self.search_airport = None
        self.content_frame = None
        self.title_label = None
        self.content_label = None

        self.master = master
        self.master.title("SkyWizz")

        self.show_main_menu()

    def show_main_menu(self):
        """
        Shows main menu with buttons
        :return:
        """
        if self.content_frame is not None:
            # Remove old frame and create a new frame
            self.content_frame.destroy()

        # Create a frame for the content
        self.content_frame = tk.Frame(self.master)
        self.content_frame.grid(row=4, column=0, columnspan=2)

        # Creates the title label
        self.title_label = tk.Label(self.content_frame, text="SkyWizz", font=("Montserrat", 20))
        self.title_label.grid(row=0, column=0, columnspan=2)

        # Create a label for the content
        self.content_label = tk.Label(self.content_frame, text="Welcome to SkyWizz!")
        self.content_label.grid(row=1, column=0, columnspan=2)

        # Create a button widget for submitting search
        search_airport_button = tk.Button(self.content_frame, text="Search by Airport Code",
                                               command=self.search_airport_window)
        search_airport_button.grid(row=2, column=0)

        # # Create a menu bar
        # self.menu_bar = tk.Menu(master)
        #
        # # Create a file menu with options
        # self.options_menu = tk.Menu(self.menu_bar, tearoff=0)
        # self.options_menu.add_command(label="Search by Airport Code", command=self.search_airport)
        # self.options_menu.add_cascade(label="Menu", menu=self.options_menu)
        #
        # master.config(menu=self.menu_bar)

    def search_airport_window(self):
        """
        Search airport window
        :return:
        """
        # Remove old frame and create a new frame
        self.content_frame.destroy()
        self.content_frame = tk.Frame(self.master)
        self.content_frame.grid(row=4, column=0, columnspan=2)

        # Create a label for the departure airport
        depart_label = tk.Label(self.content_frame, text="Departure Airport:")
        depart_label.grid(row=0, column=0)

        # Creates an entry field for the departure airport ICAO code
        depart_entry = tk.Entry(self.content_frame)
        depart_entry.grid(row=0, column=1)

        # Create a button widget for submitting search
        submit_button = tk.Button(self.content_frame, text="Submit",
                                       command=lambda: self.show_airport_status(depart_entry))
        submit_button.grid(row=1, column=0, columnspan=2)

        # Create a button widget to go back to the main menu
        back_button = tk.Button(self.content_frame, text="Back", command=self.show_main_menu)
        back_button.grid(row=2, column=0, columnspan=2)

    def show_airport_status(self, depart_entry):
        # Get the departure airport code from the depart_entry field
        airport_code = depart_entry.get()
        airport_status_text = ""
        try:

            # If it is IATA Code
            if len(airport_code) == 3:
                airport_status_text = airport_status(airport_code, "iata")
            # If it is ICAO Code
            elif len(airport_code) == 4:
                airport_status_text = airport_status(airport_code, "icao")
            else:
                airport_status_text = "Not a valid airport code format, please try using 3-4 characters\n" \
                                      "ICAO - 4 characters -> LPPT" \
                                      "\nIATA - 3 characters -> LIS"
        except Exception as e:
            # Handle the exception by displaying an error message
            airport_status_text = f"Error fetching data: {str(e)}"

        # Create a new popup window
        popup = tk.Toplevel(self.master)

        # Create a label to display the airport status
        status_label = tk.Label(popup, text=airport_status_text)
        status_label.pack()


if __name__ == '__main__':
    # Creates the main window
    window = tk.Tk()
    sky_wizz = SkyWizz(window)
    window.mainloop()
