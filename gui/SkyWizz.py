import tkinter as tk
from functions.main import airport_status


class SkyWizz:
    def __init__(self, master):
        self.master = master
        master.title("SkyWizz")

        # Creates the title label
        self.title_label = tk.Label(master, text="SkyWizz", font=("Montserrat", 20))
        self.title_label.pack()

        # Creates a label for the flight number
        self.flight_label = tk.Label(master, text="Flight Number:")
        self.flight_label.pack()

        # Create an entry field for the flight number
        self.flight_entry = tk.Entry(master)
        self.flight_entry.pack()

        # Creates a label for the departure airport
        self.depart_label = tk.Label(master, text="Departure Airport:")
        self.depart_label.pack()

        # Creates an entry field for the departure airport ICAO code
        self.depart_entry = tk.Entry(master)
        self.depart_entry.pack()

        # Creates a label for the arrival airport
        self.arrive_label = tk.Label(master, text="Arrival Airport:")
        self.arrive_label.pack()

        # Create an entry field for the arrival airport ICAO code
        self.arrive_entry = tk.Entry(master)
        self.arrive_entry.pack()

        # Create a button widget for submitting search
        self.submit_button = tk.Button(master, text="Submit", command=self.show_airport_status)
        self.submit_button.pack()

    def show_airport_status(self):
        # Get the departure airport code from the depart_entry field
        airport_code = self.depart_entry.get()
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
