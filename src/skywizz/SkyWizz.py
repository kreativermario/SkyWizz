import tkinter as tk
from src.utils.airport_functions import distance_between_airports, get_airport_info


class SkyWizz:
    def __init__(self, master):
        """
        Constructor method that initializes the GUI and creates a container
        that is updated for each sub-menu
        :param master: Tkinter Window
        """
        self.search_airport = None
        self.content_frame = None
        self.title_label = None
        self.content_label = None

        self.master = master
        self.master.title('SkyWizz')

        # Create a frame to contain all the widgets
        self.container = tk.Frame(self.master)
        self.container.pack(fill='both', expand=True)

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
        self.content_frame = tk.Frame(self.container)
        self.content_frame.pack(padx=20, pady=20)

        # Creates the title label
        self.title_label = tk.Label(self.content_frame, text='SkyWizz',
                                    font=('Montserrat', 20))
        self.title_label.pack()

        # Create a label for the content
        self.content_label = tk.Label(self.content_frame,
                                      text='Welcome to SkyWizz!')
        self.content_label.pack(pady=10)

        # Create a button widget
        search_airport_button = tk.Button(self.content_frame,
                                          text='Get Airport Info by Code',
                                          command=self.airport_info_window)
        search_airport_button.pack(pady=10)

        # Create a button widget for submitting search
        distance_between_airports_button = tk.Button(
            self.content_frame,
            text='Distance between airports',
            command=self.distance_airports_window)
        distance_between_airports_button.pack(pady=10)

        # # Create a menu bar
        # self.menu_bar = tk.Menu(master)
        #
        # # Create a file menu with options
        # self.options_menu = tk.Menu(self.menu_bar, tearoff=0)
        # self.options_menu.add_command(label='Search by Airport Code',
        # command=self.search_airport)
        # self.options_menu.add_cascade(label='Menu', menu=self.options_menu)
        #
        # master.config(menu=self.menu_bar)

    def distance_airports_window(self):
        """
        GUI Window that updates to show the submit form to get distance
        info between two airports
        :return:
        """
        # Remove old frame and create a new frame
        self.content_frame.destroy()
        self.content_frame = tk.Frame(self.container)
        self.content_frame.pack(padx=20, pady=20)

        # Create a label for the first airport
        airport1_label = tk.Label(self.content_frame, text='1st Airport: ')
        airport1_label.pack()

        # Creates an entry field for the first airport
        airport1_label_entry = tk.Entry(self.content_frame)
        airport1_label_entry.pack()

        # Create a label for the second airport
        airport2_label = tk.Label(self.content_frame, text='2nd Airport: ')
        airport2_label.pack()

        # Creates an entry field for the second airport
        airport2_label_entry = tk.Entry(self.content_frame)
        airport2_label_entry.pack()

        # Create a button widget for submitting search
        submit_button = tk.Button(self.content_frame, text='Submit',
                                  command=lambda:
                                  self.get_distance_between_airports(
                                      airport1_label_entry,
                                      airport2_label_entry))
        submit_button.pack()

        # Create a button widget to go back to the main menu
        back_button = tk.Button(self.content_frame, text='Back',
                                command=self.show_main_menu)
        back_button.pack()

    def airport_info_window(self):
        """
        GUI window that updates to show the
        :return:
        """
        # Remove old frame and create a new frame
        self.content_frame.destroy()
        self.content_frame = tk.Frame(self.container)
        self.content_frame.pack(padx=20, pady=20)

        # Create a label for the departure airport
        depart_label = tk.Label(self.content_frame, text='Departure Airport:')
        depart_label.pack()

        # Creates an entry field for the departure airport ICAO code
        airport_entry = tk.Entry(self.content_frame)
        airport_entry.pack()

        # Create a button widget for submitting search
        submit_button = tk.Button(self.content_frame, text='Submit',
                                  command=lambda:
                                  self.get_airport_info(airport_entry))
        submit_button.pack()

        # Create a button widget to go back to the main menu
        back_button = tk.Button(self.content_frame, text='Back',
                                command=self.show_main_menu)
        back_button.pack()

    def get_airport_info(self, airport_entry):
        """
        Function that treats the data input by the user from the
        airport_info_window GUI
        :param airport_entry: Data input that is the airport code
        :type: airport_entry: str
        :return:
        """
        # Get the departure airport code from the airport_entry field
        airport_code = airport_entry.get()
        airport_info_text = ""
        try:
            airport_info_text = get_airport_info(airport_code)
        except Exception as e:
            # Handle the exception by displaying an error message
            airport_info_text = f'Error fetching data: {str(e)}'

        # Create a new popup window
        popup = tk.Toplevel(self.master)

        # Create a text widget to display the airport status
        status_text = tk.Text(popup, wrap=tk.WORD, font=('Montserrat', 12))
        status_text.insert(tk.END, airport_info_text)
        status_text.config(state=tk.DISABLED)
        status_text.pack(fill=tk.BOTH, expand=True)

    def get_distance_between_airports(self, depart_entry, arrival_entry):
        """
        Function that treats the data input by the user from the
        distance_airports_window GUI
        :param depart_entry: Departure airport code
        :param arrival_entry: Arrival airport code
        :return:
        """
        # Get the departure airport code from the depart_entry field
        depart_airport_code = depart_entry.get()
        arrival_airport_code = arrival_entry.get()
        distance_text = ""
        try:
            # Call API
            distance_text = distance_between_airports(depart_airport_code,
                                                      arrival_airport_code)
        except Exception as e:
            # Handle the exception by displaying an error message
            distance_text = f'Error fetching data: {str(e)}'

        # Create a new popup window
        popup = tk.Toplevel(self.master)

        # Create a text widget to display the airport status
        status_text = tk.Text(popup, wrap=tk.WORD, font=('Montserrat', 12))
        status_text.insert(tk.END, distance_text)
        status_text.config(state=tk.DISABLED)
        status_text.pack(fill=tk.BOTH, expand=True)

# if __name__ == '__main__':
#     # Creates the main window
#     window = tk.Tk()
#     sky_wizz = SkyWizz(window)
#     window.mainloop()
