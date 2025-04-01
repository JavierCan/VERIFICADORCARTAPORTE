# main.py

import os
import base64
from io import BytesIO
import streamlit as st
from pdf_handler import process_uploaded_files, generar_zip

def main():
    st.title("📁 Verificación Cartaportes")

    uploaded_files = st.file_uploader(
        "📂 Sube archivos XML, ZIP o PDF (puedes seleccionar varios archivos):",
        type=["zip", "xml", "pdf"],
        accept_multiple_files=True
    )

    if st.button("🚀 Procesar archivos"):
        if uploaded_files:
            df_result, pdf_files = process_uploaded_files(uploaded_files)
            st.session_state.df_result = df_result
            st.session_state.pdf_files = pdf_files

            if not df_result.empty:
                st.success("✅ Datos procesados correctamente:")
            else:
                st.warning("⚠️ No se encontraron XML válidos en los archivos cargados.")
        else:
            st.warning("⚠️ Por favor sube archivos antes de procesar.")

    if "df_result" in st.session_state and not st.session_state.df_result.empty:
        st.dataframe(st.session_state.df_result)

        total_facturada = st.session_state.df_result["Cantidad Litros Facturada"].sum()
        total_transportada = st.session_state.df_result["Litros Transportada"].sum()

        st.write(f"**Suma total Facturada (todas las filas):** {total_facturada:.3f}")
        st.write(f"**Suma total Transportada (todas las filas):** {total_transportada:.3f}")

        combustibles_unicos = st.session_state.df_result["Combustible"].dropna().unique()
        if len(combustibles_unicos) > 0:
            combustible_seleccionado = st.selectbox("Filtrar suma por combustible:", options=combustibles_unicos)
            df_filtrado = st.session_state.df_result[st.session_state.df_result["Combustible"] == combustible_seleccionado]
            total_facturada_filtrada = df_filtrado["Cantidad Litros Facturada"].sum()
            total_transportada_filtrada = df_filtrado["Litros Transportada"].sum()
            st.write(f"Suma total Facturada para **{combustible_seleccionado}**: {total_facturada_filtrada:.3f}")
            st.write(f"Suma total Transportada para **{combustible_seleccionado}**: {total_transportada_filtrada:.3f}")
        else:
            st.info("No se encontraron valores de combustible para filtrar.")

        # Descarga de Excel
        excel_buffer = BytesIO()
        st.session_state.df_result.to_excel(excel_buffer, index=False)
        excel_buffer.seek(0)
        st.download_button(
            "📥 Descargar Excel (solo datos)",
            data=excel_buffer,
            file_name="datos_procesados.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        # Descarga de ZIP (Excel + PDFs asociados)
        zip_buffer = generar_zip(st.session_state.df_result, st.session_state.pdf_files)
        st.download_button(
            "📥 Descargar ZIP (Excel + PDFs asociados)",
            data=zip_buffer,
            file_name="datos_y_pdfs.zip",
            mime="application/zip"
        )

        st.markdown("---")
        st.subheader("📄 **Visualizar PDF asociado**")
        archivos_con_pdf = st.session_state.df_result[
            st.session_state.df_result['PDF Asociado'] != 'No encontrado'
        ]['PDF Asociado'].unique().tolist()

        if archivos_con_pdf:
            selected_pdf = st.selectbox("Selecciona un PDF para visualizar:", archivos_con_pdf)
            pdf_path = st.session_state.pdf_files[selected_pdf]

            if os.path.exists(pdf_path):
                with open(pdf_path, "rb") as f:
                    base64_pdf = base64.b64encode(f.read()).decode('utf-8')
                pdf_display = f'''
                    <iframe src="data:application/pdf;base64,{base64_pdf}"
                            width="100%" height="700"
                            type="application/pdf">
                    </iframe>
                '''
                st.markdown(pdf_display, unsafe_allow_html=True)
            else:
                st.error(f"❌ Archivo no encontrado: {pdf_path}")
        else:
            st.info("ℹ️ No hay PDFs asociados para visualizar.")

if __name__ == "__main__":
    main()
