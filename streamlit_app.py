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
    """Gera um diagrama simples do equipamento"""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Desenho simplificado do compressor
    compressor_rect = plt.Rectangle((0.5, 1.5), 1.5, 2, fill=False, edgecolor='black', linewidth=2)
    ax.add_patch(compressor_rect)
    
    # Rótulos
    ax.text(1.25, 2.5, 'COMPRESSOR', ha='center', va='center', fontsize=12, fontweight='bold')
    
    # Tubulação de entrada
    ax.plot([1.3, 2.5], [2, 2], 'k-', linewidth=2)
    ax.plot([1.3, 2.5], [2.5, 2.5], 'k-', linewidth=2)
    
    # Tubulação de saída
    ax.plot([2, 2.5], [2, 2], 'k-', linewidth=2)
    ax.plot([2, 2.5], [2.5, 2.5], 'k-', linewidth=2)
    
    # Air Cooler
    cooler_rect = plt.Rectangle((2.7, 1.8), 1.2, 1.4, fill=False, edgecolor='blue', linewidth=2)
    ax.add_patch(cooler_rect)
    ax.text(3.3, 2.5, 'AIR COOLER', ha='center', va='center', fontsize=12, color='blue', fontweight='bold')
    
    # Setas de fluxo
    ax.annotate('', xy=(0.3, 2), xytext=(-0.2, 2),
                arrowprops=dict(arrowstyle='<-', lw=2))
    ax.annotate('', xy=(2.3, 2), xytext=(2.6, 2),
                arrowprops=dict(arrowstyle='<-', lw=2))
    
    ax.set_xlim(0, 4)
    ax.set_ylim(0, 4)
    ax.axis('off')
    
    return fig

# Função para gerar PFD do processo
def generate_pfd():
    """Gera um PFD simplificado do processo"""
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Componentes do PFD
    # Reservatório de entrada
    reservoir_in = plt.Circle((1, 2), 0.3, fill=False, edgecolor='black', linewidth=2)
    ax.add_patch(reservoir_in)
    ax.text(1, 2, 'RESERV\nENTRADA', ha='center', va='center', fontsize=8)
    
    # Compressor
    compressor = plt.Rectangle((2.5, 1.5), 1, 1, fill=False, edgecolor='black', linewidth=2)
    ax.add_patch(compressor)
    ax.text(3, 2, 'COMPRESSOR', ha='center', va='center', fontsize=10)
    
    # Air Cooler
    cooler = plt.Rectangle((4.5, 1.7), 1, 0.6, fill=False, edgecolor='blue', linewidth=2)
    ax.add_patch(cooler)
    ax.text(5, 2, 'AIR COOLER', ha='center', va='center', fontsize=10, color='blue')
    
    # Reservatório de saída
    reservoir_out = plt.Circle((7, 2), 0.3, fill=False, edgecolor='black', linewidth=2)
    ax.add_patch(reservoir_out)
    ax.text(7, 2, 'RESERV\nSAÍDA', ha='center', va='center', fontsize=8)
    
    # Conexões
    ax.plot([1.3, 2.5], [2, 2], 'k-', linewidth=2)
    ax.plot([3.5, 4.5], [2, 2], 'k-', linewidth=2)
    ax.plot([5.5, 6.7], [2, 2], 'k-', linewidth=2)
    
    # Setas de fluxo
    ax.annotate('', xy=(1.6, 2), xytext=(1.3, 2),
                arrowprops=dict(arrowstyle='<-', lw=2))
    ax.annotate('', xy=(4.3, 2), xytext=(3.6, 2),
                arrowprops=dict(arrowstyle='<-', lw=2))
    ax.annotate('', xy=(6.9, 2), xytext=(5.6, 2),
                arrowprops=dict(arrowstyle='<-', lw=2))
    
    ax.set_xlim(0, 8)
    ax.set_ylim(0, 4)
    ax.axis('off')
    
    return fig

# Função para calcular performance do compressor
def calculate_performance(inlet_press, discharge_press, rpm):
    """Calcula performance do compressor (simulado)"""
    # Evita divisão por zero
    if inlet_press == 0:
        return {'pressure_ratio': 0, 'flow_rate': 0, 'bhp': 0}
        
    # Cálculo fictício para demonstração
    pressure_ratio = discharge_press / inlet_press
    flow_rate = 5000 * (rpm / 1000)  # m³/h
    bhp = (discharge_press - inlet_press) * 0.05 * (rpm / 1000)
    
    return {
        'pressure_ratio': pressure_ratio,
        'flow_rate': flow_rate,
        'bhp': bhp
    }

