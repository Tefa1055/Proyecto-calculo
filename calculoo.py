import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Parámetros fijos (no necesitas cambiarlos)
A = 0.2
k = 2.0
m = 0.5
omega_default = np.sqrt(k / m)

# Construcción del contexto "seguro" para eval
safe_dict = {'np': np, 'A': A, 'k': k, 'm': m, 'omega': omega_default, 'pi': np.pi, 'e': np.e}
# Añadir funciones numpy directamente (sin exposición completa innecesaria)
for name in ['sin','cos','tan','exp','sqrt','log','abs','arctan','arcsin','arccos']:
    safe_dict[name] = getattr(np, name)

def safe_eval(expr, t):
    """Evalúa expr en términos de t usando safe_dict. Devuelve np.array."""
    ctx = dict(safe_dict)
    ctx['t'] = t
    try:
        res = eval(expr, {"__builtins__": {}}, ctx)
        return np.array(res, dtype=float)
    except Exception as e:
        raise ValueError(f"Error al evaluar '{expr}': {e}")

def numeric_derivative(y, t):
    return np.gradient(y, t)

# Interfaz simple
class SimpleMAS(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("MAS Simple")
        self.geometry("880x560")
        self.create_widgets()

    def create_widgets(self):
        left = ttk.Frame(self, padding=8)
        left.pack(side="left", fill="y")

        ttk.Label(left, text="Fórmula x(t):").pack(anchor="w")
        self.entry_x = ttk.Entry(left, width=30)
        self.entry_x.pack(fill="x", pady=(0,6))
        self.entry_x.insert(0, "A*np.cos(omega*t)")

        ttk.Label(left, text="Fórmula y(t) (opcional para 2D):").pack(anchor="w")
        self.entry_y = ttk.Entry(left, width=30)
        self.entry_y.pack(fill="x", pady=(0,6))

        # Tiempo y resolución (pequeño)
        ttk.Label(left, text="t0, t1, puntos").pack(anchor="w", pady=(6,0))
        tframe = ttk.Frame(left)
        tframe.pack(fill="x", pady=(0,6))
        self.t0 = tk.DoubleVar(value=0.0)
        self.t1 = tk.DoubleVar(value=6.0)
        self.npoints = tk.IntVar(value=200)
        ttk.Entry(tframe, textvariable=self.t0, width=6).grid(row=0, column=0)
        ttk.Entry(tframe, textvariable=self.t1, width=6).grid(row=0, column=1, padx=4)
        ttk.Entry(tframe, textvariable=self.npoints, width=6).grid(row=0, column=2)

        # Tipo de gráfica (mínimo)
        ttk.Label(left, text="Tipo de gráfica:").pack(anchor="w", pady=(6,0))
        self.plot_type = tk.StringVar(value="pos1d")
        ttk.Radiobutton(left, text="Posición 1D (x vs t)", variable=self.plot_type, value="pos1d").pack(anchor="w")
        ttk.Radiobutton(left, text="Velocidad 1D (v vs t)", variable=self.plot_type, value="vel1d").pack(anchor="w")
        ttk.Radiobutton(left, text="Aceleración 1D (a vs t)", variable=self.plot_type, value="acc1d").pack(anchor="w")
        ttk.Radiobutton(left, text="Trayectoria 2D (x,y)", variable=self.plot_type, value="traj2d").pack(anchor="w")

        btns = ttk.Frame(left, padding=(0,8))
        btns.pack(fill="x", pady=(8,0))
        ttk.Button(btns, text="Graficar", command=self.plot).pack(side="left", padx=4)
        ttk.Button(btns, text="Guardar imagen...", command=self.save).pack(side="left", padx=4)
        ttk.Button(btns, text="Ayuda", command=self.help).pack(side="left", padx=4)

        # Área de figura (derecha)
        right = ttk.Frame(self)
        right.pack(side="left", fill="both", expand=True)
        self.fig, self.ax = plt.subplots(figsize=(7,5))
        self.canvas = FigureCanvasTkAgg(self.fig, master=right)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def help(self):
        msg = (
            "Instrucciones simples:\n"
            "- Escribe x(t) (obligatorio). Ejemplo: A*np.cos(omega*t)\n"
            "- Si quieres 2D escribe y(t) (ej. A*np.sin(omega*t)).\n"
            "- Los parámetros A,k,m están fijos: A=0.2, k=2.0, m=0.5.\n"
            "- omega se calcula automáticamente (omega = sqrt(k/m)).\n"
            "- Modifica solo t0, t1 y puntos si quieres más/menos tiempo o resolución.\n"
        )
        messagebox.showinfo("Ayuda", msg)

    def plot(self):
        self.ax.cla()
        t0 = float(self.t0.get())
        t1 = float(self.t1.get())
        n = int(self.npoints.get())
        if n < 10:
            messagebox.showerror("Error", "puntos debe ser >= 10")
            return
        t = np.linspace(t0, t1, n)

        expr_x = self.entry_x.get().strip()
        expr_y = self.entry_y.get().strip()
        ptype = self.plot_type.get()

        try:
            x = safe_eval(expr_x, t)
        except Exception as e:
            messagebox.showerror("Error x(t)", str(e))
            return

        if ptype == "pos1d":
            self.ax.plot(t, x)
            self.ax.set_xlabel("t (s)"); self.ax.set_ylabel("x(t) (m)")
            self.ax.set_title("Posición vs tiempo")
            self.ax.grid(True)
        elif ptype == "vel1d":
            v = numeric_derivative(x, t)
            self.ax.plot(t, v)
            self.ax.set_xlabel("t (s)"); self.ax.set_ylabel("v(t) (m/s)")
            self.ax.set_title("Velocidad vs tiempo")
            self.ax.grid(True)
        elif ptype == "acc1d":
            v = numeric_derivative(x, t)
            a = numeric_derivative(v, t)
            self.ax.plot(t, a)
            self.ax.set_xlabel("t (s)"); self.ax.set_ylabel("a(t) (m/s^2)")
            self.ax.set_title("Aceleración vs tiempo")
            self.ax.grid(True)
        elif ptype == "traj2d":
            if not expr_y:
                messagebox.showerror("Error", "Para 2D debes escribir y(t).")
                return
            try:
                y = safe_eval(expr_y, t)
            except Exception as e:
                messagebox.showerror("Error y(t)", str(e))
                return
            self.ax.plot(x, y)
            self.ax.set_aspect('equal', 'box')
            self.ax.set_xlabel("x (m)"); self.ax.set_ylabel("y (m)")
            self.ax.set_title("Trayectoria 2D")
            self.ax.grid(True)
        else:
            messagebox.showerror("Error", "Tipo de gráfica no soportado")

        self.canvas.draw()

    def save(self):
        file = filedialog.asksaveasfilename(defaultextension=".png",
                                            filetypes=[("PNG","*.png"),("PDF","*.pdf")])
        if file:
            self.fig.savefig(file, bbox_inches="tight")
            messagebox.showinfo("Guardado", f"Figura guardada en:\n{file}")

if __name__ == "__main__":
    app = SimpleMAS()
    app.mainloop()
