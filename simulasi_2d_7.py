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

def differential_drive_simulation(left_speed, left_radius, right_speed, right_radius, body_radius, initial_x, initial_y, initial_orientation):
    # Konversi sudut ke radian
    initial_orientation_rad = np.radians(initial_orientation)

    # Inisialisasi posisi dan orientasi
    x = initial_x
    y = initial_y
    theta = initial_orientation_rad

    # Jika posisi dan orientasi terakhir disimpan, gunakan untuk inisialisasi
    if last_position is not None and last_orientation is not None:
        x = last_position[0]
        y = last_position[1]
        theta = np.radians(last_orientation)

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

def reset_simulation():
    global anim_global, canvas_widget, last_position, last_orientation
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

    # Reset posisi dan orientasi terakhir
    last_position = None
    last_orientation = None

def stop_simulation():
    global anim_global, last_position, last_orientation
    if anim_global is None:
        messagebox.showinfo("Info", "Tidak ada simulasi yang berjalan.")
        return

    # Simpan posisi dan orientasi terakhir sebelum menghentikan simulasi
    last_position = (float(initial_x_entry.get()), float(initial_y_entry.get()))
    last_orientation = float(initial_orientation_entry.get())

    anim_global.event_source.stop()

def continue_simulation():
    global anim_global
    if anim_global is None:
        messagebox.showinfo("Info", "Tidak ada simulasi yang berhenti.")
        return

    anim_global.event_source.start()

def save_simulation():
    global anim_global
    if anim_global is None:
        messagebox.showinfo("Info", "Tidak ada simulasi yang berjalan.")
        return

    filename = filedialog.asksaveasfilename(defaultextension=".sim", filetypes=[("Simulation files", "*.sim")])
    if filename:
        with open(filename, 'wb') as file:
            pickle.dump((saved_values, last_position, last_orientation), file)
        messagebox.showinfo("Info", "Simulasi berhasil disimpan.")

def load_simulation():
    global saved_values, last_position, last_orientation
    filename = filedialog.askopenfilename(defaultextension=".sim", filetypes=[("Simulation files", "*.sim")])
    if filename:
        with open(filename, 'rb') as file:
            saved_values, last_position, last_orientation = pickle.load(file)
        messagebox.showinfo("Info", "Simulasi berhasil dimuat.")
        update_entry_values()
        start_simulation()  # Mulai simulasi dengan nilai yang dimuat

def clear_saved_values():
    global saved_values
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
    messagebox.showinfo("Info", "Semua nilai tersimpan berhasil dihapus.")

def update_entry_values():
    left_speed_entry.delete(0, tk.END)
    left_speed_entry.insert(0, str(saved_values["left_speed"]) if saved_values["left_speed"] is not None else "")
    left_radius_entry.delete(0, tk.END)
    left_radius_entry.insert(0, str(saved_values["left_radius"]) if saved_values["left_radius"] is not None else "")
    right_speed_entry.delete(0, tk.END)
    right_speed_entry.insert(0, str(saved_values["right_speed"]) if saved_values["right_speed"] is not None else "")
    right_radius_entry.delete(0, tk.END)
    right_radius_entry.insert(0, str(saved_values["right_radius"]) if saved_values["right_radius"] is not None else "")
    body_radius_entry.delete(0, tk.END)
    body_radius_entry.insert(0, str(saved_values["body_radius"]) if saved_values["body_radius"] is not None else "")
    initial_x_entry.delete(0, tk.END)
    initial_x_entry.insert(0, str(saved_values["initial_x"]) if saved_values["initial_x"] is not None else "")
    initial_y_entry.delete(0, tk.END)
    initial_y_entry.insert(0, str(saved_values["initial_y"]) if saved_values["initial_y"] is not None else "")
    initial_orientation_entry.delete(0, tk.END)
    initial_orientation_entry.insert(0, str(saved_values["initial_orientation"]) if saved_values["initial_orientation"] is not None else "")

def exit_program():
    global anim_global
    if anim_global is not None:
        anim_global.event_source.stop()
    window.destroy()

# Membuat GUI
window = tk.Tk()
window.title("Simulasi Gerakan Mobile Robot Differential Drive")

# Frame untuk input
input_frame = tk.Frame(window)
input_frame.grid(row=0, column=0)

tk.Label(input_frame, text="Kecepatan Roda Kiri:").grid(row=0, column=0, sticky="w")
left_speed_entry = tk.Entry(input_frame)
left_speed_entry.grid(row=0, column=1)

tk.Label(input_frame, text="Radius Roda Kiri:").grid(row=1, column=0, sticky="w")
left_radius_entry = tk.Entry(input_frame)
left_radius_entry.grid(row=1, column=1)

tk.Label(input_frame, text="Kecepatan Roda Kanan:").grid(row=2, column=0, sticky="w")
right_speed_entry = tk.Entry(input_frame)
right_speed_entry.grid(row=2, column=1)

tk.Label(input_frame, text="Radius Roda Kanan:").grid(row=3, column=0, sticky="w")
right_radius_entry = tk.Entry(input_frame)
right_radius_entry.grid(row=3, column=1)

tk.Label(input_frame, text="Radius Body:").grid(row=4, column=0, sticky="w")
body_radius_entry = tk.Entry(input_frame)
body_radius_entry.grid(row=4, column=1)

tk.Label(input_frame, text="Posisi X Awal:").grid(row=5, column=0, sticky="w")
initial_x_entry = tk.Entry(input_frame)
initial_x_entry.grid(row=5, column=1)

tk.Label(input_frame, text="Posisi Y Awal:").grid(row=6, column=0, sticky="w")
initial_y_entry = tk.Entry(input_frame)
initial_y_entry.grid(row=6, column=1)

tk.Label(input_frame, text="Orientasi Awal (derajat):").grid(row=7, column=0, sticky="w")
initial_orientation_entry = tk.Entry(input_frame)
initial_orientation_entry.grid(row=7, column=1)

# Frame untuk plotting
plot_frame = tk.Frame(window)
plot_frame.grid(row=0, column=1, rowspan=8)

# Frame untuk tombol
button_frame = tk.Frame(window)
button_frame.grid(row=8, column=0, columnspan=2)

start_button = tk.Button(button_frame, text="Mulai Simulasi", command=start_simulation)
start_button.grid(row=0, column=0, padx=5, pady=5)

reset_button = tk.Button(button_frame, text="Reset", command=reset_simulation)
reset_button.grid(row=0, column=1, padx=5, pady=5)

stop_button = tk.Button(button_frame, text="Stop", command=stop_simulation)
stop_button.grid(row=0, column=2, padx=5, pady=5)

continue_button = tk.Button(button_frame, text="Lanjutkan Simulasi", command=continue_simulation)
continue_button.grid(row=0, column=3, padx=5, pady=5)

save_button = tk.Button(button_frame, text="Save", command=save_simulation)
save_button.grid(row=0, column=4, padx=5, pady=5)

load_button = tk.Button(button_frame, text="Load", command=load_simulation)
load_button.grid(row=0, column=5, padx=5, pady=5)

exit_button = tk.Button(button_frame, text="Keluar", command=exit_program)
exit_button.grid(row=0, column=6, padx=5, pady=5)

# Mengatur ukuran relatif terhadap layar
window.grid_columnconfigure(1, weight=1)
window.grid_rowconfigure(0, weight=1)

window.mainloop()
