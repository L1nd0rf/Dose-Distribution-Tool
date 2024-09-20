import numpy as np

def calculate_dose_ref(gui):
    amplitude = float(gui.get_amplitude())
    sigma = int(gui.get_sigma())
    speed = float(gui.get_speed()) / 60
    scan_x = int(gui.get_scanx())
    dt = int(gui.get_sampling_time())
    beam_current = float(gui.get_beam_current())

    dy = speed * dt
    n = int(6 * sigma / dy)
    gc = amplitude*beam_current/scan_x
    j = np.array(range(n))
    gaussian_exp_arg = (-0.5 * ((-3 * sigma + j * dy) / sigma) ** 2)
    dose = gc * np.exp(gaussian_exp_arg) * (dt / 1000)

    return np.sum(dose)