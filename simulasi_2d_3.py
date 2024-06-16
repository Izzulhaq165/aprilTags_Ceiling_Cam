import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation

# Variabel global untuk menyimpan objek animasi dan widget canvas
anim_global = None
canvas_widget = None

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
    ax.set_aspect('equal', adjustable='datalim')
    ax.invert_yaxis()  # Balik sumbu y agar sesuai dengan koordinat umum

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
        ax.plot(x_plot, y_plot, 'b-')
        ax.plot(x, y, 'bo')
        ax.set_xlim(min(x_plot) - 1, max(x_plot) + 1)
        ax.set_ylim(min(y_plot) - 1, max(y_plot) + 1)

    # Animasi
    anim = FuncAnimation(fig, update, frames=times, repeat=False, blit=False)
    return fig, anim

def start_simulation():
    global anim_global
    if anim_global is not None:
        messagebox.showinfo("Info", "Simulasi sudah berjalan.")
        return

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
        global canvas_widget
        canvas = FigureCanvasTkAgg(fig, master=window)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.grid(row=12, column=0, columnspan=2)  # Ubah baris menjadi 12

        # Simpan objek animasi dalam variabel global
        anim_global = anim

        # Memastikan animasi tetap ada hingga plt.show() dipanggil
        anim._start()

    except ValueError:
        messagebox.showerror("Error", "Input harus berupa angka")

def reset_simulation():
    global anim_global, canvas_widget
    if anim_global is None:
        messagebox.showinfo("Info", "Tidak ada simulasi yang berjalan.")
        return

    anim_global.event_source.stop()
    anim_global = None

    plt.close('all')
    canvas_widget.destroy()

    # Reset nilai input
    left_speed_entry.delete(0, tk.END)
    left_radius_entry.delete(0, tk.END)
    right_speed_entry.delete(0, tk.END)
    right_radius_entry.delete(0, tk.END)
    body_radius_entry.delete(0, tk.END)
    initial_x_entry.delete(0, tk.END)
    initial_y_entry.delete(0, tk.END)
    initial_orientation_entry.delete(0, tk.END)

def stop_simulation():
    global anim_global
    if anim_global is None:
        messagebox.showinfo("Info", "Tidak ada simulasi yang berjalan.")
        return

    anim_global.event_source.stop()

def exit_program():
    global anim_global
    if anim_global is not None:
        anim_global.event_source.stop()
    window.destroy()

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

# Tombol untuk memulai simulasi, reset, stop, dan keluar
start_button = tk.Button(window, text="Mulai Simulasi", command=start_simulation)
start_button.grid(row=8, column=0, columnspan=2)

reset_button = tk.Button(window, text="Reset", command=reset_simulation)
reset_button.grid(row=9, column=0, columnspan=2)

stop_button = tk.Button(window, text="Stop", command=stop_simulation)
stop_button.grid(row=10, column=0, columnspan=2)

exit_button = tk.Button(window, text="Keluar", command=exit_program)
exit_button.grid(row=11, column=0, columnspan=2)

window.mainloop()