import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io

# Função para garantir que um valor seja numérico
def ensure_numeric(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default

# Função para gerar diagrama do equipamento
def generate_equipment_diagram():
    fig, ax = plt.subplots(figsize=(10, 6))
    compressor_rect = plt.Rectangle((0.5, 1.5), 1.5, 2, fill=False, edgecolor='black', linewidth=2)
    ax.add_patch(compressor_rect)
    ax.text(1.25, 2.5, 'COMPRESSOR', ha='center', va='center', fontsize=12, fontweight='bold')
    ax.plot([0.3, 0.5], [2, 2], 'k-', linewidth=2)
    ax.plot([2.0, 2.7], [2, 2], 'k-', linewidth=2)
    cooler_rect = plt.Rectangle((2.7, 1.8), 1.2, 1.4, fill=False, edgecolor='blue', linewidth=2)
    ax.add_patch(cooler_rect)
    ax.text(3.3, 2.5, 'AIR COOLER', ha='center', va='center', fontsize=12, color='blue', fontweight='bold')
    ax.annotate('', xy=(0.3, 2), xytext=(-0.2, 2), arrowprops=dict(arrowstyle='<-', lw=2))
    ax.annotate('', xy=(2.3, 2), xytext=(2.6, 2), arrowprops=dict(arrowstyle='<-', lw=2))
    ax.set_xlim(0, 4)
    ax.set_ylim(0, 4)
    ax.axis('off')
    return fig

# Função para gerar PFD do processo
def generate_pfd():
    fig, ax = plt.subplots(figsize=(12, 6))
    reservoir_in = plt.Circle((1, 2), 0.3, fill=False, edgecolor='black', linewidth=2)
    ax.add_patch(reservoir_in)
    ax.text(1, 2, 'RESERV\nENTRADA', ha='center', va='center', fontsize=8)
    compressor = plt.Rectangle((2.5, 1.5), 1, 1, fill=False, edgecolor='black', linewidth=2)
    ax.add_patch(compressor)
    ax.text(3, 2, 'COMPRESSOR', ha='center', va='center', fontsize=10)
    cooler = plt.Rectangle((4.5, 1.7), 1, 0.6, fill=False, edgecolor='blue', linewidth=2)
    ax.add_patch(cooler)
    ax.text(5, 2, 'AIR COOLER', ha='center', va='center', fontsize=10, color='blue')
    reservoir_out = plt.Circle((7, 2), 0.3, fill=False, edgecolor='black', linewidth=2)
    ax.add_patch(reservoir_out)
    ax.text(7, 2, 'RESERV\nSAÍDA', ha='center', va='center', fontsize=8)
    ax.plot([1.3, 2.5], [2, 2], 'k-', linewidth=2)
    ax.plot([3.5, 4.5], [2, 2], 'k-', linewidth=2)
    ax.plot([5.5, 6.7], [2, 2], 'k-', linewidth=2)
    ax.annotate('', xy=(1.6, 2), xytext=(1.3, 2), arrowprops=dict(arrowstyle='<-', lw=2))
    ax.annotate('', xy=(4.3, 2), xytext=(3.6, 2), arrowprops=dict(arrowstyle='<-', lw=2))
    ax.annotate('', xy=(6.9, 2), xytext=(5.6, 2), arrowprops=dict(arrowstyle='<-', lw=2))
    ax.set_xlim(0, 8)
    ax.set_ylim(0, 4)
    ax.axis('off')
    return fig

# Função para calcular performance do compressor
def calculate_performance(inlet_press, discharge_press, rpm):
    pressure_ratio = (discharge_press / inlet_press) if inlet_press != 0 else None
    flow_rate = 5000 * (rpm / 1000)
    bhp = (discharge_press - inlet_press) * 0.05 * (rpm / 1000)
    return {'pressure_ratio': pressure_ratio, 'flow_rate': flow_rate, 'bhp': bhp}

# Função para gerar relatório em texto
from datetime import datetime
def generate_report(data):
    report = []
    report.append("RELATÓRIO DE PERFORMANCE DO COMPRESSOR")
    report.append(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    report.append("\nCONFIGURAÇÃO DO EQUIPAMENTO:")
    report.append(f"- Motor: {data['motor_type']}")
    report.append(f"- RPM: {data['rpm']}")
    report.append(f"- Derate: {data['derate']} %")
    report.append(f"- Potência Air Cooler: {data['air_cooler_power']} %")
    report.append(f"- Perda de Carga: {data['cooler_pressure_drop']} % por estágio")
    report.append(f"- Temperatura Saída: {data['cooler_temp']} °F por estágio")
    report.append(f"- Stroke: {data['stroke']}")
    report.append(f"- Nº Cilindros: {data['num_cylinders']}")
    report.append("\nRESULTADOS DE PERFORMANCE:")
    report.append(f"- Pressão de Entrada: {data['inlet_press']} {data['pressure_unit']}")
    report.append(f"- Pressão de Descarga: {data['discharge_press']} {data['pressure_unit']}")
    report.append(f"- Vazão: {data['flow_rate']:.2f} {data['flow_unit']}")
    report.append(f"- Potência Requerida (BHP): {data['performance']['bhp']:.2f}")
    return "\n".join(report)

# Função para exportar PDF
 def export_to_pdf(report):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, "RELATÓRIO DE PERFORMANCE DO COMPRESSOR")
    c.setFont("Helvetica", 12)
    y = height - 100
    for line in report.split("\n"):
        if y < 50:
            c.showPage()
            y = height - 50
        c.drawString(50, y, line)
        y -= 20
    c.save()
    buffer.seek(0)
    return buffer

# Main
def main():
    st.set_page_config(page_title="Aplicativo de Performance de Compressores", layout="wide")
    # Inicializa equipment_data
    if 'equipment_data' not in st.session_state:
        st.session_state.equipment_data = {
            'motor_type': 'Gás Natural', 'rpm': 1500, 'derate': 5.0, 'air_cooler_power': 4.0,
            'cooler_pressure_drop': 1.0, 'cooler_temp': 120.0, 'stroke': 200, 'num_cylinders': 4,
            'inlet_press': 100.0, 'discharge_press': 500.0, 'performance': None, 'cylinders': []
        }

    # Abas do Streamlit
    tabs = st.tabs(["Unidades de Medida","Configuração do Equipamento","Processo","Cálculo de Performance","Relatório","Multirun"] )

    # ABA 0
    with tabs[0]:
        st.header("Configuração de Unidades")
        pressure_unit = st.radio("Unidade de Pressão:", ["psig","kgf/cm²g"], key="pressure_unit")
        temp_unit = st.radio("Unidade de Temperatura:", ["°C","°F"], key="temp_unit")
        length_unit = st.radio("Unidade de Comprimento:", ["mm","polegadas"], key="length_unit")
        flow_unit = st.radio("Unidade de Vazão:", ["E3*m3/d","MMSCFD"], key="flow_unit")

    # ABA 1
    with tabs[1]:
        st.header("Configuração do Equipamento")
        col1, col2 = st.columns(2)
        with col1:
            motor_type = st.selectbox("Tipo de Motor:", ["Gás Natural","Elétrico"], key="motor_type")
            rpm = st.number_input("RPM:", value=st.session_state.equipment_data['rpm'], step=100, key="rpm")
            derate = st.slider("Derate (%):", 0.0, 20.0, value=st.session_state.equipment_data['derate'], key="derate")
            air_cooler_power = st.number_input("Potência Air Cooler (%):", value=st.session_state.equipment_data['air_cooler_power'], step=0.5, key="air_cooler_power")
        with col2:
            cooler_pressure_drop = st.number_input("Perda de Carga (%):", value=st.session_state.equipment_data['cooler_pressure_drop'], step=0.1, key="cooler_pressure_drop")
            cooler_temp = st.number_input("Temperatura Saída (°F):", value=st.session_state.equipment_data['cooler_temp'], step=5, key="cooler_temp")
        stroke = st.number_input("Stroke:", value=st.session_state.equipment_data['stroke'], step=10, key="stroke")
        num_cylinders = st.number_input("Nº Cilindros:", min_value=1, max_value=12, value=st.session_state.equipment_data['num_cylinders'], key="num_cylinders")
        if st.button("Adicionar Cilindro", key="add_cyl_btn"):
            st.session_state.equipment_data['cylinders'].append({'estagio':len(st.session_state.equipment_data['cylinders'])+1,'clearance':5.0,'sace':'Sim','vvcp':0.0})
        if st.session_state.equipment_data['cylinders']:
            st.write("Cilindros:")
            for i,c in enumerate(st.session_state.equipment_data['cylinders']): st.write(f"{i+1}: Estágio {c['estagio']}, Clearance {c['clearance']}%, SACE {c['sace']}, VVCP {c['vvcp']}%")
        if st.button("Gerar Diagrama do Equipamento", key="diag_btn"):
            st.pyplot(generate_equipment_diagram())

    # ABA Processo
    with tabs[2]:
        st.header("Processo")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Mostrar PFD", key="pfd_btn"): st.pyplot(generate_pfd())
        with col2:
            if st.session_state.equipment_data['performance']:
                st.metric("Potência Requerida (BHP)", f"{st.session_state.equipment_data['performance']['bhp']:.2f}")
            else:
                st.info("Calcule a performance primeiro.")

    # ABA Performance
    with tabs[3]:
        st.header("Cálculo de Performance")
        inlet_press = st.number_input("Pressão de Entrada:", value=st.session_state.equipment_data['inlet_press'], key="inlet_press")
        discharge_press = st.number_input("Pressão de Descarga:", value=st.session_state.equipment_data['discharge_press'], key="discharge_press")
        if st.button("Calcular Performance", key="perf_btn"):
            perf = calculate_performance(inlet_press, discharge_press, st.session_state.rpm)
            st.session_state.equipment_data.update({'inlet_press':inlet_press,'discharge_press':discharge_press,'performance':perf})
            st.success("Performance calculada.")
            st.experimental_rerun()

    # ABA Relatório
    with tabs[4]:
        st.header("Relatório de Performance")
        if st.session_state.equipment_data['performance']:
            data = dict(st.session_state.equipment_data)
            data.update({'pressure_unit':st.session_state.pressure_unit,'flow_unit':st.session_state.flow_unit})
            report = generate_report(data)
            st.text_area("Relatório", value=report, height=300)
            if st.button("Exportar PDF", key="export_pdf_btn"):
                buf = export_to_pdf(report)
                st.download_button("Baixar PDF", data=buf, file_name="relatorio.pdf", mime="application/pdf")
        else:
            st.warning("Calcule a performance antes.")

    # ABA Multirun
    with tabs[5]:
        st.header("Análise Paramétrica (Multirun)")
        min_inlet = st.number_input("PS Min:", value=100.0, key="min_inlet")
        max_inlet = st.number_input("PS Max:", value=500.0, key="max_inlet")
        min_discharge = st.number_input("PD Min:", value=200.0, key="min_discharge")
        max_discharge = st.number_input("PD Max:", value=800.0, key="max_discharge")
        min_rpm = st.number_input("RPM Min:", value=1000.0, key="min_rpm")
        max_rpm = st.number_input("RPM Max:", value=2000.0, key="max_rpm")
        if st.button("Executar Análise", key="multi_btn"):
            inlet_range = np.linspace(min_inlet, max_inlet, 10)
            discharge_range = np.linspace(min_discharge, max_discharge, 10)
            rpm_range = np.linspace(min_rpm, max_rpm, 5)
            flow_data, power_data = [], []
            for s in inlet_range:
                for d in discharge_range:
                    for r in rpm_range:
                        perf = calculate_performance(s,d,r)
                        flow_data.append((s,perf['flow_rate']))
                        power_data.append((s,perf['bhp']))
            fig, (ax1,ax2) = plt.subplots(1,2,figsize=(15,6))
            ax1.scatter([f[0] for f in flow_data],[f[1] for f in flow_data], alpha=0.6)
            ax1.set_title('PS x Vazão'); ax1.set_xlabel('PS'); ax1.set_ylabel('Vazão'); ax1.grid()
            ax2.scatter([p[0] for p in power_data],[p[1] for p in power_data], alpha=0.6)
            ax2.set_title('PS x Potência'); ax2.set_xlabel('PS'); ax2.set_ylabel('BHP'); ax2.grid()
            st.pyplot(fig)

if __name__ == "__main__":
    main()
