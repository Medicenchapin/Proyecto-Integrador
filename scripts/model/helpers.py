import os
import gdown

def download_data(url: str, output_path: str = "data/sale.csv"):
    """
    Descarga un archivo desde Google Drive u otra URL y lo guarda en la ruta especificada.
    
    Parámetros:
    ----------
    url : str
        URL del archivo (por ejemplo, link de gdown o Drive).
    output_path : str, opcional
        Ruta donde guardar el archivo. Por defecto: 'data/sale.csv'
    """
    # Crea la carpeta si no existe
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Descarga el archivo
    print(f"📥 Descargando archivo")
    gdown.download(url, output_path, quiet=False)
    print(f"✅ Archivo guardado en: {output_path}")