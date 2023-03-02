import tkinter as tk

# Creates the main window
window = tk.Tk()
window.title("SkyWizz")

# Creates the title label
title_label = tk.Label(window, text="SkyWizz", font=("Montserrat", 20))
title_label.pack()

# Creates a label for the flight number
flight_label = tk.Label(window, text="Flight Number:")
flight_label.pack()

# Create an entry field for the flight number
flight_entry = tk.Entry(window)
flight_entry.pack()

# Creates a label  for the departure airport
depart_label = tk.Label(window, text="Departure Airport:")
depart_label.pack()

# Creates an entry field for the departure airport ICAO code
depart_entry = tk.Entry(window)
depart_entry.pack()

# Creates a label  for the arrival airport
arrive_label = tk.Label(window, text="Arrival Airport:")
arrive_label.pack()

# Create an entry field for the arrival airport ICAO code
arrive_entry = tk.Entry(window)
arrive_entry.pack()

# Create a button widget for submitting search
submit_button = tk.Button(window, text="Submit")
submit_button.pack()

# Start the main event loop
window.mainloop()
