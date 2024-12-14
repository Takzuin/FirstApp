import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import mysql.connector
from mysql.connector import Error
from tkcalendar import DateEntry  # Importa DateEntry

# ... (Código de funciones conectar_base_datos, obtener_categorias, etc.)

# Función para conectar a la base de datos
def conectar_base_datos():
    try:
        # Establecer la conexión a la base de datos
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


# Función para obtener las categorías disponibles
def obtener_categorias():
    conexion = conectar_base_datos()
    categorias = []
    if conexion:
        cursor = conexion.cursor()
        try:
            query = "SELECT categoria_id, nombre FROM categorias"
            cursor.execute(query)
            categorias = cursor.fetchall()

        except Error as e:
            messagebox.showerror("Error", f"Error al obtener las categorías: {e}")
        finally:
            cursor.close()
            conexion.close()
    
    return categorias

# Función para registrar una transacción
def registrar_transaccion(tipo, monto, categoria_id, cuenta_id, descripcion):
    conexion = conectar_base_datos()
    if conexion:
        cursor = conexion.cursor()
        try:
            # SQL para insertar una nueva transacción
            query = """
            INSERT INTO transacciones (tipo, monto, categoria_id, cuenta_id, descripcion)
            VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(query, (tipo, monto, categoria_id, cuenta_id, descripcion))
            conexion.commit()  # Guardar los cambios
            messagebox.showinfo("Éxito", "Transacción registrada con éxito")

        except Error as e:
            messagebox.showerror("Error", f"Error al registrar la transacción: {e}")
        finally:
            cursor.close()
            conexion.close()

# Función para generar un reporte de gastos por categoría
def reporte_gastos_por_categoria(fecha_inicio, fecha_fin):
    conexion = conectar_base_datos()
    if conexion:
        cursor = conexion.cursor()
        try:
            query = """
            SELECT c.nombre AS categoria, SUM(t.monto) AS total_gastos
            FROM transacciones t
            JOIN categorias c ON t.categoria_id = c.categoria_id
            WHERE t.tipo = 'gasto' AND t.fecha BETWEEN %s AND %s
            GROUP BY t.categoria_id
            """
            cursor.execute(query, (fecha_inicio, fecha_fin))
            resultados = cursor.fetchall()

            reporte = "\nReporte de gastos por categoría:\n"
            for fila in resultados:
                reporte += f"Categoría: {fila[0]}, Total Gastado: {fila[1]:.2f}\n"

            messagebox.showinfo("Reporte de Gastos", reporte)

        except Error as e:
            messagebox.showerror("Error", f"Error al generar el reporte: {e}")
        finally:
            cursor.close()
            conexion.close()

# Función para registrar una meta financiera
def registrar_meta_financiera(nombre, objetivo, fecha_inicio, fecha_fin, usuario_id):
    conexion = conectar_base_datos()
    if conexion:
        cursor = conexion.cursor()
        try:
            query = """
            INSERT INTO metas_financieras (nombre, objetivo, fecha_inicio, fecha_fin, usuario_id)
            VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(query, (nombre, objetivo, fecha_inicio, fecha_fin, usuario_id))
            conexion.commit()
            messagebox.showinfo("Éxito", "Meta financiera registrada con éxito")

        except Error as e:
            messagebox.showerror("Error", f"Error al registrar la meta financiera: {e}")
        finally:
            cursor.close()
            conexion.close()

# Función para calcular el progreso de una meta financiera
def calcular_progreso_meta(meta_id):
    conexion = conectar_base_datos()
    if conexion:
        cursor = conexion.cursor()
        try:
            query_meta = """
            SELECT objetivo FROM metas_financieras WHERE meta_id = %s
            """
            cursor.execute(query_meta, (meta_id,))
            objetivo = cursor.fetchone()

            if objetivo:
                objetivo = objetivo[0]

                query_ingresos = """
                SELECT SUM(monto) FROM transacciones
                WHERE categoria_id = (SELECT categoria_id FROM categorias WHERE nombre = 'Ahorros') 
                AND tipo = 'ingreso'
                """
                cursor.execute(query_ingresos)
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

# Función para mostrar las categorías en un ComboBox
def mostrar_categorias():
    categorias = obtener_categorias()
    categoria_names = [categoria[1] for categoria in categorias]
    return categoria_names

# Interfaz de usuario con Tkinter
def registrar_transaccion_gui():
    tipo = tipo_entry.get()
    monto = float(monto_entry.get())
    categoria = categoria_var.get()
    cuenta_id = int(cuenta_id_entry.get())
    descripcion = descripcion_entry.get()

    if tipo and monto and categoria and cuenta_id:
        categoria_id = obtener_categorias()[categoria_names.index(categoria)][0]
        registrar_transaccion(tipo, monto, categoria_id, cuenta_id, descripcion)
    else:
        messagebox.showerror("Error", "Por favor, complete todos los campos.")

def generar_reporte():
    fecha_inicio = fecha_inicio_entry.get_date()  # Obtener fecha de DateEntry
    fecha_fin = fecha_fin_entry.get_date()      # Obtener fecha de DateEntry
    reporte_gastos_por_categoria(fecha_inicio, fecha_fin)

