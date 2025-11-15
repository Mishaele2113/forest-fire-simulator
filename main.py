import tkinter as tk
import numpy as np
import matplotlib.pyplot as plt
from enum import Enum
from typing import Tuple, List
from matplotlib.colors import ListedColormap
from scipy.ndimage import convolve
from matplotlib.animation import FuncAnimation

class NeighborhoodType(Enum):
    MOORE = "moore"
    VON_NEUMANN = "von_neumann"

class CellState(Enum):
    EMPTY = 0
    FIRING = 1
    TREE = 2

colors = ["#49423D", "orange", "green"]
cmap_forest = ListedColormap(colors)

class CellColor(Enum):
    EMPTY = colors[0]
    FIRING = colors[1]
    TREE = colors[2]

def create_ca(w: int, h: int):
    return np.zeros((w, h))

def init_state(ca: np.ndarray, eta: float, f: int):
    w, h = ca.shape
    tree_mask = np.random.rand(w, h) <= eta
    ca[tree_mask] = CellState.TREE.value
    tree_indices = np.argwhere(ca == CellState.TREE.value)
    if f > len(tree_indices):
        f = len(tree_indices)
    fire_indices = tree_indices[np.random.choice(len(tree_indices), f, replace=False)]
    for i, j in fire_indices:
        ca[i, j] = CellState.FIRING.value
    return ca

def get_kernel(nt: NeighborhoodType) -> np.ndarray:
    if nt == NeighborhoodType.MOORE:
        return np.array([[1, 1, 1],
                         [1, 0, 1],
                         [1, 1, 1]])
    elif nt == NeighborhoodType.VON_NEUMANN:
        return np.array([[0, 1, 0],
                         [1, 0, 1],
                         [0, 1, 0]])
    else:
        raise ValueError(f"Unknown neighborhood type: {nt}")

def update(ca: np.ndarray, nt: NeighborhoodType, p_g: float, p_f: float, boundary: str = "periodic"):
    kernel = get_kernel(nt)
    mode = "wrap" if boundary == "periodic" else "nearest"
    fire_mask = (ca == CellState.FIRING.value).astype(np.uint8)
    fire_neighbors = convolve(fire_mask, kernel, mode=mode)
    new_ca = np.copy(ca)
    new_ca[ca == CellState.FIRING.value] = CellState.EMPTY.value
    tree_mask = (ca == CellState.TREE.value)
    ignite_mask = (fire_neighbors > 0) & tree_mask
    random_fire = (np.random.rand(*ca.shape) < p_f) & tree_mask & (~ignite_mask)
    new_ca[ignite_mask | random_fire] = CellState.FIRING.value
    empty_mask = (ca == CellState.EMPTY.value)
    grow_mask = (np.random.rand(*ca.shape) < p_g) & empty_mask
    new_ca[grow_mask] = CellState.TREE.value
    return new_ca

class Statistics:
    def __init__(self):
        self.t = []
        self.a_f = []
        self.a_t = []
        self.a_e = []

    def append(self, t: int, ca: np.ndarray):
        self.t.append(t)
        self.a_f.append(np.sum(ca == CellState.FIRING.value))
        self.a_t.append(np.sum(ca == CellState.TREE.value))
        self.a_e.append(np.sum(ca == CellState.EMPTY.value))

    def plot_firing_time(self, ax):
        ax.plot(self.t, self.a_f, label="Горящие деревья", color="orange")
        ax.set_xlabel("Время")
        ax.legend()
        return ax

    def plot_trees_time(self, ax):
        ax.plot(self.t, self.a_t, label="Обычные деревья", color="green")
        ax.set_xlabel("Время")
        ax.legend()
        return ax

    def plot_empty_time(self, ax):
        ax.plot(self.t, self.a_e, label="Свободные места для новых деревьев", color="gray")
        ax.set_xlabel("Время")
        ax.legend()
        return ax

def simulate(ca: np.ndarray, nt: NeighborhoodType, time: int, p_g: float, p_f: float, boundary: str = "periodic"):
    st = Statistics()
    evolution = []
    for t in range(time):
        ca = update(ca, nt, p_g, p_f, boundary)
        st.append(t, ca)
        evolution.append(np.copy(ca))
    return st, evolution

def visualize_evolution(evolution: List[np.ndarray], interval: int = 100):
    fig, ax = plt.subplots(figsize=(5, 6))
    im = ax.matshow(evolution[0], cmap=cmap_forest)
    fig.suptitle("Визуализация моделирования лесного пожара")

    def update(frame):
        im.set_data(evolution[frame])
        ax.set_title(f"Время: {frame + 1}")
        return [im]

    ani = FuncAnimation(fig, update, frames=len(evolution), interval=100, repeat=False)
    ani.save(filename="res.gif", writer="ffmpeg")
    plt.show()

