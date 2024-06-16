import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation

def differential_drive_simulation(left_speed, left_radius, right_speed, right_radius, body_radius, initial_x, initial_y, initial_orientation):
    # Konversi sudut ke radian
    initial_orientation_rad = np.radians(initial_orientation)

    # Inisialisasi posisi dan orientasi
    x = initial_x
    y = initial_y
    theta = initial_orientation_rad

    # Inisialisasi list posisi x dan y untuk plotting jalur
    x_plot = [x]
    y_plot = [y]

    # Waktu simulasi
    total_time = 10  # Misalnya, simulasi berjalan selama 10 detik
    dt = 0.1  # Interval waktu
    times = np.arange(0, total_time, dt)

    # Plotting
    fig, ax = plt.subplots()
    ax.set_aspect('equal', 'datalim')

    # Fungsi untuk mengupdate posisi dan orientasi robot
    def update(frame):
        nonlocal x, y, theta

        # Hitung kecepatan translasi (linear) masing-masing roda
        v_left = left_speed * left_radius
        v_right = right_speed * right_radius

        # Hitung kecepatan translasi (linear) total dan kecepatan rotasi (angular) robot
        v = (v_left + v_right) / 2
        omega = (v_right - v_left) / body_radius

        # Hitung perubahan posisi dan orientasi
        dx = v * np.cos(theta) * dt
        dy = v * np.sin(theta) * dt
        dtheta = omega * dt

        # Perbarui posisi dan orientasi
        x += dx
        y += dy
        theta += dtheta

        # Simpan posisi untuk plotting jalur
        x_plot.append(x)
        y_plot.append(y)

        # Memplot posisi robot dan jalur yang diikuti
        ax.clear()
        ax.set_aspect('equal', 'datalim')
        ax.plot(x_plot, y_plot, 'b-')
        ax.plot(x, y, 'bo')
        ax.set_xlim(-10, 10)
        ax.set_ylim(-10, 10)

    # Animasi
    anim = FuncAnimation(fig, update, frames=times, repeat=False, blit=False)
    return fig, anim

def start_simulation():
    try:
        left_speed = float(left_speed_entry.get())
        left_radius = float(left_radius_entry.get())
        right_speed = float(right_speed_entry.get())
        right_radius = float(right_radius_entry.get())
        body_radius = float(body_radius_entry.get())
        initial_x = float(initial_x_entry.get())
        initial_y = float(initial_y_entry.get())
        initial_orientation = float(initial_orientation_entry.get())

        fig, anim = differential_drive_simulation(left_speed, left_radius, right_speed, right_radius, body_radius, initial_x, initial_y, initial_orientation)
        canvas = FigureCanvasTkAgg(fig, master=window)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.grid(row=10, column=0, columnspan=2)  # Ubah baris menjadi 10

        # Simpan objek animasi dalam variabel global
        global anim_global
        anim_global = anim

        # Memastikan animasi tetap ada hingga plt.show() dipanggil
        anim._start()

    except ValueError:
        messagebox.showerror("Error", "Input harus berupa angka")

# Membuat GUI
window = tk.Tk()
window.title("Simulasi Gerakan Mobile Robot Differential Drive")

# Membuat label dan entry untuk setiap parameter
tk.Label(window, text="Kecepatan Roda Kiri:").grid(row=0, column=0)
left_speed_entry = tk.Entry(window)
left_speed_entry.grid(row=0, column=1)

tk.Label(window, text="Radius Roda Kiri:").grid(row=1, column=0)
left_radius_entry = tk.Entry(window)
left_radius_entry.grid(row=1, column=1)

tk.Label(window, text="Kecepatan Roda Kanan:").grid(row=2, column=0)
right_speed_entry = tk.Entry(window)
right_speed_entry.grid(row=2, column=1)

tk.Label(window, text="Radius Roda Kanan:").grid(row=3, column=0)
right_radius_entry = tk.Entry(window)
right_radius_entry.grid(row=3, column=1)

tk.Label(window, text="Radius Body:").grid(row=4, column=0)
body_radius_entry = tk.Entry(window)
body_radius_entry.grid(row=4, column=1)

tk.Label(window, text="Posisi X Awal:").grid(row=5, column=0)
initial_x_entry = tk.Entry(window)
initial_x_entry.grid(row=5, column=1)

tk.Label(window, text="Posisi Y Awal:").grid(row=6, column=0)
initial_y_entry = tk.Entry(window)
initial_y_entry.grid(row=6, column=1)

tk.Label(window, text="Orientasi Awal (derajat):").grid(row=7, column=0)
initial_orientation_entry = tk.Entry(window)
initial_orientation_entry.grid(row=7, column=1)

# Tombol untuk memulai simulasi
start_button = tk.Button(window, text="Mulai Simulasi", command=start_simulation)
start_button.grid(row=8, column=0, columnspan=2)

window.mainloop()
