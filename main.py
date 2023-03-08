import tkinter as tk
from src.skywizz.SkyWizz import SkyWizz

def main():
    # Create the Tkinter window
    window = tk.Tk()

    # Initialize the SkyWizz app
    skywizz_app = SkyWizz(window)

    # Run the app
    window.mainloop()

if __name__ == '__main__':
    main()