def registrar_meta_gui():


    nombre = meta_nombre_entry.get()
    objetivo = float(objetivo_entry.get())
    fecha_inicio = meta_fecha_inicio_entry.get_date()  # Obtener fecha de DateEntry
    fecha_fin = meta_fecha_fin_entry.get_date()      # Obtener fecha de DateEntry
    usuario_id = int(usuario_id_entry.get())

    if nombre and objetivo and fecha_inicio and fecha_fin and usuario_id:
        registrar_meta_financiera(nombre, objetivo, fecha_inicio, fecha_fin, usuario_id)  # Llamar a registrar_meta_financiera
    else:
        messagebox.showerror("Error", "Por favor, complete todos los campos.")
# Interfaz de usuario con Tkinter
def calcular_progreso_gui():
    meta_id = int(meta_id_entry.get())
    calcular_progreso_meta(meta_id) 
def mostrar_interfaz():
    window = tk.Tk()
    window.title("Gestión Financiera")

    # Estilo con ttk (opcional)
    style = ttk.Style()
    style.theme_use('clam')

    # Mostrar categorías disponibles
    global categoria_names  # Declarar categoria_names como global
    categoria_names = mostrar_categorias()

    # Interfaz gráfica (usando ttk)
    global tipo_entry, monto_entry, categoria_var, cuenta_id_entry, descripcion_entry 
    global fecha_inicio_entry, fecha_fin_entry
    global meta_nombre_entry, objetivo_entry, meta_fecha_inicio_entry, meta_fecha_fin_entry, usuario_id_entry
    global meta_id_entry 
    
    ttk.Label(window, text="Tipo de Transacción (ingreso/gasto)").grid(row=0, column=0, padx=5, pady=5)
    tipo_entry = ttk.Entry(window)
    tipo_entry.grid(row=0, column=1, padx=5, pady=5)

    ttk.Label(window, text="Monto").grid(row=1, column=0, padx=5, pady=5)
    monto_entry = ttk.Entry(window)
    monto_entry.grid(row=1, column=1, padx=5, pady=5)

    ttk.Label(window, text="Categoría").grid(row=2, column=0, padx=5, pady=5)
    categoria_var = tk.StringVar()
    categoria_combobox = ttk.Combobox(window, textvariable=categoria_var)
    categoria_combobox['values'] = categoria_names
    categoria_combobox.grid(row=2, column=1, padx=5, pady=5)

    ttk.Label(window, text="ID Cuenta").grid(row=3, column=0, padx=5, pady=5)
    cuenta_id_entry = ttk.Entry(window)
    cuenta_id_entry.grid(row=3, column=1, padx=5, pady=5)

    ttk.Label(window, text="Descripción (opcional)").grid(row=4, column=0, padx=5, pady=5)
    descripcion_entry = ttk.Entry(window)
    descripcion_entry.grid(row=4, column=1, padx=5, pady=5)

    ttk.Button(window, text="Registrar Transacción", command=registrar_transaccion_gui).grid(row=5, column=0, columnspan=2, pady=10)

    # Generar reporte
    ttk.Label(window, text="Fecha Inicio").grid(row=6, column=0, padx=5, pady=5)
    fecha_inicio_entry = DateEntry(window, date_pattern='yyyy-mm-dd') 
    fecha_inicio_entry.grid(row=6, column=1, padx=5, pady=5)

    ttk.Label(window, text="Fecha Fin").grid(row=7, column=0, padx=5, pady=5)
    fecha_fin_entry = DateEntry(window, date_pattern='yyyy-mm-dd')
    fecha_fin_entry.grid(row=7, column=1, padx=5, pady=5)

    ttk.Button(window, text="Generar Reporte", command=generar_reporte).grid(row=8, column=0, columnspan=2, pady=10)

    # Registrar meta financiera
    ttk.Label(window, text="Nombre de la Meta").grid(row=9, column=0, padx=5, pady=5)
    meta_nombre_entry = ttk.Entry(window)
    meta_nombre_entry.grid(row=9, column=1, padx=5, pady=5)

    ttk.Label(window, text="Objetivo de la Meta").grid(row=10, column=0, padx=5, pady=5)
    objetivo_entry = ttk.Entry(window)
    objetivo_entry.grid(row=10, column=1, padx=5, pady=5)

    ttk.Label(window, text="Fecha Inicio Meta").grid(row=11, column=0, padx=5, pady=5)
    meta_fecha_inicio_entry = DateEntry(window, date_pattern='yyyy-mm-dd')
    meta_fecha_inicio_entry.grid(row=11, column=1, padx=5, pady=5)

    ttk.Label(window, text="Fecha Fin Meta").grid(row=12, column=0, padx=5, pady=5)
    meta_fecha_fin_entry = DateEntry(window, date_pattern='yyyy-mm-dd')
    meta_fecha_fin_entry.grid(row=12, column=1, padx=5, pady=5)

    ttk.Label(window, text="ID Usuario").grid(row=13, column=0, padx=5, pady=5)
    usuario_id_entry = ttk.Entry(window)
    usuario_id_entry.grid(row=13, column=1, padx=5, pady=5)

    ttk.Button(window, text="Registrar Meta", command=registrar_meta_gui).grid(row=14, column=0, columnspan=2, pady=10)

    # Calcular progreso
    ttk.Label(window, text="ID de Meta").grid(row=15, column=0, padx=5, pady=5)
    meta_id_entry = ttk.Entry(window)
    meta_id_entry.grid(row=15, column=1, padx=5, pady=5)

    ttk.Button(window, text="Calcular Progreso", command=calcular_progreso_gui).grid(row=16, column=0, columnspan=2, pady=10)

    window.mainloop()

if __name__ == "__main__":
    mostrar_interfaz()