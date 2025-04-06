import tkinter as tk
from tkinter import messagebox, ttk
import numpy as np
import matplotlib.pyplot as plt
from sympy import sympify, symbols, lambdify, diff
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

x = symbols('x')

# Validar entradas dependiendo del método seleccionado
def validar_entrada():
    try:
        expr = sympify(funcion_entry.get())
        f = lambdify(x, expr)
        metodo = metodo_var.get()
        a_val = a_entry.get().strip()
        b_val = b_entry.get().strip()
        tolerancia_val = tolerancia_entry.get().strip()
        max_iter_val = max_iter_entry.get().strip()

        if not a_val or not tolerancia_val or not max_iter_val:
            messagebox.showerror("Error", "Por favor, completa todos los campos obligatorios.")
            return None, None, None, None, None, None

        a_val = float(a_val)
        tolerancia = float(tolerancia_val)
        max_iter = int(max_iter_val)

        if metodo in ["Bisección", "Falsa Posición"]:
            if not b_val:
                messagebox.showerror("Error", "El método seleccionado requiere un valor para 'b'.")
                return None, None, None, None, None, None
            b_val = float(b_val)
            if f(a_val) * f(b_val) >= 0:
                messagebox.showerror("Error", "El método seleccionado requiere f(a) * f(b) < 0.")
                return None, None, None, None, None, None
            return f, a_val, b_val, tolerancia, max_iter, expr

        elif metodo == "Newton-Raphson":
            df = lambdify(x, diff(expr, x))
            if df(a_val) == 0:
                messagebox.showerror("Error", "La derivada no debe ser 0 en x0 para Newton-Raphson.")
                return None, None, None, None, None, None
            return f, a_val, None, tolerancia, max_iter, df

    except Exception as e:
        messagebox.showerror("Error", f"Entrada no válida: {e}")
        return None, None, None, None, None, None

def calcular():
    f, a, b, tolerancia, max_iter, extra = validar_entrada()
    if f is None:
        return

    metodo = metodo_var.get()
    resultados = []
    raiz = None  # Variable para almacenar la raíz encontrada

    if metodo == "Bisección":
        for i in range(max_iter):
            c = (a + b) / 2.0
            fc = f(c)
            resultados.append((i+1, a, b, c, fc))
            if abs(fc) < tolerancia or abs(b - a) < tolerancia:
                raiz = c
                break
            elif f(a) * fc < 0:
                b = c
            else:
                a = c

    elif metodo == "Falsa Posición":
        for i in range(max_iter):
            fa, fb = f(a), f(b)
            c = b - fb * (b - a) / (fb - fa)
            fc = f(c)
            resultados.append((i+1, a, b, c, fc))
            if abs(fc) < tolerancia:
                raiz = c
                break
            elif fa * fc < 0:
                b = c
            else:
                a = c

    elif metodo == "Newton-Raphson":
        df = extra
        for i in range(max_iter):
            if df(a) == 0:
                messagebox.showerror("Error", f"La derivada se anuló en la iteración {i+1}. Abortando.")
                break
            c = a - f(a)/df(a)
            fc = f(c)
            resultados.append((i+1, a, '-', c, fc))
            if abs(fc) < tolerancia or abs(c - a) < tolerancia:
                raiz = c
                break
            a = c

    mostrar_resultados(resultados, metodo, raiz)

def mostrar_resultados(resultados, metodo, raiz):
    for row in tabla.get_children():
        tabla.delete(row)

    x_vals, y_vals = [], []
    for i, a, b, c, fc in resultados:
        tabla.insert("", "end", values=(i, a, b, c, fc))
        x_vals.append(i)
        y_vals.append(abs(fc))

    ax.clear()
    ax.plot(x_vals, y_vals, marker='o', linestyle='--', color='red')
    ax.set_facecolor("#87CEEB")
    ax.set_title(f"Convergencia - {metodo}")
    ax.set_xlabel("Iteración")
    ax.set_ylabel("|f(c)|")
    canvas.draw()
    
    # Mostrar la raíz encontrada solo para Falsa Posición
    if metodo == "Falsa Posición" and raiz is not None:
        raiz_label.config(text=f"Raíz encontrada: {raiz:.6f}")
    else:
        raiz_label.config(text="")