# ==============================================================================
# FUNÇÃO ADICIONADA PARA CORRIGIR O ERRO
# ==============================================================================
def generate_report(data):
    """Gera uma string formatada com os dados do relatório."""
    
    # Acessa os dados de performance de forma segura
    performance = data.get('performance', {})
    
    report_string = f"""
RELATÓRIO DE PERFORMANCE DO COMPRESSOR
---------------------------------------

DADOS DO EQUIPAMENTO:
  - Tipo de Motor: {data.get('motor_type', 'N/A')}
  - RPM de Operação: {data.get('rpm', 0)} RPM
  - Derate Aplicado: {data.get('derate', 0)}%
  - Potência do Air Cooler: {data.get('air_cooler_power', 0)}%
  - Stroke: {data.get('stroke', 0)} mm
  - Número de Cilindros: {data.get('num_cylinders', 0)}

CONDIÇÕES DE PROCESSO:
  - Pressão de Entrada: {data.get('inlet_press', 0):.2f} {data.get('pressure_unit', 'N/A')}
  - Pressão de Descarga: {data.get('discharge_press', 0):.2f} {data.get('pressure_unit', 'N/A')}
  - Perda de Carga no Cooler: {data.get('cooler_pressure_drop', 0)}% por estágio
  - Temperatura de Saída do Cooler: {data.get('cooler_temp', 0)}°F por estágio

RESULTADOS DA PERFORMANCE:
  - Razão de Compressão: {performance.get('pressure_ratio', 0):.2f}
  - Vazão Volumétrica: {performance.get('flow_rate', 0):.2f} {data.get('flow_unit', 'N/A')}
  - Potência Requerida (BHP): {performance.get('bhp', 0):.2f} BHP
"""
    return report_string.strip()

# Função para gerar relatório em PDF
def export_to_pdf(report):
    """Exporta o relatório para PDF"""
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # Título
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, "RELATÓRIO DE PERFORMANCE DO COMPRESSOR")
    
    # Conteúdo
    c.setFont("Helvetica", 12)
    y_position = height - 100
    
    # Dividir o relatório em linhas
    lines = report.split('\n')
    for line in lines:
        if line.strip():
            c.drawString(50, y_position, line)
            y_position -= 20
            if y_position < 50:
                c.showPage()
                y_position = height - 50
    
    c.save()
    buffer.seek(0)
    return buffer

