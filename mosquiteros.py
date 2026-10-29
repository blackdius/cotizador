import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import json
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

class CotizadorMosquiteros:
    def __init__(self, root):
        self.root = root
        self.root.title("Cotizador Profesional de Mosquiteros")
        self.root.geometry("1100x1000")
        self.root.minsize(1000, 900)
        self.root.configure(bg="#f4f6f9")

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TNotebook", background="#f4f6f9")
        style.configure("TNotebook.Tab", font=("Segoe UI", 11, "bold"), padding=[16, 8])
        style.configure("TFrame", background="#f4f6f9")
        style.configure("TLabel", background="#f4f6f9", font=("Segoe UI", 10))
        style.configure("Treeview", font=("Segoe UI", 10), rowheight=28)
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))

        # Archivos de guardado
        self.archivo_materiales = "materiales.json"
        self.archivo_proveedores = "proveedores.json"

        self.materiales_default = {
            "Perfil Aluminio Natural (por metro)": 6033.33,
            "Perfil Aluminio Blanco (por metro)": 6800.00,
            "Perfil Aluminio Color (por metro)": 7500.00,
            "Tela mosquitera (por m²)": 4250.00,
            "Cordón N60 (por metro)": 200.00,
            "Escuadra Mosquitero (juego x4)": 1200.00,
            "Burlete Lateral (por metro)": 6000.00,
            "Escuadra estriada 7mm (juego x4)": 443.00,
            "Accesorios Varios": 2500.00,
            "Mano de Obra / Instalación": 8000.00,
        }

        self.materiales = self.cargar_materiales()
        self.proveedores = self.cargar_proveedores()

        self.desperdicio_perfil = 0.12
        self.desperdicio_tela = 0.10

        # Notebook
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True, padx=12, pady=12)

        # Solapas en orden: Materiales → Proveedores → Cotizar
        self.tab_materiales = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_materiales, text="  Materiales y Precios  ")

        self.tab_proveedores = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_proveedores, text="  Proveedores  ")

        self.tab_cotizar = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_cotizar, text="  Cotizar / Factura  ")

        self.crear_tab_materiales()
        self.crear_tab_proveedores()
        self.crear_tab_cotizar()

    # ==================== GUARDAR / CARGAR ====================
    def cargar_materiales(self):
        if os.path.exists(self.archivo_materiales):
            try:
                with open(self.archivo_materiales, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return self.materiales_default.copy()
        return self.materiales_default.copy()

    def guardar_materiales(self):
        try:
            with open(self.archivo_materiales, "w", encoding="utf-8") as f:
                json.dump(self.materiales, f, indent=4, ensure_ascii=False)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron guardar los materiales:\n{e}")

    def cargar_proveedores(self):
        if os.path.exists(self.archivo_proveedores):
            try:
                with open(self.archivo_proveedores, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return []
        return []

    def guardar_proveedores(self):
        try:
            with open(self.archivo_proveedores, "w", encoding="utf-8") as f:
                json.dump(self.proveedores, f, indent=4, ensure_ascii=False)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron guardar los proveedores:\n{e}")

    # ==================== PESTAÑA MATERIALES ====================
    def crear_tab_materiales(self):
        frame = ttk.Frame(self.tab_materiales, padding=20)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Listado de Materiales (todos editables - se guardan automáticamente)",
                  font=("Segoe UI", 14, "bold"), foreground="#1a3c6e").pack(anchor="w", pady=(0, 12))

        columnas = ("material", "precio")
        self.tree_materiales = ttk.Treeview(frame, columns=columnas, show="headings", height=14)
        self.tree_materiales.heading("material", text="Material")
        self.tree_materiales.heading("precio", text="Precio ($)")
        self.tree_materiales.column("material", width=520)
        self.tree_materiales.column("precio", width=140, anchor="e")
        self.tree_materiales.pack(fill="x", pady=(0, 12))

        self.actualizar_tree_materiales()

        frame_editar = ttk.LabelFrame(frame, text=" Editar / Agregar Material ", padding=12)
        frame_editar.pack(fill="x", pady=8)

        ttk.Label(frame_editar, text="Nombre del material:").grid(row=0, column=0, sticky="e", padx=5, pady=6)
        self.entry_nombre_material = ttk.Entry(frame_editar, width=45, font=("Segoe UI", 10))
        self.entry_nombre_material.grid(row=0, column=1, columnspan=2, sticky="w", pady=6)

        ttk.Label(frame_editar, text="Precio:").grid(row=1, column=0, sticky="e", padx=5, pady=6)
        self.entry_nuevo_precio = ttk.Entry(frame_editar, width=18, font=("Segoe UI", 10))
        self.entry_nuevo_precio.grid(row=1, column=1, sticky="w", pady=6)

        frame_botones = ttk.Frame(frame_editar)
        frame_botones.grid(row=2, column=0, columnspan=3, pady=(10, 0))

        tk.Button(frame_botones, text="Actualizar", font=("Segoe UI", 10, "bold"),
                  bg="#1a3c6e", fg="white", relief="flat", padx=14, pady=6,
                  cursor="hand2", command=self.actualizar_material).pack(side="left", padx=6)

        tk.Button(frame_botones, text="Agregar Nuevo", font=("Segoe UI", 10, "bold"),
                  bg="#2e7d32", fg="white", relief="flat", padx=14, pady=6,
                  cursor="hand2", command=self.agregar_material).pack(side="left", padx=6)

        tk.Button(frame_botones, text="Eliminar", font=("Segoe UI", 10, "bold"),
                  bg="#c62828", fg="white", relief="flat", padx=14, pady=6,
                  cursor="hand2", command=self.eliminar_material).pack(side="left", padx=6)

        self.tree_materiales.bind("<<TreeviewSelect>>", self.cargar_material_seleccionado)

        ttk.Label(frame, text="Los cambios se guardan automáticamente en el archivo materiales.json",
                  font=("Segoe UI", 9), foreground="#666").pack(anchor="w", pady=(10, 0))

    def actualizar_tree_materiales(self):
        for item in self.tree_materiales.get_children():
            self.tree_materiales.delete(item)
        for mat, precio in self.materiales.items():
            self.tree_materiales.insert("", "end", values=(mat, f"{precio:,.2f}"))

    def cargar_material_seleccionado(self, event=None):
        seleccionado = self.tree_materiales.selection()
        if seleccionado:
            valores = self.tree_materiales.item(seleccionado[0], "values")
            self.entry_nombre_material.delete(0, tk.END)
            self.entry_nombre_material.insert(0, valores[0])
            self.entry_nuevo_precio.delete(0, tk.END)
            self.entry_nuevo_precio.insert(0, valores[1].replace(",", ""))

    def actualizar_material(self):
        seleccionado = self.tree_materiales.selection()
        if not seleccionado:
            messagebox.showwarning("Aviso", "Seleccioná un material de la lista")
            return
        try:
            nombre_nuevo = self.entry_nombre_material.get().strip()
            precio_nuevo = float(self.entry_nuevo_precio.get().replace(",", "."))
            if not nombre_nuevo:
                messagebox.showwarning("Aviso", "El nombre no puede estar vacío")
                return
            nombre_viejo = self.tree_materiales.item(seleccionado[0], "values")[0]
            if nombre_viejo in self.materiales:
                del self.materiales[nombre_viejo]
            self.materiales[nombre_nuevo] = precio_nuevo
            self.actualizar_tree_materiales()
            self.guardar_materiales()
            messagebox.showinfo("Éxito", "Material actualizado y guardado")
        except ValueError:
            messagebox.showerror("Error", "Ingresá un precio válido")

    def agregar_material(self):
        try:
            nombre = self.entry_nombre_material.get().strip()
            precio = float(self.entry_nuevo_precio.get().replace(",", "."))
            if not nombre:
                messagebox.showwarning("Aviso", "Escribí el nombre del material")
                return
            if nombre in self.materiales:
                messagebox.showwarning("Aviso", "Ese material ya existe")
                return
            self.materiales[nombre] = precio
            self.actualizar_tree_materiales()
            self.guardar_materiales()
            self.entry_nombre_material.delete(0, tk.END)
            self.entry_nuevo_precio.delete(0, tk.END)
            messagebox.showinfo("Éxito", f"Material \"{nombre}\" agregado y guardado")
        except ValueError:
            messagebox.showerror("Error", "Ingresá un precio válido")

    def eliminar_material(self):
        seleccionado = self.tree_materiales.selection()
        if not seleccionado:
            messagebox.showwarning("Aviso", "Seleccioná un material para eliminar")
            return
        nombre = self.tree_materiales.item(seleccionado[0], "values")[0]
        if messagebox.askyesno("Confirmar", f"¿Eliminar \"{nombre}\"?"):
            if nombre in self.materiales:
                del self.materiales[nombre]
            self.actualizar_tree_materiales()
            self.guardar_materiales()
            self.entry_nombre_material.delete(0, tk.END)
            self.entry_nuevo_precio.delete(0, tk.END)

    # ==================== PESTAÑA PROVEEDORES ====================
    def crear_tab_proveedores(self):
        frame = ttk.Frame(self.tab_proveedores, padding=20)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Agenda de Proveedores (se guarda automáticamente)",
                  font=("Segoe UI", 14, "bold"), foreground="#1a3c6e").pack(anchor="w", pady=(0, 12))

        # Treeview
        columnas = ("nombre", "telefono", "direccion")
        self.tree_proveedores = ttk.Treeview(frame, columns=columnas, show="headings", height=12)
        self.tree_proveedores.heading("nombre", text="Nombre / Empresa")
        self.tree_proveedores.heading("telefono", text="Teléfono")
        self.tree_proveedores.heading("direccion", text="Dirección")
        self.tree_proveedores.column("nombre", width=280)
        self.tree_proveedores.column("telefono", width=160)
        self.tree_proveedores.column("direccion", width=380)
        self.tree_proveedores.pack(fill="x", pady=(0, 12))

        self.actualizar_tree_proveedores()

        # Formulario
        frame_editar = ttk.LabelFrame(frame, text=" Agregar / Editar Proveedor ", padding=15)
        frame_editar.pack(fill="x", pady=8)

        ttk.Label(frame_editar, text="Nombre / Empresa:").grid(row=0, column=0, sticky="e", padx=8, pady=6)
        self.entry_prov_nombre = ttk.Entry(frame_editar, width=40, font=("Segoe UI", 10))
        self.entry_prov_nombre.grid(row=0, column=1, sticky="w", pady=6)

        ttk.Label(frame_editar, text="Teléfono:").grid(row=1, column=0, sticky="e", padx=8, pady=6)
        self.entry_prov_telefono = ttk.Entry(frame_editar, width=25, font=("Segoe UI", 10))
        self.entry_prov_telefono.grid(row=1, column=1, sticky="w", pady=6)

        ttk.Label(frame_editar, text="Dirección:").grid(row=2, column=0, sticky="e", padx=8, pady=6)
        self.entry_prov_direccion = ttk.Entry(frame_editar, width=50, font=("Segoe UI", 10))
        self.entry_prov_direccion.grid(row=2, column=1, sticky="w", pady=6)

        # Botones
        frame_botones = ttk.Frame(frame_editar)
        frame_botones.grid(row=3, column=0, columnspan=2, pady=(12, 0))

        tk.Button(frame_botones, text="Actualizar", font=("Segoe UI", 10, "bold"),
                  bg="#1a3c6e", fg="white", relief="flat", padx=14, pady=6,
                  cursor="hand2", command=self.actualizar_proveedor).pack(side="left", padx=6)

        tk.Button(frame_botones, text="Agregar Nuevo", font=("Segoe UI", 10, "bold"),
                  bg="#2e7d32", fg="white", relief="flat", padx=14, pady=6,
                  cursor="hand2", command=self.agregar_proveedor).pack(side="left", padx=6)

        tk.Button(frame_botones, text="Eliminar", font=("Segoe UI", 10, "bold"),
                  bg="#c62828", fg="white", relief="flat", padx=14, pady=6,
                  cursor="hand2", command=self.eliminar_proveedor).pack(side="left", padx=6)

        self.tree_proveedores.bind("<<TreeviewSelect>>", self.cargar_proveedor_seleccionado)

        ttk.Label(frame, text="Los cambios se guardan automáticamente en el archivo proveedores.json",
                  font=("Segoe UI", 9), foreground="#666").pack(anchor="w", pady=(12, 0))

    def actualizar_tree_proveedores(self):
        for item in self.tree_proveedores.get_children():
            self.tree_proveedores.delete(item)
        for prov in self.proveedores:
            self.tree_proveedores.insert("", "end", values=(
                prov.get("nombre", ""),
                prov.get("telefono", ""),
                prov.get("direccion", "")
            ))

    def cargar_proveedor_seleccionado(self, event=None):
        seleccionado = self.tree_proveedores.selection()
        if seleccionado:
            valores = self.tree_proveedores.item(seleccionado[0], "values")
            self.entry_prov_nombre.delete(0, tk.END)
            self.entry_prov_nombre.insert(0, valores[0])
            self.entry_prov_telefono.delete(0, tk.END)
            self.entry_prov_telefono.insert(0, valores[1])
            self.entry_prov_direccion.delete(0, tk.END)
            self.entry_prov_direccion.insert(0, valores[2])

    def actualizar_proveedor(self):
        seleccionado = self.tree_proveedores.selection()
        if not seleccionado:
            messagebox.showwarning("Aviso", "Seleccioná un proveedor de la lista")
            return

        nombre = self.entry_prov_nombre.get().strip()
        telefono = self.entry_prov_telefono.get().strip()
        direccion = self.entry_prov_direccion.get().strip()

        if not nombre:
            messagebox.showwarning("Aviso", "El nombre es obligatorio")
            return

        index = self.tree_proveedores.index(seleccionado[0])
        self.proveedores[index] = {
            "nombre": nombre,
            "telefono": telefono,
            "direccion": direccion
        }
        self.actualizar_tree_proveedores()
        self.guardar_proveedores()
        messagebox.showinfo("Éxito", "Proveedor actualizado y guardado")

    def agregar_proveedor(self):
        nombre = self.entry_prov_nombre.get().strip()
        telefono = self.entry_prov_telefono.get().strip()
        direccion = self.entry_prov_direccion.get().strip()

        if not nombre:
            messagebox.showwarning("Aviso", "El nombre es obligatorio")
            return

        self.proveedores.append({
            "nombre": nombre,
            "telefono": telefono,
            "direccion": direccion
        })
        self.actualizar_tree_proveedores()
        self.guardar_proveedores()

        self.entry_prov_nombre.delete(0, tk.END)
        self.entry_prov_telefono.delete(0, tk.END)
        self.entry_prov_direccion.delete(0, tk.END)
        messagebox.showinfo("Éxito", f"Proveedor \"{nombre}\" agregado y guardado")

    def eliminar_proveedor(self):
        seleccionado = self.tree_proveedores.selection()
        if not seleccionado:
            messagebox.showwarning("Aviso", "Seleccioná un proveedor para eliminar")
            return

        index = self.tree_proveedores.index(seleccionado[0])
        nombre = self.proveedores[index]["nombre"]

        if messagebox.askyesno("Confirmar", f"¿Eliminar al proveedor \"{nombre}\"?"):
            del self.proveedores[index]
            self.actualizar_tree_proveedores()
            self.guardar_proveedores()
            self.entry_prov_nombre.delete(0, tk.END)
            self.entry_prov_telefono.delete(0, tk.END)
            self.entry_prov_direccion.delete(0, tk.END)

    # ==================== PESTAÑA COTIZAR ====================
    def crear_tab_cotizar(self):
        canvas = tk.Canvas(self.tab_cotizar, bg="#ffffff", highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.tab_cotizar, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas, bg="#ffffff")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        container = self.scrollable_frame

        # ----- DATOS DEL CLIENTE -----
        frame_cliente = tk.Frame(container, bg="#ffffff")
        frame_cliente.pack(fill="x", padx=30, pady=(15, 5))

        tk.Label(frame_cliente, text="DATOS DEL CLIENTE", font=("Segoe UI", 11, "bold"),
                 bg="#ffffff", fg="#1a3c6e").grid(row=0, column=0, columnspan=6, sticky="w", pady=(0, 10))

        tk.Label(frame_cliente, text="Nº Cotización:", bg="#ffffff", font=("Segoe UI", 10)).grid(row=1, column=0, sticky="e", padx=5, pady=4)
        self.entry_nro_cotizacion = ttk.Entry(frame_cliente, width=10, font=("Segoe UI", 10), justify="center")
        self.entry_nro_cotizacion.grid(row=1, column=1, sticky="w", pady=4)
        self.entry_nro_cotizacion.insert(0, datetime.now().strftime("%H%M"))

        tk.Label(frame_cliente, text="Nombre y Apellido:", bg="#ffffff", font=("Segoe UI", 10)).grid(row=1, column=2, sticky="e", padx=5, pady=4)
        self.entry_nombre = ttk.Entry(frame_cliente, width=30, font=("Segoe UI", 10))
        self.entry_nombre.grid(row=1, column=3, sticky="w", pady=4)

        tk.Label(frame_cliente, text="Teléfono:", bg="#ffffff", font=("Segoe UI", 10)).grid(row=1, column=4, sticky="e", padx=5, pady=4)
        self.entry_telefono = ttk.Entry(frame_cliente, width=16, font=("Segoe UI", 10))
        self.entry_telefono.grid(row=1, column=5, sticky="w", pady=4)

        tk.Label(frame_cliente, text="Dirección:", bg="#ffffff", font=("Segoe UI", 10)).grid(row=2, column=0, sticky="e", padx=5, pady=4)
        self.entry_direccion = ttk.Entry(frame_cliente, width=42, font=("Segoe UI", 10))
        self.entry_direccion.grid(row=2, column=1, columnspan=3, sticky="w", pady=4)

        tk.Label(frame_cliente, text="Fecha:", bg="#ffffff", font=("Segoe UI", 10)).grid(row=2, column=4, sticky="e", padx=5, pady=4)
        self.entry_fecha = ttk.Entry(frame_cliente, width=16, font=("Segoe UI", 10))
        self.entry_fecha.grid(row=2, column=5, sticky="w", pady=4)
        self.entry_fecha.insert(0, datetime.now().strftime("%d/%m/%Y"))

        tk.Frame(container, bg="#1a3c6e", height=2).pack(fill="x", padx=30, pady=12)

        tk.Label(container, text="COTIZACIÓN DE MOSQUITERO", font=("Segoe UI", 16, "bold"),
                 bg="#ffffff", fg="#1a3c6e").pack(pady=(0, 10))

        # ----- MEDIDAS -----
        frame_medidas = tk.Frame(container, bg="#ffffff")
        frame_medidas.pack()

        tk.Label(frame_medidas, text="Ancho (m):", bg="#ffffff").grid(row=0, column=0, padx=8)
        self.entry_ancho = ttk.Entry(frame_medidas, width=9, font=("Segoe UI", 11), justify="center")
        self.entry_ancho.grid(row=0, column=1, padx=4)
        self.entry_ancho.insert(0, "1.00")

        tk.Label(frame_medidas, text="Alto (m):", bg="#ffffff").grid(row=0, column=2, padx=8)
        self.entry_alto = ttk.Entry(frame_medidas, width=9, font=("Segoe UI", 11), justify="center")
        self.entry_alto.grid(row=0, column=3, padx=4)
        self.entry_alto.insert(0, "1.00")

        tk.Label(frame_medidas, text="Cantidad:", bg="#ffffff").grid(row=0, column=4, padx=8)
        self.entry_cantidad = ttk.Entry(frame_medidas, width=7, font=("Segoe UI", 11), justify="center")
        self.entry_cantidad.grid(row=0, column=5, padx=4)
        self.entry_cantidad.insert(0, "1")

        tk.Label(frame_medidas, text="% Ganancia:", bg="#ffffff").grid(row=0, column=6, padx=8)
        self.entry_ganancia = ttk.Entry(frame_medidas, width=7, font=("Segoe UI", 11), justify="center")
        self.entry_ganancia.grid(row=0, column=7, padx=4)
        self.entry_ganancia.insert(0, "40")

        # Tipo de Perfil
        frame_perfil = tk.Frame(container, bg="#ffffff")
        frame_perfil.pack(pady=(12, 6))

        tk.Label(frame_perfil, text="Tipo de Perfil:", font=("Segoe UI", 10, "bold"),
                 bg="#ffffff", fg="#1a3c6e").pack(side="left", padx=(0, 15))

        self.var_perfil = tk.StringVar(value="Natural")

        for texto in ["Natural", "Blanco", "Color"]:
            tk.Radiobutton(frame_perfil, text=texto, variable=self.var_perfil, value=texto,
                           font=("Segoe UI", 10), bg="#ffffff", activebackground="#ffffff",
                           cursor="hand2").pack(side="left", padx=12)

        tk.Button(container, text="GENERAR COTIZACIÓN", font=("Segoe UI", 12, "bold"),
                  bg="#1a3c6e", fg="white", relief="flat", cursor="hand2",
                  padx=30, pady=9, command=self.calcular_cotizacion).pack(pady=12)

        # ===================== DETALLE =====================
        frame_detalle = tk.Frame(container, bg="#ffffff")
        frame_detalle.pack(fill="x", padx=40, pady=6)

        tk.Label(frame_detalle, text="DETALLE DE PRODUCTOS / SERVICIOS", font=("Segoe UI", 10, "bold"),
                 bg="#ffffff", fg="#1a3c6e").pack(anchor="w", pady=(0, 4))

        header = tk.Frame(frame_detalle, bg="#e8eef7")
        header.pack(fill="x", pady=(0, 3))

        tk.Label(header, text="DESCRIPCIÓN", font=("Segoe UI", 9, "bold"), bg="#e8eef7",
                 width=68, anchor="center").pack(side="left", padx=4, pady=5)
        tk.Label(header, text="IMPORTE $", font=("Segoe UI", 9, "bold"), bg="#e8eef7",
                 width=16, anchor="center").pack(side="right", padx=4, pady=5)

        self.lineas_desc = []
        self.lineas_importe = []

        for i in range(7):
            fila = tk.Frame(frame_detalle, bg="#ffffff")
            fila.pack(fill="x", pady=1)

            entry_desc = ttk.Entry(fila, width=70, font=("Segoe UI", 9))
            entry_desc.pack(side="left", padx=(0, 10))
            self.lineas_desc.append(entry_desc)

            entry_imp = ttk.Entry(fila, width=16, font=("Segoe UI", 9), justify="center")
            entry_imp.pack(side="right")
            entry_imp.bind("<FocusOut>", self.formatear_importe)
            entry_imp.bind("<Return>", self.formatear_importe)
            self.lineas_importe.append(entry_imp)

        # ===================== DESGLOSE =====================
        tk.Label(container, text="DESGLOSE DE MATERIALES", font=("Segoe UI", 10, "bold"),
                 bg="#ffffff", fg="#1a3c6e").pack(anchor="w", padx=40, pady=(14, 4))

        self.frame_desglose = tk.Frame(container, bg="#f8f9fc", bd=1, relief="solid")
        self.frame_desglose.pack(fill="x", padx=40, pady=4)

        self.label_desglose_izq = tk.Label(self.frame_desglose, text="El desglose aparecerá aquí",
                                           font=("Segoe UI", 9), bg="#f8f9fc", justify="left",
                                           anchor="nw", padx=15, pady=10)
        self.label_desglose_izq.pack(side="left", fill="both", expand=True)

        self.label_desglose_der = tk.Label(self.frame_desglose, text="",
                                           font=("Segoe UI", 9), bg="#f8f9fc", justify="left",
                                           anchor="nw", padx=15, pady=10)
        self.label_desglose_der.pack(side="left", fill="both", expand=True)

        # ===================== TOTALES =====================
        frame_totales = tk.Frame(container, bg="#ffffff")
        frame_totales.pack(pady=(16, 8))

        tk.Label(frame_totales, text="SUBTOTAL $", font=("Segoe UI", 11, "bold"),
                 bg="#ffffff", fg="#333").grid(row=0, column=0, sticky="e", padx=15, pady=4)
        self.entry_subtotal = ttk.Entry(frame_totales, width=16, font=("Segoe UI", 12), justify="center")
        self.entry_subtotal.grid(row=0, column=1, pady=4)
        self.entry_subtotal.bind("<KeyRelease>", self.actualizar_total)

        tk.Label(frame_totales, text="IVA 21% $", font=("Segoe UI", 11, "bold"),
                 bg="#ffffff", fg="#333").grid(row=1, column=0, sticky="e", padx=15, pady=4)
        self.entry_iva = ttk.Entry(frame_totales, width=16, font=("Segoe UI", 12), justify="center")
        self.entry_iva.grid(row=1, column=1, pady=4)
        self.entry_iva.bind("<KeyRelease>", self.actualizar_total)

        tk.Frame(frame_totales, bg="#1a3c6e", height=2).grid(row=2, column=0, columnspan=2, sticky="ew", pady=8)

        tk.Label(frame_totales, text="PRECIO FINAL $", font=("Segoe UI", 14, "bold"),
                 bg="#ffffff", fg="#1a3c6e").grid(row=3, column=0, sticky="e", padx=15, pady=6)
        self.label_total = tk.Label(frame_totales, text="0.00", font=("Segoe UI", 18, "bold"),
                                    bg="#ffffff", fg="#1a3c6e")
        self.label_total.grid(row=3, column=1, sticky="e", pady=6)

        # Botones PDF
        frame_botones = tk.Frame(container, bg="#ffffff")
        frame_botones.pack(pady=(10, 25))

        tk.Button(frame_botones, text="💾  GUARDAR PDF (completo)", font=("Segoe UI", 11, "bold"),
                  bg="#2e7d32", fg="white", relief="flat", cursor="hand2",
                  padx=20, pady=10, command=lambda: self.generar_pdf(incluir_desglose=True)).pack(side="left", padx=12)

        tk.Button(frame_botones, text="🖨  IMPRIMIR / PDF Cliente", font=("Segoe UI", 11, "bold"),
                  bg="#1565c0", fg="white", relief="flat", cursor="hand2",
                  padx=20, pady=10, command=lambda: self.generar_pdf(incluir_desglose=False)).pack(side="left", padx=12)

    def parsear_numero(self, texto):
        if not texto:
            return 0.0
        texto = texto.strip().replace("$", "").replace(" ", "").replace(",", "")
        try:
            return float(texto)
        except:
            return 0.0

    def formatear_importe(self, event=None):
        widget = event.widget
        texto = widget.get().strip()
        if not texto:
            self.actualizar_total()
            return
        limpio = texto.replace("$", "").replace(" ", "").replace(",", "")
        try:
            valor = float(limpio)
            widget.delete(0, tk.END)
            widget.insert(0, f"$ {valor:,.2f}")
        except:
            pass
        self.actualizar_total()

    def obtener_suma_lineas(self):
        total = 0.0
        for entry in self.lineas_importe:
            total += self.parsear_numero(entry.get())
        return total

    def calcular_cotizacion(self):
        try:
            ancho = float(self.entry_ancho.get().replace(",", "."))
            alto = float(self.entry_alto.get().replace(",", "."))
            cantidad = int(self.entry_cantidad.get())
            ganancia_pct = float(self.entry_ganancia.get().replace(",", ".")) / 100
            tipo_perfil = self.var_perfil.get()

            if ancho <= 0 or alto <= 0 or cantidad <= 0:
                messagebox.showerror("Error", "Las medidas y cantidad deben ser mayores a cero")
                return

            clave_perfil = f"Perfil Aluminio {tipo_perfil} (por metro)"
            if clave_perfil not in self.materiales:
                messagebox.showerror("Error", f"No se encontró el material: {clave_perfil}")
                return

            perimetro = 2 * (ancho + alto)
            metros_perfil = perimetro * (1 + self.desperdicio_perfil)
            m2_tela = (ancho * alto) * (1 + self.desperdicio_tela)
            lado_largo = max(ancho, alto)

            costo_perfil = metros_perfil * self.materiales[clave_perfil]
            costo_tela = m2_tela * self.materiales.get("Tela mosquitera (por m²)", 0)
            costo_cordon = perimetro * self.materiales.get("Cordón N60 (por metro)", 0)
            costo_escuadra = self.materiales.get("Escuadra Mosquitero (juego x4)", 0)
            costo_burlete = lado_largo * self.materiales.get("Burlete Lateral (por metro)", 0)
            costo_escuadra_est = self.materiales.get("Escuadra estriada 7mm (juego x4)", 0)
            costo_accesorios = self.materiales.get("Accesorios Varios", 0)
            costo_mano_obra = self.materiales.get("Mano de Obra / Instalación", 0)

            costo_unitario = (costo_perfil + costo_tela + costo_cordon + costo_escuadra +
                              costo_burlete + costo_escuadra_est + costo_accesorios + costo_mano_obra)

            subtotal_base = costo_unitario * cantidad * (1 + ganancia_pct)
            extras = self.obtener_suma_lineas()
            subtotal = subtotal_base + extras
            iva = subtotal * 0.21
            total = subtotal + iva

            self.ultimo_calculo = {
                "ancho": ancho, "alto": alto, "cantidad": cantidad,
                "tipo_perfil": tipo_perfil,
                "costo_perfil": costo_perfil * cantidad,
                "costo_tela": costo_tela * cantidad,
                "costo_cordon": costo_cordon * cantidad,
                "costo_escuadra": costo_escuadra * cantidad,
                "costo_burlete": costo_burlete * cantidad,
                "costo_escuadra_est": costo_escuadra_est * cantidad,
                "costo_accesorios": costo_accesorios * cantidad,
                "costo_mano_obra": costo_mano_obra * cantidad,
                "subtotal_base": subtotal_base,
                "extras": extras
            }

            desglose_izq = f"""Medida: {ancho:.2f} × {alto:.2f} m
Cantidad: {cantidad}  |  Perfil: {tipo_perfil}

Perfil Aluminio {tipo_perfil}   ${costo_perfil * cantidad:,.0f}
Tela mosquitera                ${costo_tela * cantidad:,.0f}
Cordón N60                     ${costo_cordon * cantidad:,.0f}
Escuadra Mosquitero            ${costo_escuadra * cantidad:,.0f}"""

            desglose_der = f"""
Burlete Lateral                ${costo_burlete * cantidad:,.0f}
Escuadra estriada 7mm          ${costo_escuadra_est * cantidad:,.0f}
Accesorios Varios              ${costo_accesorios * cantidad:,.0f}
Mano de Obra                   ${costo_mano_obra * cantidad:,.0f}"""

            self.label_desglose_izq.config(text=desglose_izq.strip())
            self.label_desglose_der.config(text=desglose_der.strip())

            self.entry_subtotal.delete(0, tk.END)
            self.entry_subtotal.insert(0, f"{subtotal:,.2f}")

            self.entry_iva.delete(0, tk.END)
            self.entry_iva.insert(0, f"{iva:,.2f}")

            self.label_total.config(text=f"{total:,.2f}")

        except ValueError:
            messagebox.showerror("Error", "Revisá que todos los campos tengan números válidos")

    def actualizar_total(self, event=None):
        try:
            if hasattr(self, "ultimo_calculo"):
                subtotal_base = self.ultimo_calculo.get("subtotal_base", 0)
            else:
                subtotal_base = self.parsear_numero(self.entry_subtotal.get())

            extras = self.obtener_suma_lineas()
            subtotal = subtotal_base + extras
            iva = subtotal * 0.21
            total = subtotal + iva

            self.entry_subtotal.delete(0, tk.END)
            self.entry_subtotal.insert(0, f"{subtotal:,.2f}")
            self.entry_iva.delete(0, tk.END)
            self.entry_iva.insert(0, f"{iva:,.2f}")
            self.label_total.config(text=f"{total:,.2f}")
        except:
            self.label_total.config(text="---")

    # ==================== PDF ====================
    def generar_pdf(self, incluir_desglose=True):
        if not hasattr(self, "ultimo_calculo"):
            messagebox.showwarning("Aviso", "Primero generá la cotización")
            return

        tipo = "completo" if incluir_desglose else "cliente"
        nro = self.entry_nro_cotizacion.get().strip() or "0000"
        nombre_default = f"Presupuesto_{nro}_{tipo}.pdf"

        ruta = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            initialfile=nombre_default,
            title="Guardar presupuesto como PDF"
        )
        if not ruta:
            return

        try:
            self._crear_pdf(ruta, incluir_desglose)
            messagebox.showinfo("Éxito", f"PDF guardado correctamente:\n{ruta}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar el PDF:\n{str(e)}")

    def _crear_pdf(self, ruta, incluir_desglose):
        doc = SimpleDocTemplate(ruta, pagesize=A4,
                                rightMargin=18*mm, leftMargin=18*mm,
                                topMargin=15*mm, bottomMargin=15*mm)

        styles = getSampleStyleSheet()
        estilo_titulo = ParagraphStyle('Titulo', parent=styles['Heading1'], fontSize=18, alignment=TA_CENTER,
                                       textColor=colors.HexColor("#1a3c6e"), spaceAfter=4, fontName="Helvetica-Bold")
        estilo_subtitulo = ParagraphStyle('Subtitulo', parent=styles['Normal'], fontSize=11, alignment=TA_CENTER,
                                          textColor=colors.HexColor("#333333"), spaceAfter=12)
        estilo_normal = ParagraphStyle('Normal2', parent=styles['Normal'], fontSize=10, leading=14)
        estilo_bold = ParagraphStyle('Bold', parent=styles['Normal'], fontSize=10, fontName="Helvetica-Bold")

        story = []
        calc = self.ultimo_calculo

        story.append(Paragraph("PRESUPUESTO", estilo_titulo))
        story.append(Paragraph(f"Nº {self.entry_nro_cotizacion.get()}   |   Fecha: {self.entry_fecha.get()}", estilo_subtitulo))
        story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#1a3c6e"), spaceAfter=10))

        datos_cliente = [
            [Paragraph("<b>DATOS DEL CLIENTE</b>", estilo_bold), ""],
            [Paragraph(f"<b>Nombre:</b> {self.entry_nombre.get()}", estilo_normal),
             Paragraph(f"<b>Teléfono:</b> {self.entry_telefono.get()}", estilo_normal)],
            [Paragraph(f"<b>Dirección:</b> {self.entry_direccion.get()}", estilo_normal), ""],
        ]
        tabla_cliente = Table(datos_cliente, colWidths=[95*mm, 75*mm])
        tabla_cliente.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#e8eef7")),
            ('SPAN', (0, 0), (-1, 0)),
            ('SPAN', (0, 2), (-1, 2)),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('BOX', (0, 0), (-1, -1), 0.8, colors.HexColor("#1a3c6e")),
        ]))
        story.append(tabla_cliente)
        story.append(Spacer(1, 6*mm))

        story.append(Paragraph(
            f"<b>Medidas:</b> {calc['ancho']:.2f} m × {calc['alto']:.2f} m &nbsp;&nbsp;|&nbsp;&nbsp; "
            f"<b>Cantidad:</b> {calc['cantidad']} &nbsp;&nbsp;|&nbsp;&nbsp; <b>Perfil:</b> {calc['tipo_perfil']}",
            estilo_normal
        ))
        story.append(Spacer(1, 4*mm))

        lineas_data = [["DESCRIPCIÓN", "IMPORTE ($)"]]
        for desc_entry, imp_entry in zip(self.lineas_desc, self.lineas_importe):
            desc = desc_entry.get().strip()
            imp = imp_entry.get().strip()
            if desc or imp:
                lineas_data.append([desc, imp if imp else ""])

        if len(lineas_data) > 1:
            story.append(Paragraph("<b>DETALLE</b>", estilo_bold))
            story.append(Spacer(1, 2*mm))
            tabla_lineas = Table(lineas_data, colWidths=[140*mm, 30*mm])
            tabla_lineas.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1a3c6e")),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('ALIGN', (1, 0), (1, -1), 'CENTER'),
                ('GRID', (0, 0), (-1, -1), 0.4, colors.grey),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ]))
            story.append(tabla_lineas)
            story.append(Spacer(1, 5*mm))

        if incluir_desglose:
            story.append(Paragraph("<b>DESGLOSE DE MATERIALES (uso interno)</b>", estilo_bold))
            story.append(Spacer(1, 2*mm))
            desglose_data = [
                ["Material", "Importe ($)"],
                [f"Perfil Aluminio {calc['tipo_perfil']}", f"${calc['costo_perfil']:,.0f}"],
                ["Tela mosquitera", f"${calc['costo_tela']:,.0f}"],
                ["Cordón N60", f"${calc['costo_cordon']:,.0f}"],
                ["Escuadra Mosquitero", f"${calc['costo_escuadra']:,.0f}"],
                ["Burlete Lateral", f"${calc['costo_burlete']:,.0f}"],
                ["Escuadra estriada 7mm", f"${calc['costo_escuadra_est']:,.0f}"],
                ["Accesorios Varios", f"${calc['costo_accesorios']:,.0f}"],
                ["Mano de Obra / Instalación", f"${calc['costo_mano_obra']:,.0f}"],
            ]
            tabla_desglose = Table(desglose_data, colWidths=[120*mm, 50*mm])
            tabla_desglose.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#455a64")),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                ('GRID', (0, 0), (-1, -1), 0.3, colors.grey),
                ('TOPPADDING', (0, 0), (-1, -1), 3),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor("#f5f5f5")),
            ]))
            story.append(tabla_desglose)
            story.append(Spacer(1, 5*mm))

        subtotal = self.parsear_numero(self.entry_subtotal.get())
        iva = self.parsear_numero(self.entry_iva.get())
        total = subtotal + iva

        totales_data = [
            ["Subtotal", f"$ {subtotal:,.2f}"],
            ["IVA 21%", f"$ {iva:,.2f}"],
            ["TOTAL", f"$ {total:,.2f}"],
        ]
        tabla_totales = Table(totales_data, colWidths=[120*mm, 50*mm])
        tabla_totales.setStyle(TableStyle([
            ('FONTNAME', (0, 2), (-1, 2), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 2), (-1, 2), 13),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('TEXTCOLOR', (0, 2), (-1, 2), colors.HexColor("#1a3c6e")),
            ('LINEABOVE', (0, 2), (-1, 2), 1.2, colors.HexColor("#1a3c6e")),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(tabla_totales)

        story.append(Spacer(1, 8*mm))
        story.append(HRFlowable(width="100%", thickness=0.8, color=colors.grey, spaceAfter=6))

        pie = "Documento de uso interno • Precios expresados en pesos argentinos" if incluir_desglose else \
              "Presupuesto para cliente • Válido por 15 días • Precios expresados en pesos argentinos"
        story.append(Paragraph(pie, ParagraphStyle('Pie', parent=styles['Normal'], fontSize=8,
                                                    alignment=TA_CENTER, textColor=colors.grey)))

        doc.build(story)

if __name__ == "__main__":
    root = tk.Tk()
    app = CotizadorMosquiteros(root)
    root.mainloop()