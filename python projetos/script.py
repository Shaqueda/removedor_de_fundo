import streamlit as st
from rembg import remove
from PIL import Image
from io import BytesIO
import zipfile

st.set_page_config(layout="wide", page_title="Removedor de Fundo em Lote")

st.title("✂️ Removedor de Fundo - Lote")
st.write("Faça upload de múltiplas imagens (10 ou mais) e baixe todas sem fundo de uma vez.")

# Upload de múltiplos arquivos
uploaded_files = st.file_uploader("Arraste suas imagens aqui", type=["png", "jpg", "jpeg", "webp"], accept_multiple_files=True)

if uploaded_files:
    st.write(f"---")
    st.write(f"📂 **{len(uploaded_files)} imagens identificadas.** Processando...")
    
    # Barra de progresso
    progress_bar = st.progress(0)
    
    # Lista para guardar os resultados em memória (para o ZIP)
    processed_images = []

    # Cria colunas para mostrar as imagens (preview)
    cols = st.columns(4) 
    
    for index, uploaded_file in enumerate(uploaded_files):
        try:
            # Ler a imagem original
            image = Image.open(uploaded_file)
            
            # Remover o fundo
            # Usamos BytesIO para manipular a imagem na memória RAM sem salvar no disco
            img_byte_arr = BytesIO()
            image.save(img_byte_arr, format=image.format)
            img_byte_arr = img_byte_arr.getvalue()
            
            output_data = remove(img_byte_arr)
            
            # Converter de volta para imagem PIL para mostrar na tela e salvar
            output_image = Image.open(BytesIO(output_data))
            
            # Adicionar à lista para o ZIP
            file_name = uploaded_file.name.split('.')[0] + "_sem_fundo.png"
            processed_images.append((file_name, output_image))
            
            # Atualizar barra de progresso
            progress_bar.progress((index + 1) / len(uploaded_files))
            
            # Mostrar na tela (apenas as 4 primeiras para não poluir)
            if index < 4:
                with cols[index]:
                    st.image(output_image, caption=f"Resultado: {uploaded_file.name}")

        except Exception as e:
            st.error(f"Erro ao processar {uploaded_file.name}: {e}")

    st.success("✅ Processamento concluído!")

    # --- Criar o arquivo ZIP para download ---
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zf:
        for file_name, img in processed_images:
            # Salvar imagem em buffer temporário
            img_buffer = BytesIO()
            img.save(img_buffer, format="PNG")
            # Adicionar ao zip
            zf.writestr(file_name, img_buffer.getvalue())

    # Botão de Download
    st.download_button(
        label="⬇️ Baixar Todas as Imagens (ZIP)",
        data=zip_buffer.getvalue(),
        file_name="imagens_sem_fundo.zip",
        mime="application/zip",
        use_container_width=True
    )