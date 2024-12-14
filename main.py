import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import mysql.connector
from mysql.connector import Error
from tkcalendar import DateEntry  # Importa DateEntry

# Conexión a la base de datos
def conectar_base_datos():
    try:
        conexion = mysql.connector.connect(
            host='localhost',  # Cambia por la dirección de tu servidor si no es local
            database='FinanzasDB',
            user='root',  # Cambia por tu usuario
            password=''  # Cambia por tu contraseña
        )
        if conexion.is_connected():
            print("Conexión exitosa a la base de datos")
            return conexion
    except Error as e:
        messagebox.showerror("Error de conexión", f"Error al conectar a la base de datos: {e}")
        return None

# Función para registrar una transacción
def registrar_transaccion(tipo, monto, categoria):
    conexion = conectar_base_datos()
    if conexion:
        cursor = conexion.cursor()
        try:
            # Buscar la categoría o crearla si no existe
            cursor.execute("SELECT categoria_id FROM categorias WHERE nombre = %s", (categoria,))
            resultado = cursor.fetchone()
            if resultado:
                categoria_id = resultado[0]
            else:
                cursor.execute("INSERT INTO categorias (nombre) VALUES (%s)", (categoria,))
                conexion.commit()
                categoria_id = cursor.lastrowid

            # Insertar la transacción
            query = """
            INSERT INTO transacciones (tipo, monto, categoria_id)
            VALUES (%s, %s, %s)
            """
            cursor.execute(query, (tipo, monto, categoria_id))
            conexion.commit()
            messagebox.showinfo("Éxito", "Transacción registrada con éxito")
        except Error as e:
            messagebox.showerror("Error", f"Error al registrar la transacción: {e}")
        finally:
            cursor.close()
            conexion.close()

# Función para generar reportes de gastos categorizados
def generar_reporte_gastos():
    conexion = conectar_base_datos()
    if conexion:
        cursor = conexion.cursor()
        try:
            query = """
            SELECT c.nombre AS categoria, SUM(t.monto) AS total_gastos
            FROM transacciones t
            JOIN categorias c ON t.categoria_id = c.categoria_id
            WHERE t.tipo = 'gasto'
            GROUP BY c.nombre
            """
            cursor.execute(query)
            resultados = cursor.fetchall()

            if resultados:
                reporte = "\nReporte de gastos por categoría:\n"
                for fila in resultados:
                    reporte += f"Categoría: {fila[0]}, Total Gastado: {fila[1]:.2f}\n"
                messagebox.showinfo("Reporte de Gastos", reporte)
            else:
                messagebox.showinfo("Reporte de Gastos", "No se encontraron datos de gastos.")
        except Error as e:
            messagebox.showerror("Error", f"Error al generar el reporte: {e}")
        finally:
            cursor.close()
            conexion.close()

# Función para calcular el progreso hacia metas financieras
def calcular_progreso_meta(meta_id):
    conexion = conectar_base_datos()
    if conexion:
        cursor = conexion.cursor()
        try:
            query_meta = """
            SELECT objetivo FROM metas_financieras WHERE meta_id = %s
            """
            cursor.execute(query_meta, (meta_id,))
            resultado = cursor.fetchone()

            if resultado:
                objetivo = resultado[0]
                query_ahorros = """
                SELECT SUM(monto) FROM transacciones
                WHERE tipo = 'ingreso'
                """
                cursor.execute(query_ahorros)
                ahorros_totales = cursor.fetchone()[0] or 0

                progreso = (ahorros_totales / objetivo) * 100
                messagebox.showinfo("Progreso de Meta", f"Progreso hacia la meta: {progreso:.2f}%")
            else:
                messagebox.showerror("Error", "Meta no encontrada")
        except Error as e:
            messagebox.showerror("Error", f"Error al calcular el progreso: {e}")
        finally:
            cursor.close()
            conexion.close()

# Función para analizar patrones de gasto
def analizar_patrones_gasto():
    conexion = conectar_base_datos()
    if conexion:
        cursor = conexion.cursor()
        try:
            query = """
            SELECT c.nombre AS categoria, COUNT(*) AS cantidad, AVG(t.monto) AS promedio
            FROM transacciones t
            JOIN categorias c ON t.categoria_id = c.categoria_id
            WHERE t.tipo = 'gasto'
            GROUP BY c.nombre
            """
            cursor.execute(query)
            resultados = cursor.fetchall()

            if resultados:
                reporte = "\nAnálisis de patrones de gasto:\n"
                for fila in resultados:
                    reporte += f"Categoría: {fila[0]}, Cantidad de Gastos: {fila[1]}, Promedio por Gasto: {fila[2]:.2f}\n"
                messagebox.showinfo("Patrones de Gasto", reporte)
            else:
                messagebox.showinfo("Patrones de Gasto", "No se encontraron patrones de gasto.")
        except Error as e:
            messagebox.showerror("Error", f"Error al analizar patrones de gasto: {e}")
        finally:
            cursor.close()
            conexion.close()

# Función para registrar desde la interfaz
def registrar_transaccion_gui():
    try:
        tipo = tipo_entry.get().strip()
        monto = float(monto_entry.get())
        categoria = categoria_var.get().strip()

        if tipo and monto and categoria:
            registrar_transaccion(tipo, monto, categoria)
        else:
            messagebox.showerror("Error", "Por favor, complete todos los campos.")
    except ValueError:
        messagebox.showerror("Error", "Monto inválido. Debe ser un número.")
    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error: {e}")

# Función para mostrar la interfaz gráfica
def mostrar_interfaz():
    window = tk.Tk()
    window.title("Gestión Financiera Simplificada")

    # Campos para transacción
    ttk.Label(window, text="Tipo de Transacción (ingreso/gasto)").grid(row=0, column=0, padx=5, pady=5)
    global tipo_entry
    tipo_entry = ttk.Entry(window)
    tipo_entry.grid(row=0, column=1, padx=5, pady=5)

    ttk.Label(window, text="Monto").grid(row=1, column=0, padx=5, pady=5)
    global monto_entry
    monto_entry = ttk.Entry(window)
    monto_entry.grid(row=1, column=1, padx=5, pady=5)

    ttk.Label(window, text="Categoría").grid(row=2, column=0, padx=5, pady=5)
    global categoria_var
    categoria_var = tk.StringVar()
    categoria_entry = ttk.Entry(window, textvariable=categoria_var)
    categoria_entry.grid(row=2, column=1, padx=5, pady=5)

    ttk.Button(window, text="Registrar Transacción", command=registrar_transaccion_gui).grid(row=3, column=0, columnspan=2, pady=10)

    # Botones adicionales
    ttk.Button(window, text="Generar Reporte de Gastos", command=generar_reporte_gastos).grid(row=4, column=0, columnspan=2, pady=10)
    ttk.Button(window, text="Analizar Patrones de Gasto", command=analizar_patrones_gasto).grid(row=5, column=0, columnspan=2, pady=10)

    window.mainloop()

if __name__ == "__main__":
    mostrar_interfaz()
