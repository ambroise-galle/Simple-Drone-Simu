import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, Arrow
import math
import time

# -------------------------
# Session state init
# -------------------------
if "initialized" not in st.session_state:
    st.session_state.initialized = True
    st.session_state.drone_pos_x = 0.0
    st.session_state.drone_speed_x = 0.0
    st.session_state.drone_acc_x = 0.0
    st.session_state.pitch = 10.0
    st.session_state.pitch_rate = 0.0
    st.session_state.wind_force = 0.0
    st.session_state.running = False

# -------------------------
# Physics params
# -------------------------
mass = 2.2
thrust = 22.0
pitch_inertia = 1.0 / 12.0 * mass * 0.4 * 0.4
flap_angle = 0.0

# Drawing params
fig_size_x = 12
fig_size_y = 6
scale = 30

drone_heigh = 90
drone_width = 20
prop_length = 50
prop_thickness = 2
flap_length = 35
flap_thickness = 20
target_point_radius = 2

target_pos_x = 0
target_pos_y = 0

import matplotlib.pyplot as plt
from IPython.display import display, clear_output
import ipywidgets as widgets
from matplotlib.patches import *
from matplotlib.text import *
import threading
import time
from IPython.display import display
import asyncio
import math


# Parametres graphique
fig_size_x = 12
fig_size_y = 6
scale = 30

drone_heigh = 90
drone_width = 20
prop_length = 50
prop_thickness = 2
flap_length = 35
flap_thickness = 20
target_point_radius = 2

# Plot
fig, ax = plt.subplots(figsize=(fig_size_x, fig_size_y))
ax.set_xlim(-fig_size_x * scale, fig_size_x * scale)
ax.set_ylim(-fig_size_y * scale, fig_size_y * scale)

# Formes desinées
target = Circle((0, 0), target_point_radius, fc='red')
drone = Rectangle((0, 0), drone_width, drone_heigh, fc='blue')
prop = Rectangle((0, 0), prop_length, prop_thickness, fc='black')
flap = Arrow(0, 0, 0, -flap_length,width=flap_thickness , fc='black')

texte = Text((100,100),"Heelo", color='black')

# Ajout des formes au graphique
ax.add_patch(target)
ax.add_patch(drone)
ax.add_patch(prop)
ax.add_patch(flap)

#
plt.title("Moving Square with ipywidgets")
plt.grid(True)
plt.close(fig)

# Output widget to update the plot
plot_output = widgets.Output()

# Affiche le plot dans le widget
with plot_output:
    display(fig)



# -------------------------
# Physics update
# -------------------------
def update(dt):
    flap_cl = flap_angle / 20.0
    flap_force = flap_cl * 10 * 10 * 0.6 * 0.14 * 1.225

    torque = -flap_force * 0.2

    st.session_state.pitch_rate += dt * torque / pitch_inertia / (2 * math.pi) * 360
    st.session_state.pitch += dt * st.session_state.pitch_rate

    x_force = math.sin(math.radians(st.session_state.pitch)) * thrust

    st.session_state.drone_acc_x = (x_force + st.session_state.wind_force) / mass
    st.session_state.drone_speed_x += dt * st.session_state.drone_acc_x
    st.session_state.drone_pos_x += st.session_state.drone_speed_x * dt

# -------------------------
# Drawing
# -------------------------

# Dessine les éléments
def draw(target,drone,prop,flap,target_pos_x,target_pos_y,drone_pos_x,pitch,flap_length):

  cos_pitch = math.cos(pitch / 360 * 2 * math.pi)
  sin_pitch = math.sin(pitch / 360 * 2 * math.pi)

  # Dessine la cible
  target.center = (target_pos_x, target_pos_y)

  # Dessine le drone
  drone.set_xy((drone_pos_x - cos_pitch*drone.get_width()/2 - sin_pitch*drone.get_height()/2, sin_pitch*drone.get_width()/2 - cos_pitch*drone.get_height()/2))
  drone.set_angle(-pitch) # CCW fonction mais CW angle

  # Dessine les hélices
  prop.set_xy((drone_pos_x - cos_pitch*prop.get_width()/2 + sin_pitch*(drone.get_height()/2 + 10), sin_pitch*prop.get_width()/2 + cos_pitch*(drone.get_height()/2 + 10)))
  prop.set_angle(-pitch)

  # Dessine les flaps
  flap.set_data(drone_pos_x -sin_pitch*drone.get_height()/2, -cos_pitch*drone.get_height()/2, -sin_pitch*flap_length, -cos_pitch*flap_length)



  with plot_output:
        clear_output(wait=True)
        display(fig)

