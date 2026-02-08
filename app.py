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
def draw():
    fig, ax = plt.subplots(figsize=(fig_size_x, fig_size_y))
    ax.set_xlim(-fig_size_x * scale, fig_size_x * scale)
    ax.set_ylim(-fig_size_y * scale, fig_size_y * scale)
    ax.grid(True)

    pitch = st.session_state.pitch
    drone_pos_x = st.session_state.drone_pos_x

    cos_pitch = math.cos(math.radians(pitch))
    sin_pitch = math.sin(math.radians(pitch))

    target = Circle((target_pos_x, target_pos_y), target_point_radius, fc='red')
    drone = Rectangle(
        (
            drone_pos_x - cos_pitch * drone_width / 2 - sin_pitch * drone_heigh / 2,
            sin_pitch * drone_width / 2 - cos_pitch * drone_heigh / 2
        ),
        drone_width,
        drone_heigh,
        angle=-pitch,
        fc='blue'
    )

    prop = Rectangle(
        (
            drone_pos_x - cos_pitch * prop_length / 2 + sin_pitch * (drone_heigh / 2 + 10),
            sin_pitch * prop_length / 2 + cos_pitch * (drone_heigh / 2 + 10)
        ),
        prop_length,
        prop_thickness,
        angle=-pitch,
        fc='black'
    )

    flap = Arrow(
        drone_pos_x - sin_pitch * drone_heigh / 2,
        -cos_pitch * drone_heigh / 2,
        -sin_pitch * flap_length,
        -cos_pitch * flap_length,
        width=flap_thickness
    )

    ax.add_patch(target)
    ax.add_patch(drone)
    ax.add_patch(prop)
    ax.add_patch(flap)

    st.pyplot(fig)

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
    for _ in range(50):  # runs a short burst each refresh
        update(0.05)

# Draw frame
with placeholder:
    draw()

# Auto refresh when running
if st.session_state.running:
    time.sleep(0.05)
    st.rerun()