root = tk.Tk()
root.iconbitmap("icon.ico")
root.title("Моделирование лесного пожара")

seed_var = tk.IntVar(value=1234)
grid_w_var = tk.IntVar(value=200)
grid_h_var = tk.IntVar(value=200)
eta_var = tk.DoubleVar(value=0.15)
f_var = tk.IntVar(value=1)
p_g_var = tk.DoubleVar(value=1e-2)
p_f_var = tk.DoubleVar(value=1e-5)  
sim_time_var = tk.IntVar(value=5000)
boundary_type_var = tk.StringVar()
cv_var = tk.StringVar()

boundary_type_list = ("Отражение", "Повторение")
cv_list = ("Мура", "фон Неймана")

config_frame = tk.LabelFrame(root, text="Параметры", padx=10, pady=10)
config_frame.pack(padx=10, pady=10, fill="x")

label = tk.Label(config_frame, text="Начальное число ГСЧ:")
label.grid(row=0, column=0, padx=5, pady=5, sticky="e")
entry = tk.Entry(config_frame, textvariable=seed_var, width=15)
entry.grid(row=0, column=1, padx=5, pady=5)

label = tk.Label(config_frame, text="Размер сетки деревьев:")
label.grid(row=1, column=0, padx=5, pady=5, sticky="e")
entry = tk.Entry(config_frame, textvariable=grid_w_var, width=15)
entry.grid(row=1, column=1, padx=5, pady=5)
label = tk.Label(config_frame, text="x")
label.grid(row=1, column=2, padx=5, pady=5, sticky="e")
entry = tk.Entry(config_frame, textvariable=grid_h_var, width=15)
entry.grid(row=1, column=3, padx=5, pady=5)

label = tk.Label(config_frame, text="Начальное заполнение деревьями:")
label.grid(row=2, column=0, padx=5, pady=5, sticky="e")
entry = tk.Entry(config_frame, textvariable=eta_var, width=15)
entry.grid(row=2, column=1, padx=5, pady=5)

label = tk.Label(config_frame, text="Начальное количество горящих деревьев:")
label.grid(row=3, column=0, padx=5, pady=5, sticky="e")
entry = tk.Entry(config_frame, textvariable=f_var, width=15)
entry.grid(row=3, column=1, padx=5, pady=5)

label = tk.Label(config_frame, text="Частота роста деревьев:")
label.grid(row=4, column=0, padx=5, pady=5, sticky="e")
entry = tk.Entry(config_frame, textvariable=p_g_var, width=15)
entry.grid(row=4, column=1, padx=5, pady=5)

label = tk.Label(config_frame, text="Частота возникновения пожара:")
label.grid(row=5, column=0, padx=5, pady=5, sticky="e")
entry = tk.Entry(config_frame, textvariable=p_f_var, width=15)
entry.grid(row=5, column=1, padx=5, pady=5)

label = tk.Label(config_frame, text="Длительность моделирования:")
label.grid(row=6, column=0, padx=5, pady=5, sticky="e")
entry = tk.Entry(config_frame, textvariable=sim_time_var, width=15)
entry.grid(row=6, column=1, padx=5, pady=5)

label = tk.Label(config_frame, text="Представление границы:")
label.grid(row=7, column=0, padx=5, pady=5, sticky="e")
spin = tk.Spinbox(config_frame, values=boundary_type_list, textvariable=boundary_type_var, width=15)
spin.grid(row=7, column=1, padx=5, pady=5)

label = tk.Label(config_frame, text="Окрестность:")
label.grid(row=8, column=0, padx=5, pady=5, sticky="e")
spin = tk.Spinbox(config_frame, values=cv_list, textvariable=cv_var, width=15)
spin.grid(row=8, column=1, padx=5, pady=5)

def run():
    root.quit()

    np.random.RandomState(seed=seed_var.get())

    if boundary_type_list.index(boundary_type_var.get()) == 0:
        boundary_type = "reflective"
    else:
        boundary_type = "periodic"

    if cv_list.index(cv_var.get()) == 0:
        cv = NeighborhoodType.MOORE
    else:
        cv = NeighborhoodType.VON_NEUMANN

    ca = create_ca(grid_w_var.get(), grid_h_var.get())
    init_state(ca, eta_var.get(), f_var.get())
    st, evolution = simulate(ca, cv, time=sim_time_var.get(), p_g=p_g_var.get(), p_f=p_f_var.get(), boundary=boundary_type)
    fig, ax = plt.subplots(3, 1, figsize=(10, 15))
    fig.suptitle("Результат моделирования лесного пожара")
    st.plot_firing_time(ax[0])
    st.plot_trees_time(ax[1])
    st.plot_empty_time(ax[2])
    plt.show()
    visualize_evolution(evolution, interval=1)

run_button = tk.Button(root, text="Расчёт", command=run)
run_button.pack(pady=5)

root.mainloop()