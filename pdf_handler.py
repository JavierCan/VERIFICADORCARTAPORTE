# pdf_handler.py

import os
import shutil
import zipfile
from io import BytesIO
import pandas as pd
import streamlit as st
from xml_processor import process_file_based_on_format

def identify_pdf(xml_filename: str, pdf_files: dict) -> str:
    """
    Busca el PDF asociado a un archivo XML.
    """
    base_name = os.path.splitext(xml_filename)[0]
    pdf_name = base_name + ".pdf"
    return pdf_name if pdf_name in pdf_files else 'No encontrado'

def process_uploaded_files(uploaded_files) -> tuple[pd.DataFrame, dict]:
    """
    Procesa los archivos subidos:
      1. Crea un directorio temporal y extrae ZIPs.
      2. Recopila los archivos PDF y XML.
      3. Procesa cada XML y asocia su PDF correspondiente.
      4. Retorna un DataFrame con la información y un diccionario con los PDFs.
    """
    temp_dir = './temp_files'
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir)

    pdf_files = {}

    # Guardar archivos y extraer ZIPs
    for uploaded_file in uploaded_files:
        file_path = os.path.join(temp_dir, uploaded_file.name)
        with open(file_path, 'wb') as f:
            f.write(uploaded_file.getbuffer())

        if uploaded_file.name.lower().endswith('.pdf'):
            pdf_files[uploaded_file.name] = file_path
        elif uploaded_file.name.lower().endswith('.zip'):
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)

    # Detectar PDFs extraídos
    for root_dir, _, files in os.walk(temp_dir):
        for file in files:
            if file.lower().endswith('.pdf'):
                full_path = os.path.join(root_dir, file)
                pdf_files[file] = full_path

    # Recopilar archivos XML
    all_xml_files = []
    for root_dir, _, files in os.walk(temp_dir):
        for file in files:
            if file.lower().endswith('.xml'):
                all_xml_files.append(os.path.join(root_dir, file))
    all_xml_files = sorted(all_xml_files)

    all_data = []
    total_xml = len(all_xml_files)
    progress_bar = st.progress(0) if total_xml else None

    for idx, xml_path in enumerate(all_xml_files, start=1):
        try:
            data = process_file_based_on_format(xml_path)
            if data:
                xml_filename = os.path.basename(xml_path)
                data['XML_File'] = xml_filename
                data['PDF Asociado'] = identify_pdf(xml_filename, pdf_files)
                all_data.append(data)
        except Exception as e:
            print(f"Error procesando {xml_path}: {e}")

        if progress_bar:
            progress_bar.progress(idx / total_xml)

    df_result = pd.DataFrame(all_data)
    if not df_result.empty:
        df_result["Cantidad Litros Facturada"] = df_result["Cantidad Litros Facturada"].astype(float)
        df_result["Litros Transportada"] = df_result["Litros Transportada"].astype(float)
        df_result = df_result.sort_values(by="FechaEmision", na_position='last').reset_index(drop=True)
        df_result.drop(columns=["FechaEmision"], inplace=True)

    return df_result, pdf_files

def generar_zip(df: pd.DataFrame, pdf_files: dict) -> bytes:
    """
    Genera un ZIP en memoria que incluye:
      - Un archivo Excel con los datos procesados.
      - Los PDFs asociados.
    """
    buffer = BytesIO()
    with zipfile.ZipFile(buffer, 'w') as zf:
        excel_buffer = BytesIO()
        df.to_excel(excel_buffer, index=False)
        zf.writestr("datos_procesados.xlsx", excel_buffer.getvalue())
        for pdf_name in df['PDF Asociado'].unique():
            if pdf_name != 'No encontrado' and pdf_name in pdf_files:
                zf.write(pdf_files[pdf_name], arcname=pdf_name)
    buffer.seek(0)
    return buffer.getvalue()