# Função principal do Streamlit
def main():
    st.set_page_config(page_title="Aplicativo de Performance de Compressores", layout="wide")
    
    # Inicializar estado da sessão com valores seguros
    if 'equipment_data' not in st.session_state:
        st.session_state.equipment_data = {
            'motor_type': 'Gás Natural',
            'rpm': 1500,
            'derate': 5,
            'air_cooler_power': 4.0,
            'cooler_pressure_drop': 1.0,
            'cooler_temp': 120,
            'stroke': 200,
            'num_cylinders': 4,
            'inlet_press': 100.0,
            'discharge_press': 500.0,
            'performance': None,
            'cylinders': []
        }
    
    # Abas principais
    tabs = st.tabs([
        "Unidades de Medida",
        "Configuração do Equipamento",
        "Processo",
        "Cálculo de Performance",
        "Relatório",
        "Multirun"
    ])
    
    with tabs[0]:  # Unidades de Medida
        st.header("Configuração de Unidades")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.subheader("Pressão")
            pressure_unit = st.radio(
                "Unidade:",
                ["psig", "kgf/cm²g"],
                key="pressure_unit"
            )
        
        with col2:
            st.subheader("Temperatura")
            temp_unit = st.radio(
                "Unidade:",
                ["°C", "°F"],
                key="temp_unit"
            )
        
        with col3:
            st.subheader("Comprimento")
            length_unit = st.radio(
                "Unidade:",
                ["mm", "polegadas"],
                key="length_unit"
            )
            
        st.subheader("Vazão Volumétrica")
        flow_unit = st.radio(
            "Unidade:",
            ["E3*m3/d", "MMSCFD"],
            key="flow_unit"
        )
    
    with tabs[1]:  # Configuração do Equipamento
        st.header("Configuração do Equipamento")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Motor")
            motor_type = st.selectbox(
                "Tipo de Motor:",
                ["Gás Natural", "Elétrico"],
                key="motor_type"
            )
            
            rpm = st.number_input(
                "RPM:",
                min_value=500,
                max_value=3000,
                value=int(st.session_state.equipment_data.get('rpm', 1500)),
                step=100,
                key="rpm"
            )
            
            derate = st.slider(
                "Derate (%):",
                min_value=0,
                max_value=20,
                value=int(st.session_state.equipment_data.get('derate', 5)),
                key="derate"
            )
            
            air_cooler_power = st.number_input(
                "Potência Air Cooler (%):",
                min_value=1.0,
                max_value=10.0,
                value=float(st.session_state.equipment_data.get('air_cooler_power', 4.0)),
                step=0.5,
                key="air_cooler_power"
            )
        
        with col2:
            st.subheader("Air Cooler")
            cooler_pressure_drop = st.number_input(
                "Perda de Carga (% por estágio):",
                min_value=0.1,
                max_value=5.0,
                value=float(st.session_state.equipment_data.get('cooler_pressure_drop', 1.0)),
                step=0.1,
                key="cooler_pressure_drop"
            )
            
            cooler_temp = st.number_input(
                "Temperatura Saída (°F por estágio):",
                min_value=80,
                max_value=200,
                value=int(st.session_state.equipment_data.get('cooler_temp', 120)),
                step=5,
                key="cooler_temp"
            )
        
        st.subheader("Compressor")
        col3, col4 = st.columns(2)
        
        with col3:
            stroke = st.number_input(
                "Stroke:",
                min_value=100,
                max_value=400,
                value=int(st.session_state.equipment_data.get('stroke', 200)),
                step=10,
                key="stroke"
            )
            
            num_cylinders = st.number_input(
                "Número de Cilindros:",
                min_value=1,
                max_value=12,
                value=int(st.session_state.equipment_data.get('num_cylinders', 4)),
                step=1,
                key="num_cylinders"
            )
        
        with col4:
            if st.button("Adicionar Cilindro"):
                new_cylinder = {
                    'estagio': len(st.session_state.equipment_data['cylinders']) + 1,
                    'clearance': 5.0,
                    'sace': 'Sim',
                    'vvcp': 0.0
                }
                st.session_state.equipment_data['cylinders'].append(new_cylinder)
        
        # Mostrar cilindros adicionados
        if st.session_state.equipment_data['cylinders']:
            st.write("Cilindros Adicionados:")
            for i, cyl in enumerate(st.session_state.equipment_data['cylinders']):
                st.write(f"Cilindro {i+1}: Estágio {cyl['estagio']}, Clearance {cyl['clearance']}%, SACE {cyl['sace']}, VVCP {cyl['vvcp']}%")
        
        # Botão para gerar diagrama
        if st.button("Gerar Diagrama do Equipamento"):
            fig = generate_equipment_diagram()
            st.pyplot(fig)
    
    with tabs[2]:  # Processo
        st.header("Processo")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("PFD do Compressor e Air Cooler")
            if st.button("Mostrar PFD"):
                fig = generate_pfd()
                st.pyplot(fig)
        
        with col2:
            st.subheader("Estimativa de Potência")
            if st.session_state.equipment_data['performance']:
                st.metric("Potência Requerida (BHP)", 
                          f"{st.session_state.equipment_data['performance']['bhp']:.2f}")
            else:
                st.info("Calcule a performance primeiro para ver a potência.")
    
    with tabs[3]:  # Cálculo de Performance
        st.header("Cálculo de Performance")
        
        col1, col2 = st.columns(2)
        
        with col1:
            inlet_press = st.number_input(
                "Pressão de Entrada:",
                min_value=50.0,
                max_value=1000.0,
                value=float(st.session_state.equipment_data.get('inlet_press', 100.0)),
                step=10.0,
                key="inlet_press_input" # Chave diferente para evitar conflito com session_state
            )
        
        with col2:
            discharge_press = st.number_input(
                "Pressão de Descarga:",
                min_value=inlet_press + 10,
                max_value=2000.0,
                value=float(st.session_state.equipment_data.get('discharge_press', 500.0)),
                step=10.0,
                key="discharge_press_input" # Chave diferente para evitar conflito
            )
        
        if st.button("Calcular Performance"):
            # Usar valores dos widgets, não do session_state diretamente
            current_rpm = ensure_numeric(st.session_state.get('rpm', 1500))

            performance = calculate_performance(
                inlet_press, 
                discharge_press, 
                current_rpm
            )
            st.session_state.equipment_data['performance'] = performance
            st.session_state.equipment_data['inlet_press'] = inlet_press
            st.session_state.equipment_data['discharge_press'] = discharge_press
            
            st.success("Performance calculada com sucesso!")
            
            # Atualizar dados para outras abas
            st.rerun()
    
    with tabs[4]:  # Relatório
        st.header("Relatório de Performance")
        
        if st.session_state.equipment_data.get('performance'):
            # Coletar todos os dados atuais do session_state
            report_data = {
                'motor_type': st.session_state.get('motor_type'),
                'rpm': st.session_state.get('rpm'),
                'derate': st.session_state.get('derate'),
                'air_cooler_power': st.session_state.get('air_cooler_power'),
                'cooler_pressure_drop': st.session_state.get('cooler_pressure_drop'),
                'cooler_temp': st.session_state.get('cooler_temp'),
                'stroke': st.session_state.get('stroke'),
                'num_cylinders': st.session_state.get('num_cylinders'),
                'inlet_press': st.session_state.equipment_data.get('inlet_press'),
                'discharge_press': st.session_state.equipment_data.get('discharge_press'),
                'pressure_unit': st.session_state.get('pressure_unit'),
                'flow_unit': st.session_state.get('flow_unit'),
                'performance': st.session_state.equipment_data.get('performance')
            }

            report = generate_report(report_data)
            
            st.text_area("Conteúdo do Relatório:", value=report, height=400)
            
            if st.button("Exportar PDF"):
                pdf_buffer = export_to_pdf(report)
                st.download_button(
                    label="Baixar Relatório PDF",
                    data=pdf_buffer,
                    file_name="relatorio_compressor.pdf",
                    mime="application/pdf"
                )
        else:
            st.warning("Calcule a performance primeiro para gerar o relatório.")
    
    with tabs[5]:  # Multirun
        st.header("Análise Paramétrica (Multirun)")
        
        # Usar colunas apenas se houver conteúdo para elas
        st.subheader("Parâmetros de Variação")
        
        min_inlet = st.number_input("Pressão de Sucção Mínima:", value=100.0)
        max_inlet = st.number_input("Pressão de Sucção Máxima:", value=500.0)
        min_discharge = st.number_input("Pressão de Descarga Mínima:", value=600.0)
        max_discharge = st.number_input("Pressão de Descarga Máxima:", value=1000.0)
        min_rpm = st.number_input("RPM Mínimo:", value=1000)
        max_rpm = st.number_input("RPM Máximo:", value=2000)
        
        if st.button("Executar Análise Multirun"):
            # Gerar dados para análise
            inlet_range = np.linspace(min_inlet, max_inlet, 10)
            discharge_range = np.linspace(min_discharge, max_discharge, 10)
            rpm_range = np.linspace(min_rpm, max_rpm, 5)
            
            results = []
            
            for suction in inlet_range:
                for discharge in discharge_range:
                    # Garantir que a descarga seja maior que a sucção
                    if discharge > suction:
                        for rpm_val in rpm_range:
                            performance = calculate_performance(suction, discharge, rpm_val)
                            results.append({
                                'suction': suction,
                                'discharge': discharge,
                                'rpm': rpm_val,
                                'flow_rate': performance['flow_rate'],
                                'bhp': performance['bhp']
                            })
            
            if not results:
                st.warning("Nenhum ponto de dados válido gerado. Verifique os intervalos de pressão.")
            else:
                # Criar gráficos
                fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
                
                df = pd.DataFrame(results)

                # Gráfico de vazão vs pressão de sucção
                ax1.scatter(df['suction'], df['flow_rate'], alpha=0.6, c=df['rpm'], cmap='viridis')
                ax1.set_xlabel('Pressão de Sucção')
                ax1.set_ylabel('Vazão Volumétrica')
                ax1.set_title('PS x Vazão')
                ax1.grid(True, linestyle='--', alpha=0.7)
                
                # Gráfico de potência vs pressão de sucção
                ax2.scatter(df['suction'], df['bhp'], alpha=0.6, c=df['rpm'], cmap='viridis')
                ax2.set_xlabel('Pressão de Sucção')
                ax2.set_ylabel('Potência Requerida (BHP)')
                ax2.set_title('PS x Potência')
                ax2.grid(True, linestyle='--', alpha=0.7)
                
                st.pyplot(fig)
                
                st.success("Análise concluída! Verifique os gráficos acima.")

if __name__ == "__main__":
    main()