def borrar_datos():
    for row in tabla.get_children():
        tabla.delete(row)
    ax.clear()
    canvas.draw()
    funcion_entry.delete(0, tk.END)
    a_entry.delete(0, tk.END)
    b_entry.delete(0, tk.END)
    tolerancia_entry.delete(0, tk.END)
    max_iter_entry.delete(0, tk.END)
    raiz_label.config(text="")

# Ventana principal
root = tk.Tk()
root.title("Métodos de Raíces")
root.geometry("950x650")  # Aumenté un poco el tamaño para el nuevo recuadro
root.configure(bg="#d3d3d3")

frame_entrada = tk.Frame(root, bg="#d3d3d3")
frame_entrada.pack(pady=10)

tk.Label(frame_entrada, text="Función", bg="#d3d3d3").grid(row=0, column=0, padx=5)
funcion_entry = tk.Entry(frame_entrada, width=30)
funcion_entry.grid(row=0, column=1, padx=5)

tk.Label(frame_entrada, text="a (o x0)", bg="#d3d3d3").grid(row=0, column=2, padx=5)
a_entry = tk.Entry(frame_entrada, width=10)
a_entry.grid(row=0, column=3, padx=5)

tk.Label(frame_entrada, text="b", bg="#d3d3d3").grid(row=0, column=4, padx=5)
b_entry = tk.Entry(frame_entrada, width=10)
b_entry.grid(row=0, column=5, padx=5)

tk.Label(frame_entrada, text="Tolerancia", bg="#d3d3d3").grid(row=1, column=0, padx=5)
tolerancia_entry = tk.Entry(frame_entrada, width=10)
tolerancia_entry.grid(row=1, column=1, padx=5)

tk.Label(frame_entrada, text="Max iter", bg="#d3d3d3").grid(row=1, column=2, padx=5)
max_iter_entry = tk.Entry(frame_entrada, width=10)
max_iter_entry.grid(row=1, column=3, padx=5)

tk.Label(frame_entrada, text="Método", bg="#d3d3d3").grid(row=1, column=4, padx=5)
metodo_var = tk.StringVar(value="Bisección")
metodo_menu = ttk.Combobox(frame_entrada, textvariable=metodo_var, values=["Bisección", "Falsa Posición", "Newton-Raphson"], state="readonly")
metodo_menu.grid(row=1, column=5, padx=5)

tk.Button(frame_entrada, text="Calcular", command=calcular, bg="green").grid(row=2, column=4, pady=5)
tk.Button(frame_entrada, text="Borrar Datos", command=borrar_datos, bg="green").grid(row=2, column=5, pady=5)

# Frame para mostrar la raíz encontrada (solo para Falsa Posición)
frame_raiz = tk.Frame(root, bg="#d3d3d3")
frame_raiz.pack(pady=5)
raiz_label = tk.Label(frame_raiz, text="", bg="#d3d3d3", font=('Arial', 12, 'bold'))
raiz_label.pack()

frame_contenido = tk.Frame(root, bg="#d3d3d3")
frame_contenido.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

frame_grafica = tk.Frame(frame_contenido, bg="#d3d3d3")
frame_grafica.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

fig, ax = plt.subplots()
canvas = FigureCanvasTkAgg(fig, master=frame_grafica)
canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

frame_tabla = tk.Frame(frame_contenido, bg="#008000")
frame_tabla.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

scroll_x = ttk.Scrollbar(frame_tabla, orient=tk.HORIZONTAL)
scroll_y = ttk.Scrollbar(frame_tabla, orient=tk.VERTICAL)

tabla = ttk.Treeview(frame_tabla, columns=("Iteración", "a", "b", "c", "f(c)"), show="headings", xscrollcommand=scroll_x.set, yscrollcommand=scroll_y.set)
for col in ("Iteración", "a", "b", "c", "f(c)"):
    tabla.heading(col, text=col)
    tabla.column(col, width=150, anchor='center')

scroll_x.config(command=tabla.xview)
scroll_y.config(command=tabla.yview)

scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
tabla.pack(fill=tk.BOTH, expand=True)

root.mainloop()