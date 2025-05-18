import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

do_download = False
do_save = False

if do_download:
    # Download WLTP data
    fn = "https://unece.org/fileadmin/DAM/trans/doc/2012/wp29grpe/WLTP-DHC-12-07e.xls"
    os.system(f"wget {fn} -O wltp.xls")

# Read the data
df = pd.read_excel("wltp.xls", sheet_name="WLTC_class_3", skiprows=5)


def extract(col):
    unit = df.iloc[0, col]
    data = df.iloc[1:, col].values
    return data, unit


# Extract the data
phase, _ = extract(1)
time, time_unit = extract(2)
phase_time, phase_time_unit = extract(3)
speed, speed_unit = extract(4)
acc, acc_unit = extract(5)

assert time_unit == phase_time_unit == "s"
assert speed_unit == "km/h"
assert acc_unit == "m/s²"

# Physical constants
g = 9.81  # gravity (m/s²)
rho = 1.225  # air density (kg/m³)
kilo = 1000
hour = 3600

speed *= kilo / hour  # Convert to m/s

# Vehicle parameters
m = 1600  # mass (kg)
A_f = 2.2  # frontal area (m²)
C_d = 0.28  # drag coefficient
C_r = 0.01  # rolling resistance coefficient
eta = 0.90  # drivetrain efficiency

# Compute forces and power
F_aero = 0.5 * rho * C_d * A_f * speed**2
F_roll = m * g * C_r
F_inertia = m * acc
F_total = F_aero + F_roll + F_inertia

# Power
P_raw = F_total * speed
P_motor = P_raw / eta

# Plot power vs t
plt.figure(figsize=(10, 5))

# Plot phases
phases, idx = np.unique(phase, return_index=True)
phases = phases[np.argsort(idx)]

for p in phases:
    mask = phase == p
    plt.plot(time[mask], P_motor[mask] / kilo, label=p)

plt.title("Electric Motor Power Over Time")
plt.xlabel("Time / s")
plt.ylabel("Power / kW")
plt.grid(True)
plt.legend()
plt.tight_layout()

plt.show()

if do_save:
    # Export time and power to CSV
    df = pd.DataFrame({"Time / s": time, "Power / W": P_motor})
    df.to_csv("wltp.csv", index=False)
