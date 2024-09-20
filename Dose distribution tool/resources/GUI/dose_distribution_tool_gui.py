import os
import tkinter as tk
from tkinter import filedialog
from resources.GaussFit.GaussFit import theoricDoseDistribution
from resources.DoseCalculator.DoseReferenceCalculator import calculate_dose_ref
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.figure import Figure


class DoseDistributionTool:
    def __init__(self, root):
        self.centered_x_extended = None
        self.centered_x = None
        self.gaussian_parameters = None
        self.normalized_factor = None
        self.raw_x = None
        self.raw_y = None
        self.fit_y = None
        self.canvas_exist = False

        self.root = root
        self.root.title("Dose Distribution Tool")

        # Title
        title_label = tk.Label(root, text="Dose Distribution Tool", font=("Helvetica", 24))
        title_label.grid(row=0, column=0, columnspan=2)

        # Input parameters
        self.input_frame = tk.Frame(root, height=10)
        self.input_frame.grid(row=1, column=0, pady=20)
        self.input_label = tk.Label(self.input_frame, text='Input parameters', font=("Helvetica", 20), height=2)
        self.input_label.grid(row=0, column=0, columnspan=2)
        self.input_current_label = tk.Label(self.input_frame, text='Beam current [mA]' + ":", width=20)
        self.input_current_label.grid(row=1, column=0, sticky='W')
        self.input_current_entry = tk.Entry(self.input_frame, width=20)
        self.input_current_entry.grid(row=1, column=1)
        self.input_scanx_label = tk.Label(self.input_frame, text='Scan X [mm]' + ":", width=20)
        self.input_scanx_label.grid(row=2, column=0, sticky='W')
        self.input_scanx_entry = tk.Entry(self.input_frame, width=20)
        self.input_scanx_entry.grid(row=2, column=1)
        self.input_time_label = tk.Label(self.input_frame, text='Irradiation time [s]' + ":", width=20)
        self.input_time_label.grid(row=3, column=0, sticky='W')
        self.input_time_entry = tk.Entry(self.input_frame, width=20)
        self.input_time_entry.grid(row=3, column=1)
        self.input_distance_label = tk.Label(self.input_frame, text='Distance [mm]' + ":", width=20)
        self.input_distance_label.grid(row=4, column=0, sticky='W')
        self.input_distance_entry = tk.Entry(self.input_frame, width=20)
        self.input_distance_entry.grid(row=4, column=1)

        # Browse for CSV file
        self.csv_path = tk.StringVar()
        self.data_input_frame = tk.Frame(root, height=10)
        self.data_input_frame.grid(row=1, column=1, padx=20)
        self.data_input_label = tk.Label(self.data_input_frame, text='Data input', font=("Helvetica", 20), height=2)
        self.data_input_label.grid(row=0, column=0, columnspan=2)
        self.browse_label = tk.Label(self.data_input_frame, text="CSV File:")
        self.browse_label.grid(row=1, column=0, sticky='W')
        self.browse_entry = tk.Entry(self.data_input_frame, textvariable=self.csv_path, width=50)
        self.browse_entry.grid(row=2, column=0)
        self.browse_button = tk.Button(self.data_input_frame, text="...", command=self.browse_csv)
        self.browse_button.grid(row=2, column=2)

        # Parameters output fields creation
        self.results_frame = tk.Frame(root, width=60)
        self.results_frame.grid(row=2, column=0, pady=20)
        self.results_label = tk.Label(self.results_frame, text='Results parameters', font=("Helvetica", 20), height=2)
        self.results_label.grid(row=0, column=0, columnspan=2)
        self.amplitude_label = tk.Label(self.results_frame, text='Amplitude' + ":", width=20)
        self.amplitude_label.grid(row=1, column=0, sticky='W')
        self.amplitude_entry = tk.Entry(self.results_frame, width=20)
        self.amplitude_entry.grid(row=1, column=1)
        self.sd_label = tk.Label(self.results_frame, text='Standard deviation [mm]' + ":", width=20)
        self.sd_label.grid(row=2, column=0, sticky='W')
        self.sd_entry = tk.Entry(self.results_frame, width=20)
        self.sd_entry.grid(row=2, column=1)
        self.fitscore_label = tk.Label(self.results_frame, text='Fit score [%]' + ":", width=20)
        self.fitscore_label.grid(row=3, column=0, sticky='W')
        self.fitscore_entry = tk.Entry(self.results_frame, width=20)
        self.fitscore_entry.grid(row=3, column=1)

        # Generate gaussian
        self.generate_frame = tk.Frame(root)
        self.generate_frame.grid(row=3, column=0, padx=100)
        self.generate_button = tk.Button(self.generate_frame, text="Generate gaussian", command=self.generate_gaussian)
        self.generate_button.grid(row=0, column=0)

        # Display dose plot
        self.figure_frame = tk.Frame(root)
        self.figure_frame.grid(row=4, column=0, columnspan=2, pady=20)
        self.gaussian_figure = Figure(figsize=(8, 4), dpi=100)
        self.data = self.gaussian_figure.add_subplot()
        self.data.set_xlabel("y [mm]")
        self.data.set_ylabel("Dose [Gy*m/mA*s]")

        # Recipe parameters
        self.recipe_frame = tk.Frame(root)
        self.recipe_frame.grid(row=2, column=1, pady=20)
        self.recipe_label = tk.Label(self.recipe_frame, text='Recipe parameters', font=("Helvetica", 20), height=2)
        self.recipe_label.grid(row=0, column=0, columnspan=2)
        self.recipe_current_label = tk.Label(self.recipe_frame, text='Beam current [mA]' + ":", width=20)
        self.recipe_current_label.grid(row=1, column=0, sticky='W')
        self.recipe_current_entry = tk.Entry(self.recipe_frame, width=20)
        self.recipe_current_entry.grid(row=1, column=1)
        self.recipe_scanx_label = tk.Label(self.recipe_frame, text='Scan X [mm]' + ":", width=20)
        self.recipe_scanx_label.grid(row=2, column=0, sticky='W')
        self.recipe_scanx_entry = tk.Entry(self.recipe_frame, width=20)
        self.recipe_scanx_entry.grid(row=2, column=1)
        self.recipe_speed_label = tk.Label(self.recipe_frame, text='Speed [m/min]' + ":", width=20)
        self.recipe_speed_label.grid(row=3, column=0, sticky='W')
        self.recipe_speed_entry = tk.Entry(self.recipe_frame, width=20)
        self.recipe_speed_entry.grid(row=3, column=1)
        self.recipe_sample_time_label = tk.Label(self.recipe_frame, text='Sample time [ms]' + ":", width=20)
        self.recipe_sample_time_label.grid(row=4, column=0, sticky='W')
        self.recipe_sample_time_entry = tk.Entry(self.recipe_frame, width=20)
        self.recipe_sample_time_entry.grid(row=4, column=1)

       # Integrated dose calculator
        self.integrated_dose_frame = tk.Frame(root)
        self.integrated_dose_frame.grid(row=3, column=1, padx=10)
        self.integrated_dose_button = tk.Button(self.integrated_dose_frame, text="Integrate dose", command=self.integrate_dose)
        self.integrated_dose_button.grid(row=0, column=0)
        self.integrated_dose_label = tk.Label(self.integrated_dose_frame, text="Integrated dose reference:")
        self.integrated_dose_label.grid(row=1, column=0, sticky='W')
        self.integrated_dose_entry = tk.Entry(self.integrated_dose_frame, width=50)
        self.integrated_dose_entry.grid(row=2, column=0)


        # For test
        self.input_current_entry.insert(0, '15')
        self.input_scanx_entry.insert(0, '700')
        self.input_time_entry.insert(0, '1800')
        self.input_distance_entry.insert(0, '1000')
        if os.name == 'posix':
            self.browse_entry.insert(0, '/Users/lindorf/Library/CloudStorage/OneDrive-IBAGroup/Product/1. '
                                    'Integration/2. R&D/MCS X-Ray/Data/SAJ.144/SAJ.144 data 1m - I 15 mA - SX 70 cm - '
                                    'Time 30 min.csv')
        elif os.name == 'nt':
            self.browse_entry.insert(0, 'C:/Users/AGHSM/OneDrive - IBA Group/Product/1. Integration/2. R&D'
                                        '/MCS X-Ray/Data/SAJ.144/SAJ.144 data 1m - I 15 mA - SX 70 cm - Time 30 min.csv')
        self.recipe_current_entry.insert(0, '2')
        self.recipe_scanx_entry.insert(0, '930')
        self.recipe_sample_time_entry.insert(0, '5')
        self.recipe_speed_entry.insert(0, '0.9')

    def browse_csv(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            self.csv_path.set(file_path)

    def generate_gaussian(self):
        self.normalized_factor = 1000 * (int(self.input_scanx_entry.get()) / 1000) / (float(self.input_current_entry.get())
                                                                                * int(self.input_time_entry.get()))
        self.gaussian_parameters, self.centered_x, self.centered_x_extended, self.raw_y, self.fit_y = theoricDoseDistribution(self)
        self.amplitude_entry.delete(0, tk.END)
        self.sd_entry.delete(0, tk.END)
        self.fitscore_entry.delete(0, tk.END)
        self.amplitude_entry.insert(0, round(self.gaussian_parameters[0], 3))
        self.sd_entry.insert(0, str(int(round(self.gaussian_parameters[2], 0))))
        self.fitscore_entry.insert(0, round(self.gaussian_parameters[3], 2))
        self.generate_figure()

    def generate_figure(self):
        self.canvas = FigureCanvasTkAgg(self.gaussian_figure, master=self.figure_frame)  # A tk.DrawingArea.
        NavigationToolbar2Tk(self.canvas, self.figure_frame, pack_toolbar=False)
        self.canvas.get_tk_widget().grid(row=0, column=0)
        self.data_fit = self.data.plot(self.centered_x_extended, self.fit_y)
        self.data_raw = self.data.plot(self.centered_x, self.raw_y)
        self.canvas.draw()

    def get_amplitude(self):
        return self.amplitude_entry.get()

    def get_beam_current(self):
        return self.recipe_current_entry.get()

    def get_sigma(self):
        return self.sd_entry.get()

    def get_speed(self):
        return self.recipe_speed_entry.get()

    def get_scanx(self):
        return self.recipe_scanx_entry.get()

    def get_sampling_time(self):
        return self.recipe_sample_time_entry.get()

    def integrate_dose(self):
        self.integrated_dose_entry.delete(0, tk.END)
        self.integrated_dose_entry.insert(0, calculate_dose_ref(self))

if __name__ == "__main__":
    root = tk.Tk()
    app = DoseDistributionTool(root)
    root.mainloop()
