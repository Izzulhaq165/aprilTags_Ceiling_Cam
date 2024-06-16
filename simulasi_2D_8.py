import tkinter as tk
from tkinter import messagebox, filedialog
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation
import pickle

# Variabel global untuk menyimpan objek animasi, widget canvas, posisi, dan orientasi terakhir
anim_global = None
canvas_widget = None
last_position = None
last_orientation = None

# Variabel global untuk menyimpan semua nilai yang telah dimasukkan oleh pengguna
saved_values = {
    "left_speed": None,
    "left_radius": None,
    "right_speed": None,
    "right_radius": None,
    "body_radius": None,
    "initial_x": None,
    "initial_y": None,
    "initial_orientation": None
}

# Variabel global untuk menyimpan nilai kecepatan translasi linier dan kecepatan angular robot
linear_speed = 0
angular_speed = 0

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

    # Label untuk parameter
    label_parameters = ax.text(1.05, 0.5, "", transform=ax.transAxes, va='center', ha='left')

    # Fungsi untuk mengupdate posisi dan orientasi robot
    def update(frame):
        nonlocal x, y, theta, linear_speed, angular_speed

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

        # Hitung kecepatan translasi linier dan kecepatan angular
        linear_speed = v
        angular_speed = omega

        # Memplot posisi robot dan jalur yang diikuti
        ax.clear()
        ax.plot(x_plot, y_plot, 'b-')
        ax.plot(x, y, 'bo')
        ax.set_xlim(min(x_plot) - 1, max(x_plot) + 1)
        ax.set_ylim(min(y_plot) - 1, max(y_plot) + 1)

        # Update label-parameter
        label_parameters.set_text(f"Linear Speed: {linear_speed:.2f}\nAngular Speed: {angular_speed:.2f}\nX: {x:.2f}\nY: {y:.2f}\nPsi: {np.degrees(theta):.2f}")

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

        if last_position is not None and last_orientation is not None:
            initial_x = last_position[0]
            initial_y = last_position[1]
            initial_orientation = last_orientation
        else:
            initial_x = float(initial_x_entry.get())
            initial_y = float(initial_y_entry.get())
            initial_orientation = float(initial_orientation_entry.get())

        fig, anim = differential_drive_simulation(left_speed, left_radius, right_speed, right_radius, body_radius, initial_x, initial_y, initial_orientation)
        global canvas_widget
        canvas = FigureCanvasTkAgg(fig, master=plot_frame)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.grid(row=0, column=1, rowspan=6)

        # Simpan objek animasi dalam variabel global
        anim_global = anim

        # Memastikan animasi tetap ada hingga plt.show() dipanggil
        anim._start()

    except ValueError:
        messagebox.showerror("Error", "Input harus berupa angka")

def stop_simulation():
    global anim_global
    if anim_global is not None:
        anim_global.event_source.stop()
        messagebox.showinfo("Info", "Simulasi dihentikan.")
    else:
        messagebox.showinfo("Info", "Tidak ada simulasi yang berjalan.")

def reset_simulation():
    global anim_global, last_position, last_orientation
    if anim_global is not None:
        anim_global.event_source.stop()
        last_position = None
        last_orientation = None
        canvas_widget.destroy()
        anim_global = None
        messagebox.showinfo("Info", "Simulasi di-reset.")
    else:
        messagebox.showinfo("Info", "Tidak ada simulasi yang berjalan.")

def continue_simulation():
    global anim_global
    if anim_global is not None:
        anim_global.event_source.start()
        messagebox.showinfo("Info", "Simulasi dilanjutkan.")
    else:
        messagebox.showinfo("Info", "Tidak ada simulasi yang berjalan.")

def save_simulation():
    global saved_values, last_position, last_orientation
    saved_values = {
        "left_speed": float(left_speed_entry.get()),
        "left_radius": float(left_radius_entry.get()),
        "right_speed": float(right_speed_entry.get()),
        "right_radius": float(right_radius_entry.get()),
        "body_radius": float(body_radius_entry.get()),
        "initial_x": float(initial_x_entry.get()),
        "initial_y": float(initial_y_entry.get()),
        "initial_orientation": float(initial_orientation_entry.get())
    }
    last_position = None
    last_orientation = None
    messagebox.showinfo("Info", "Nilai simulasi telah disimpan.")

def load_simulation():
    global saved_values, last_position, last_orientation
    if saved_values:
        left_speed_entry.delete(0, tk.END)
        left_speed_entry.insert(0, str(saved_values["left_speed"]))
        left_radius_entry.delete(0, tk.END)
        left_radius_entry.insert(0, str(saved_values["left_radius"]))
        right_speed_entry.delete(0, tk.END)
        right_speed_entry.insert(0, str(saved_values["right_speed"]))
        right_radius_entry.delete(0, tk.END)
        right_radius_entry.insert(0, str(saved_values["right_radius"]))
        body_radius_entry.delete(0, tk.END)
        body_radius_entry.insert(0, str(saved_values["body_radius"]))
        initial_x_entry.delete(0, tk.END)
        initial_x_entry.insert(0, str(saved_values["initial_x"]))
        initial_y_entry.delete(0, tk.END)
        initial_y_entry.insert(0, str(saved_values["initial_y"]))
        initial_orientation_entry.delete(0, tk.END)
        initial_orientation_entry.insert(0, str(saved_values["initial_orientation"]))
        last_position = None
        last_orientation = None
        messagebox.showinfo("Info", "Nilai simulasi telah dimuat.")
    else:
        messagebox.showinfo("Info", "Tidak ada nilai simulasi yang tersimpan.")