# Boutons
button_wind_add = widgets.Button(description="Wind +")
button_next_step = widgets.Button(description="Next step")
button_wind_sub = widgets.Button(description="Wind -")
button_stop = widgets.Button(description="Stop")
button_start = widgets.Button(description="Start Simulation") # New Start button

#Calcul le prochain échantillon de la simulation
def update(dt):
  print("Update : " + str(dt))
  global pitch, pitch_rate
  global drone_pos_x, drone_speed_x, drone_acc_x

  # Force génerée par les flaps
  flap_cl = flap_angle / 20.0  #lift
  flap_force = flap_cl * 10 * 10 * 0.6 * 0.14 * 1.225 # 60cmx14cm flap area

  torque = -flap_force * 0.2
  pitch_rate += dt * torque / pitch_inertia / (2 * 3.14) * 360 # En degrés
  pitch += dt * pitch_rate 

  # Composante horizontal de la force
  x_force = math.sin(math.radians(pitch)) * thrust

  # Repercution sur la position du drone
  drone_acc_x = (x_force + wind_force) / mass
  drone_speed_x += dt * drone_acc_x
  drone_pos_x += drone_speed_x * dt

# Ajoute du vent
def on_add_wind(b):
    global wind_force
    wind_force += 1

# Retire du vent
def on_sub_wind(b):
    global wind_force
    wind_force -= 1

# Avance la simulation (single step)
def on_next_step(b):
    update(1) # Use the correct dt if needed, but the original used 1 here.
    draw(target,drone,prop,flap,target_pos_x,target_pos_y,drone_pos_x,pitch,flap_length)

# Start the continuous simulation
def on_start_click(b):
    global simu_running
    if not simu_running:
        simu_running = True
        # Reset values for a fresh start if desired, or continue from current state
        drone_pos_x = 0
        pitch = 10
        sim_thread = threading.Thread(target=start_simulation)
        sim_thread.start()

# Stop the simulation
def on_stop(b):
    global simu_running
    simu_running = False

# Main simulation loop function to run in a thread
def start_simulation():
    global simu_running
    while simu_running:
        update(0.1)
        draw(target,drone,prop,flap,target_pos_x,target_pos_y,drone_pos_x,pitch,flap_length)
        time.sleep(0.1) # Adjust sleep time for visual speed, original used 1s for dt=1
                                # Using dt * 100 means 0.5s sleep if dt = 1/200

# Events des boutons
button_wind_add.on_click(on_add_wind)
button_wind_sub.on_click(on_sub_wind)
button_next_step.on_click(on_next_step)
button_stop.on_click(on_stop)
button_start.on_click(on_start_click) # Attach new button event

controls = widgets.VBox([
    widgets.HBox([button_wind_sub, button_next_step, button_wind_add]),
    widgets.HBox([button_start, button_stop]) # Include Start and Stop buttons
])

# Paramètres physique
mass = 2.2
thrust = 22.0
pitch_inertia = 1.0 / 12.0 * mass * 0.4 * 0.4

# Variables
target_pos_x = 0
target_pos_y = 0

drone_pos_x = 0
drone_speed_x = 0
drone_acc_x = 0
pitch = 10         #En degrés
pitch_rate = 0
flap_angle = 0

wind_force = 0
simu_running = False # Initialize simu_running to False

# Display both the plot and the control buttons below it
display(widgets.VBox([plot_output, controls]))

# Initial draw, but don't start the loop automatically
update(0.1)
draw(target,drone,prop,flap,target_pos_x,target_pos_y,drone_pos_x,pitch,flap_length)

# -------------------------
# UI
# -------------------------
st.title("Drone Pitch Simulation")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Wind -"):
        st.session_state.wind_force -= 1

with col2:
    if st.button("Start"):
        st.session_state.running = True

    if st.button("Stop"):
        st.session_state.running = False

with col3:
    if st.button("Wind +"):
        st.session_state.wind_force += 1

st.write("Wind force:", st.session_state.wind_force)
st.write("Pitch:", round(st.session_state.pitch, 2))
st.write("Position X:", round(st.session_state.drone_pos_x, 2))

# -------------------------
# Simulation loop
# -------------------------
placeholder = st.empty()

if st.session_state.running:
        update(0.05)

# Draw frame
with placeholder:
    draw(target,drone,prop,flap,target_pos_x,target_pos_y,drone_pos_x,pitch,flap_length)

# Auto refresh when running
if st.session_state.running:
    time.sleep(0.05)
    st.rerun()
