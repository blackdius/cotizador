import streamlit as st
from datetime import datetime
import json
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import io

# Configuración inicial de la página web
st.set_page_config(
    page_title="Cotizador Profesional de Mosquiteros",
    page_icon="🪟",
    layout="wide"
)

# Estilos CSS personalizados para dar aspecto profesional
st.markdown("""
    <style>
    .main { background-color: #f4f6f9; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #e8eef7;
        border-radius: 5px 5px 0px 0px;
        font-weight: bold;
        color: #1a3c6e;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1a3c6e !important;
        color: white !important;
    }
    </style>
""", unsafe_allow_html=True)

# Archivos de guardado local / persistencia en Streamlit
ARCHIVO_MATERIALES = "materiales.json"
ARCH_PROVEEDORES = "proveedores.json"

MATERIALES_DEFAULT = {
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

# Funciones de carga y guardado
def cargar_materiales():
    if os.path.exists(ARCHIVO_MATERIALES):
        try:
            with open(ARCHIVO_MATERIALES, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return MATERIALES_DEFAULT.copy()
    return MATERIALES_DEFAULT.copy()

def guardar_materiales(materiales):
    try:
        with open(ARCHIVO_MATERIALES, "w", encoding="utf-8") as f:
            json.dump(materiales, f, indent=4, ensure_ascii=False)
    except Exception as e:
        st.error(f"No se pudieron guardar los materiales: {e}")

def cargar_proveedores():
    if os.path.exists(ARCH_PROVEEDORES):
        try:
            with open(ARCH_PROVEEDORES, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []

def guardar_proveedores(proveedores):
    try:
        with open(ARCH_PROVEEDORES, "w", encoding="utf-8") as f:
            json.dump(proveedores, f, indent=4, ensure_ascii=False)
    except Exception as e:
        st.error(f"No se pudieron guardar los proveedores: {e}")

# Inicializar estados de sesión
if 'materiales' not in st.session_state:
    st.session_state.materiales = cargar_materiales()
if 'proveedores' not in st.session_state:
    st.session_state.proveedores = cargar_proveedores()

DESPERDICIO_PERFIL = 0.12
DESPERDICIO_TELA = 0.10

# Título principal
st.title("🪟 Cotizador Profesional de Mosquiteros")

# Solapas principales (Tabs)
tab_cotizar, tab_materiales, tab_proveedores = st.tabs(["  Cotizar / Factura  ", "  Materiales y Precios  ", "  Proveedores  "])

# ==================== PESTAÑA COTIZAR ====================
with tab_cotizar:
    st.subheader("Datos del Cliente")
    col1, col2, col3 = st.columns(3)
    with col1:
        nro_cotizacion = st.text_input("Nº Cotización", value=datetime.now().strftime("%H%M"))
        nombre_cliente = st.text_input("Nombre y Apellido")
    with col2:
        telefono_cliente = st.text_input("Teléfono")
        fecha_cotizacion = st.text_input("Fecha", value=datetime.now().strftime("%d/%m/%Y"))
    with col3:
        direccion_cliente = st.text_input("Dirección")

    st.markdown("---")
    st.subheader("Medidas y Parámetros")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        ancho = st.number_input("Ancho (m)", value=1.00, min_value=0.01, step=0.05)
    with c2:
        alto = st.number_input("Alto (m)", value=1.00, min_value=0.01, step=0.05)
    with c3:
        cantidad = st.number_input("Cantidad", value=1, min_value=1, step=1)
    with c4:
        ganancia_pct = st.number_input("% Ganancia", value=40.0, step=5.0)

    tipo_perfil = st.radio("Tipo de Perfil", ["Natural", "Blanco", "Color"], horizontal=True)

    st.markdown("### Servicios / Extras Opcionales")
    col_ext1, col_ext2 = st.columns(2)
    with col_ext1:
        desc_extra_1 = st.text_input("Descripción Extra 1", value="")
        imp_extra_1 = st.number_input("Importe Extra 1 ($)", value=0.0, step=100.0)
        desc_extra_2 = st.text_input("Descripción Extra 2", value="")
        imp_extra_2 = st.number_input("Importe Extra 2 ($)", value=0.0, step=100.0)
    with col_ext2:
        desc_extra_3 = st.text_input("Descripción Extra 3", value="")
        imp_extra_3 = st.number_input("Importe Extra 3 ($)", value=0.0, step=100.0)
        desc_extra_4 = st.text_input("Descripción Extra 4", value="")
        imp_extra_4 = st.number_input("Importe Extra 4 ($)", value=0.0, step=100.0)

    extras_totales = imp_extra_1 + imp_extra_2 + imp_extra_3 + imp_extra_4

    if st.button("🚀 Calcular Cotización", type="primary", use_container_width=True):
        clave_perfil = f"Perfil Aluminio {tipo_perfil} (por metro)"
        if clave_perfil not in st.session_state.materiales:
            st.error(f"No se encontró el material: {clave_perfil}")
        else:
            perimetro = 2 * (ancho + alto)
            metros_perfil = perimetro * (1 + DESPERDICIO_PERFIL)
            m2_tela = (ancho * alto) * (1 + DESPERDICIO_TELA)
            lado_largo = max(ancho, alto)

            mat = st.session_state.materiales
            costo_perfil = metros_perfil * mat[clave_perfil]
            costo_tela = m2_tela * mat.get("Tela mosquitera (por m²)", 0)
            costo_cordon = perimetro * mat.get("Cordón N60 (por metro)", 0)
            costo_escuadra = mat.get("Escuadra Mosquitero (juego x4)", 0)
            costo_burlete = lado_largo * mat.get("Burlete Lateral (por metro)", 0)
            costo_escuadra_est = mat.get("Escuadra estriada 7mm (juego x4)", 0)
            costo_accesorios = mat.get("Accesorios Varios", 0)
            costo_mano_obra = mat.get("Mano de Obra / Instalación", 0)

            costo_unitario = (costo_perfil + costo_tela + costo_cordon + costo_escuadra +
                              costo_burlete + costo_escuadra_est + costo_accesorios + costo_mano_obra)

            subtotal_base = costo_unitario * cantidad * (1 + (ganancia_pct / 100))
            subtotal = subtotal_base + extras_totales
            iva = subtotal * 0.21
            total = subtotal + iva

            # Guardar en session_state para mostrar resultados y generar PDF
            st.session_state.resultado = {
                "nro": nro_cotizacion, "nombre": nombre_cliente, "tel": telefono_cliente,
                "dir": direccion_cliente, "fecha": fecha_cotizacion,
                "ancho": ancho, "alto": alto, "cantidad": cantidad, "tipo_perfil": tipo_perfil,
                "costo_perfil": costo_perfil * cantidad,
                "costo_tela": costo_tela * cantidad,
                "costo_cordon": costo_cordon * cantidad,
                "costo_escuadra": costo_escuadra * cantidad,
                "costo_burlete": costo_burlete * cantidad,
                "costo_escuadra_est": costo_escuadra_est * cantidad,
                "costo_accesorios": costo_accesorios * cantidad,
                "costo_mano_obra": costo_mano_obra * cantidad,
                "extras_detalle": [(desc_extra_1, imp_extra_1), (desc_extra_2, imp_extra_2), 
                                   (desc_extra_3, imp_extra_3), (desc_extra_4, imp_extra_4)],
                "subtotal": subtotal, "iva": iva, "total": total
            }

    # Mostrar resultados si ya se calculó
    if 'resultado' in st.session_state:
        res = st.session_state.resultado
        st.markdown("---")
        st.subheader("📊 Resultado del Cálculo")
        
        col_res1, col_res2 = st.columns(2)
        with col_res1:
            st.markdown(f"**Medidas:** {res['ancho']:.2f} × {res['alto']} m | **Cant:** {res['cantidad']}")
            st.markdown(f"**Perfil:** Aluminio {res['tipo_perfil']}")
            st.markdown(f"- Perfil Aluminio: ${res['costo_perfil']:,.2f}")
            st.markdown(f"- Tela mosquitera: ${res['costo_tela']:,.2f}")
            st.markdown(f"- Cordón N60: ${res['costo_cordon']:,.2f}")
            st.markdown(f"- Escuadras: ${res['costo_escuadra']:,.2f}")
        with col_res2:
            st.markdown(f"- Burlete Lateral: ${res['costo_burlete']:,.2f}")
            st.markdown(f"- Escuadra estriada: ${res['costo_escuadra_est']:,.2f}")
            st.markdown(f"- Accesorios: ${res['costo_accesorios']:,.2f}")
            st.markdown(f"- Mano de Obra: ${res['costo_mano_obra']:,.2f}")

            st.info(f"### Subtotal: ${res['subtotal']:,.2f}  |  IVA (21%): ${res['iva']:,.2f}  |  TOTAL: ${res['total']:,.2f}")

        # Función para generar PDF en memoria
        def generar_pdf_bytes(incluir_desglose=True):
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=15*mm, leftMargin=15*mm, topMargin=15*mm, bottomMargin=15*mm)
            styles = getSampleStyleSheet()
            
            elements = []
            estilo_titulo = ParagraphStyle('Titulo', parent=styles['Heading1'], fontSize=16, textColor=colors.HexColor("#1a3c6e"), alignment=TA_CENTER)
            estilo_sub = ParagraphStyle('Sub', parent=styles['Normal'], fontSize=10, textColor=colors.HexColor("#333333"))
            
            elements.append(Paragraph(f"COTIZACIÓN DE MOSQUITEROS Nº {res['nro']}", estilo_titulo))
            elements.append(Spacer(1, 10))
            elements.append(Paragraph(f"<b>Cliente:</b> {res['nombre']} | <b>Tel:</b> {res['tel']} | <b>Fecha:</b> {res['fecha']}", estilo_sub))
            elements.append(Paragraph(f"<b>Dirección:</b> {res['dir']}", estilo_sub))
            elements.append(Spacer(1, 15))
            
            data = [["CANT.", "DESCRIPCIÓN", "IMPORTE"]]
            data.append([str(res['cantidad']), f"Mosquitero a medida ({res['ancho']}x{res['alto']}m) - Perfil {res['tipo_perfil']}", f"${res['subtotal']:,.2f}"])
            
            for desc, imp in res['extras_detalle']:
                if desc.strip() and imp > 0:
                    data.append(["1", desc, f"${imp:,.2f}"])
                    
            t = Table(data, colWidths=[40, 360, 100])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1a3c6e")),
                ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                ('ALIGN', (0,0), (0,-1), 'CENTER'),
                ('ALIGN', (2,0), (2,-1), 'RIGHT'),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0,0), (-1,0), 6),
                ('GRID', (0,0), (-1,-1), 0.5, colors.grey)
            ]))
            elements.append(t)
            elements.append(Spacer(1, 15))
            
            elements.append(Paragraph(f"<b>SUBTOTAL:</b> ${res['subtotal']:,.2f}", ParagraphStyle('Right', parent=styles['Normal'], alignment=TA_RIGHT)))
            elements.append(Paragraph(f"<b>IVA (21%):</b> ${res['iva']:,.2f}", ParagraphStyle('Right', parent=styles['Normal'], alignment=TA_RIGHT)))
            elements.append(Paragraph(f"<b>PRECIO FINAL:</b> ${res['total']:,.2f}", ParagraphStyle('Right', parent=styles['Heading2'], textColor=colors.HexColor("#1a3c6e"), alignment=TA_RIGHT)))
            
            doc.build(elements)
            buffer.seek(0)
            return buffer.getvalue()

        pdf_data = generar_pdf_bytes()
        st.download_button(
            label="📥 Descargar Cotización en PDF",
            data=pdf_data,
            file_name=f"Cotizacion_{res['nro']}.pdf",
            mime="application/pdf",
            use_container_width=True
        )

# ==================== PESTAÑA MATERIALES ====================
with tab_materiales:
    st.subheader("Gestión de Materiales y Precios")
    st.write("Modifica los precios o agrega nuevos materiales. Los cambios se guardan automáticamente.")

    # Mostrar tabla actual
    mat_items = list(st.session_state.materiales.items())
    for mat, precio in mat_items:
        col_m1, col_m2, col_m3 = st.columns([3, 2, 1])
        with col_m1:
            st.text(mat)
        with col_m2:
            nuevo_precio = st.number_input(f"Precio {mat}", value=float(precio), key=f"mat_{mat}", step=100.0)
            if nuevo_precio != precio:
                st.session_state.materiales[mat] = nuevo_precio
                guardar_materiales(st.session_state.materiales)
        with col_m3:
            if st.button("🗑️", key=f"del_{mat}"):
                del st.session_state.materiales[mat]
                guardar_materiales(st.session_state.materiales)
                st.rerun()

    st.markdown("---")
    st.subheader("Agregar Nuevo Material")