# Membuat GUI
window = tk.Tk()
window.title("Simulasi Robot Differential Drive")
window.geometry("1000x600")

# Frame untuk input
input_frame = tk.Frame(window)
input_frame.pack(side=tk.LEFT, padx=10, pady=10)

# Label dan input untuk kecepatan roda kiri
left_speed_label = tk.Label(input_frame, text="Kecepatan Roda Kiri:")
left_speed_label.grid(row=0, column=0, padx=5, pady=5)
left_speed_entry = tk.Entry(input_frame)
left_speed_entry.grid(row=0, column=1, padx=5, pady=5)

# Label dan input untuk radius roda kiri
left_radius_label = tk.Label(input_frame, text="Radius Roda Kiri:")
left_radius_label.grid(row=1, column=0, padx=5, pady=5)
left_radius_entry = tk.Entry(input_frame)
left_radius_entry.grid(row=1, column=1, padx=5, pady=5)

# Label dan input untuk kecepatan roda kanan
right_speed_label = tk.Label(input_frame, text="Kecepatan Roda Kanan:")
right_speed_label.grid(row=2, column=0, padx=5, pady=5)
right_speed_entry = tk.Entry(input_frame)
right_speed_entry.grid(row=2, column=1, padx=5, pady=5)

# Label dan input untuk radius roda kanan
right_radius_label = tk.Label(input_frame, text="Radius Roda Kanan:")
right_radius_label.grid(row=3, column=0, padx=5, pady=5)
right_radius_entry = tk.Entry(input_frame)
right_radius_entry.grid(row=3, column=1, padx=5, pady=5)

# Label dan input untuk radius body robot
body_radius_label = tk.Label(input_frame, text="Radius Body Robot:")
body_radius_label.grid(row=4, column=0, padx=5, pady=5)
body_radius_entry = tk.Entry(input_frame)
body_radius_entry.grid(row=4, column=1, padx=5, pady=5)

# Label dan input untuk posisi x awal
initial_x_label = tk.Label(input_frame, text="Posisi X Awal:")
initial_x_label.grid(row=5, column=0, padx=5, pady=5)
initial_x_entry = tk.Entry(input_frame)
initial_x_entry.grid(row=5, column=1, padx=5, pady=5)

# Label dan input untuk posisi y awal
initial_y_label = tk.Label(input_frame, text="Posisi Y Awal:")
initial_y_label.grid(row=6, column=0, padx=5, pady=5)
initial_y_entry = tk.Entry(input_frame)
initial_y_entry.grid(row=6, column=1, padx=5, pady=5)

# Label dan input untuk orientasi awal
initial_orientation_label = tk.Label(input_frame, text="Orientasi Awal (derajat):")
initial_orientation_label.grid(row=7, column=0, padx=5, pady=5)
initial_orientation_entry = tk.Entry(input_frame)
initial_orientation_entry.grid(row=7, column=1, padx=5, pady=5)

# Frame untuk plot
plot_frame = tk.Frame(window)
plot_frame.pack(side=tk.RIGHT, padx=10, pady=10)

# Button untuk memulai simulasi
start_button = tk.Button(input_frame, text="Mulai Simulasi", command=start_simulation)
start_button.grid(row=8, column=0, columnspan=2, padx=5, pady=5)

# Button untuk menghentikan simulasi
stop_button = tk.Button(input_frame, text="Stop Simulasi", command=stop_simulation)
stop_button.grid(row=9, column=0, columnspan=2, padx=5, pady=5)

# Button untuk mereset simulasi
reset_button = tk.Button(input_frame, text="Reset Simulasi", command=reset_simulation)
reset_button.grid(row=10, column=0, columnspan=2, padx=5, pady=5)

# Button untuk melanjutkan simulasi
continue_button = tk.Button(input_frame, text="Lanjutkan Simulasi", command=continue_simulation)
continue_button.grid(row=11, column=0, columnspan=2, padx=5, pady=5)

# Button untuk menyimpan parameter simulasi
save_values_button = tk.Button(input_frame, text="Simpan Nilai", command=save_simulation)
save_values_button.grid(row=12, column=0, columnspan=2, padx=5, pady=5)

# Button untuk memuat parameter simulasi
load_values_button = tk.Button(input_frame, text="Muat Nilai", command=load_simulation)
load_values_button.grid(row=13, column=0, columnspan=2, padx=5, pady=5)

# Button untuk keluar dari program
exit_button = tk.Button(input_frame, text="Keluar", command=window.quit)
exit_button.grid(row=14, column=0, columnspan=2, padx=5, pady=5)

# Mengatur ukuran relatif terhadap layar
window.grid_columnconfigure(1, weight=1)
window.grid_rowconfigure(0, weight=1)

window.mainloop()
