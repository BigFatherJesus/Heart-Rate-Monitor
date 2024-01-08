# Heart Rate Monitor

This is a Python application that detects heart rate from a PPG signal. It was created as the final assignment for the Programming Skills Experience course.

## Dependencies

The application uses the following Python libraries:

- tkinter
- tkinter.messagebox
- customtkinter
- filedialog
- matplotlib.backends.backend_tkagg
- matplotlib.figure
- scipy.signal
- pyfirmata2
- serial
- time
- matplotlib.pyplot
- threading

## Features

The application has a GUI that allows users to:

- Open a file containing PPG signal data
- Display the heart rate calculated from the PPG signal
- Show a graph of the PPG signal
- Export the graph to a PNG image

## Usage

To run the application, simply execute the `Start.bat` script.

## Future Work

The application is currently a work in progress. Future updates will include:

- Reading data from a serial port for Real-Time PPG data
- Implementing delays in the program for better performance and to make the Real-Time data function work
- Running multiple threads at once for better performance

## Author

This application was created by Nuallan Lampe.