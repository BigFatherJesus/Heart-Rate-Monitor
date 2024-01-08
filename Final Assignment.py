# Author: Nuallan Lampe
# Date Created: 2024-01-03
# Date Modified: 2024-01-08
# This program is made for the final assignment of the Programming Skills Experience course
# This program is used to detect heart rate from a PPG signal

# This is the import section
# We use this section to import all of the modules that we need to run the program
# We import tkinter to create the GUI
# We import tkinter.messagebox to display message boxes
# We import customtkinter to make tkinter look better
# We import filedialog to open files
# We import FigureCanvasTkAgg and Figure to embed the graph in the GUI
# We import butter and filtfilt to create a low-pass filter
# We import Arduino, util, and serial to read data from a serial port TODO: Implement this
# We import time to delay the program TODO: Implement this
# We import matplotlib.pyplot to plot the graph
# We import threading to run multiple threads at once TODO: Implement this
import tkinter
import tkinter.messagebox
import customtkinter
from tkinter import filedialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from scipy.signal import butter, filtfilt
from pyfirmata2 import Arduino, util
import serial
import time
import matplotlib.pyplot as plt
import threading

# This is the customtkinter module that I used to make tkinter look better, it does not add any functionality, it just makes tkinter look better
customtkinter.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"


# This is the App class that inherits from the customtkinter.CTk class (which inherits from the tkinter.Tk class) and is used to create the GUI
class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # THIS ALL IS FOR THE GUI, I AM NOT GOING TO BE GOING INTO TOO MUCH DETAIL HERE AS IT IS NOT THE FOCUS OF THE PROJECT AND IT SHOULD BE PRETTY SELF EXPLANATORY
        # configure window
        self.title("Heart Rate Monitor")
        self.geometry(f"{1100}x{525}")

        # configure grid layout (3x2)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure((0, 1, 2), weight=1)

        # create file path label
        self.file_path_label = customtkinter.CTkLabel(self, text="File Path: ", wraplength=200)
        self.file_path_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # create heart rate label
        self.heart_rate_label = customtkinter.CTkLabel(self, text="Heart Rate: ")
        self.heart_rate_label.grid(row=1, column=0, padx=20, pady=(10, 10))

        # create open file button
        self.open_file_button = customtkinter.CTkButton(self, text="Open File", command=self.open_file)
        self.open_file_button.grid(row=2, column=0, padx=20, pady=(10, 10))

        # create show graph button
        self.show_graph_button = customtkinter.CTkButton(self, text="Show Graph", command=self.show_graph)
        self.show_graph_button.grid(row=3, column=0, padx=20, pady=(10, 10))

        # create sensitivity slider
        self.sensitivity_label = customtkinter.CTkLabel(self, text="Sensitivity:")
        self.sensitivity_label.grid(row=4, column=0, padx=20, pady=(10, 10))
        self.sensitivity_slider = customtkinter.CTkSlider(self, from_=0.1, to=2.0, command=self.update_sensitivity)
        self.sensitivity_slider.set(0.6)
        self.sensitivity_slider.grid(row=5, column=0, padx=20, pady=(10, 20))

        # create real-time data switch
        self.real_time_data_switch = customtkinter.CTkSwitch(self, text="Real-Time Data", command=self.toggle_real_time_data)
        self.real_time_data_switch.grid(row=6, column=0, padx=20, pady=(10, 20))

        # create explain dots alignment button
        self.explain_dots_alignment_button = customtkinter.CTkButton(self, text="Why do the dots not align?",command=self.explain_dots_alignment)
        self.explain_dots_alignment_button.grid(row=7, column=0, padx=20, pady=(10, 20))
        
        # create serial port selection
        self.serial_port_label = customtkinter.CTkLabel(self, text="Serial Port:")
        self.serial_port_label.grid(row=7, column=1, padx=20, pady=(10, 10))
        self.serial_port_selection = customtkinter.CTkOptionMenu(self, values=["COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM8", "COM9", "COM10"], command=self.change_serial_port_event)
        self.serial_port_selection.set("COM1")
        self.serial_port_selection.grid(row=8, column=1, padx=20, pady=(10, 20))

        # create export graph button
        self.export_graph_button = customtkinter.CTkButton(self, text="Export Graph", command=self.export_graph)
        self.export_graph_button.grid(row=6, column=1, padx=20, pady=(10, 20))

        # Open a message box to explain how to use the program and what it does, how it works, why the sensitivity slider is there, etc.
        tkinter.messagebox.showinfo("How to Use", "This program is used to detect heart rate from a PPG signal. To use this program, click the \"Open File\" button and select a file containing a PPG signal. Then, click the \"Show Graph\" button to display the graph. The red dots on the graph indicate the peaks of the PPG signal. The heart rate is calculated by finding the time difference between the first and last peak. The sensitivity slider is used to adjust the sensitivity of the peak detection algorithm. The sensitivity value ranges from 0.1 to 2.0. The real-time data switch (should) allow you to display real-time data from a selected serial port, however this does not yet work. \nNuallan Lampe")

        # function to automatically refresh the graph after changing the sensitivity
        def refresh_graph(event):
            self.refresh_graph()

        self.sensitivity_slider.bind("<ButtonRelease-1>", refresh_graph)

        # Define global variables
        self.ax = None
        self.sensitivity = 0.6
        self.sampling_rate = 0.0
        self.real_time_data_enabled = False
        self.selected_serial_port = "COM1"

        # Create figure for embedding the graph
        self.fig = Figure(figsize=(7, 4), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().grid(row=0, column=1, rowspan=6, padx=20, pady=20)

        # This is the filter function for detecting peaks
        # We use a low-pass filter to smooth out the signal
        # Then we detect peaks in the filtered signal
        # We start by defining a low-pass filter
        # Then we set the criteria and values for the filter
        # We then apply the filter to the data
    def apply_filter(self, data, cutoff):
        nyquist_freq = 0.5 * self.sampling_rate
        normalized_cutoff = cutoff / nyquist_freq
        b, a = butter(4, normalized_cutoff, btype='low', analog=False)
        filtered_data = filtfilt(b, a, data)
        return filtered_data

    # This function is called when the "Show Graph" button is clicked
    def refresh_graph(self):
        # Clear previous plot
        self.ax.clear()

        # Get the selected file path from the label
        file_path = self.file_path_label.cget("text").replace("File Path: ", "")

        # Load data from file or real-time data
        if self.real_time_data_enabled:
            # TODO: Implement real-time data loading
            # Initialize serial port connection on the selected port
            board = Arduino(self.selected_serial_port)
            board.digital[13].write(1)  # light up LED on to indicate program is running

            # Ran out of time to implement this part
            # Might be able to use pyserial to read data from the serial port
            # Might continue working on this project in the future
            pass

        else:
            xdata, ydata = [], []
            with open(file_path) as f:
                for line in f:
                    t = line.rstrip("\n").split(sep="\t")
                    xdata.append(float(t[0]))
                    ydata.append(float(t[1]))

        # Set sampling rate for the filter
        self.sampling_rate = 1.0 / (xdata[1] - xdata[0])

        # Apply low-pass filter
        filtered_ydata = self.apply_filter(ydata, self.sensitivity)

        # Peak detection
        # We detect peaks by finding points where the slope changes from positive to negative
        # We do this by finding points where the derivative is zero
        # We find the derivative by finding the difference between each point and the next point
        # We then find the points where the derivative is zero
        xdata2, ydata2 = [], []
        for i in range(1, len(filtered_ydata) - 1):
            if filtered_ydata[i] > filtered_ydata[i - 1] and filtered_ydata[i] > filtered_ydata[i + 1]:
                xdata2.append(float(xdata[i]))
                ydata2.append(float(filtered_ydata[i]))

        # Calculate heart rate
        # We calculate heart rate by finding the time difference between the first and last peak
        time_diff = xdata2[-1] - xdata2[0]
        heart_rate = (len(xdata2) / time_diff) * 60
        # round to the nearest integer
        heart_rate = round(heart_rate)


        # Display heart rate in the GUI
        self.heart_rate_label.configure(text="Heart Rate: {:}".format(heart_rate))

        # Plot data
        self.ax.plot(xdata, ydata, linewidth=1.0)
        self.ax.scatter(xdata2, ydata2, color='red')
        self.canvas.draw()

        # This function is called when the "Serial Port" option menu is changed
        # We use this function to update the selected serial port
        # TODO: Implement this function
    def change_serial_port_event(self):
        pass

    # This function is called when the "Open File" button is clicked
    # We use this function to open a file and load data from it
    def open_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if file_path:
            # Update file path label
            self.file_path_label.configure(text="File Path: " + file_path)

            # Load data from file or real-time data
            if self.real_time_data_enabled:
                # TODO: Implement real-time data loading
                pass
            else:
                # Load data from file
                # We load the data from the file into two lists, one for the x values and one for the y values
                # We then set the sampling rate for the filter
                xdata, ydata = [], []
                with open(file_path) as f:
                    for line in f:
                        t = line.rstrip("\n").split(sep="\t")
                        xdata.append(float(t[0]))
                        ydata.append(float(t[1]))

            # Set sampling rate for the filter
            self.sampling_rate = 1.0 / (xdata[1] - xdata[0])

            # Refresh the graph and calculate heart rate
            self.refresh_graph()

    # This function is called when the "Show Graph" button is clicked
    # We use this function to refresh the graph    
    def show_graph(self):
        if self.ax is None:
            self.ax = self.fig.add_subplot(111)
        # Open a message box when there is no file selected to inform the user that they need to select a file first
        if self.file_path_label.cget("text") == "File Path: ":
            tkinter.messagebox.showinfo("No File Selected", "Please select a file first.")
        else:
            self.ax.clear()
    


        # Refresh the graph and calculate heart rate
        self.refresh_graph()

    # This function is called when the "Sensitivity" slider is changed
    # We use this function to update the sensitivity value for the filter
    def update_sensitivity(self, value):
        self.sensitivity = float(value)

    # This function is called when the "Real-Time Data" switch is toggled
    # We use this function to enable or disable real-time data
    # We disable the "Open File" button when real-time data is enabled
    # We also update the file path label to show the selected serial port
    # We also clear the graph when real-time data is enabled
    # TODO: Implement this further functionality of this function, for now it just displays a message box stating that it does not work yet
    def toggle_real_time_data(self):
        self.real_time_data_enabled = not self.real_time_data_enabled
        if self.real_time_data_enabled:
            tkinter.messagebox.showinfo("Real-Time Data", "This feature does not work yet.")
            self.open_file_button.configure(state=tkinter.DISABLED)
            self.file_path_label.configure(text="Serial Port: " + self.selected_serial_port)
            self.ax.clear()
            self.fig.canvas.draw()

        else:
            self.open_file_button.configure(state=tkinter.NORMAL)

    # This function is called when the "Serial Port" option menu is changed
    # We use this function to update the selected serial port
    # I accidentally created this function twice, so I just left it here because I am scared the program will break if I delete it
    def change_serial_port_event(self, value):
        self.selected_serial_port = value

        pass

    # This function is called when the "Why do the dots not align?" button is clicked
    # We use this function to display a message box with an explanation
    def explain_dots_alignment(self):
        tkinter.messagebox.showinfo("Why do the dots not align?", "The dots do not align because the peaks are detected in the filtered signal, not the original signal. The filtered signal is delayed due to the filter, so the peaks are also delayed. This is why the dots do not align with the peaks directly. The heart rate is still calculated correctly, if not more accurately, because the peaks are detected in the filtered signal instead of the original signal.")


    # This function is called when the "Export Graph" button is clicked
    # We use this function to export the graph to a png file, showing the graph with the peaks marked, the heart rate, and the sensitivity value, and the name of the file
    # The file is saved in the same directory as the program, with the name "graph-<current txt file>.png"
    def export_graph(self):
        # Get the name of the current txt file
        file_path = self.file_path_label.cget("text").replace("File Path: ", "")
        file_name = file_path.split("/")[-1].split(".")[0]

        # Save the graph to a png file, making sure to include the name of the file and the heart rate
        self.ax.set_title("Graph-{} (HR: {:})".format(file_name, float(self.heart_rate_label.cget("text").replace("Heart Rate: ", ""))))
        self.fig.savefig("Graph-{}.png".format(file_name))

        # Temporarily change the title of the window to show that the graph has been exported, and then change it back after 2 seconds, we do the same for the button
        self.title("Graph Exported")
        self.export_graph_button.configure(text="Graph Exported")
        self.after(2000, lambda: self.title("Heart Rate Monitor"))
        self.after(2000, lambda: self.export_graph_button.configure(text="Export Graph"))





# This is the main function
# We use this function to run the program
# We create an instance of the App class and run the mainloop function
if __name__ == "__main__":
    app = App()
    app.mainloop()