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
    print(f"📥 Descargando archivo desde:\n{url}")
    gdown.download(url, output_path, quiet=False)
    print(f"✅ Archivo guardado en: {output_path}")
    
    
def get_feature_names_from_ct(ct):
    """
    ct: un ColumnTransformer ya .fit(...)
    Devuelve lista de nombres de columnas transformadas en el mismo orden
    que salen de ct.transform(X).
    Maneja pipelines, passthrough y steps que no implementan get_feature_names_out.
    """

    output_names = []

    for name, trans, cols in ct.transformers_:
        # si el transformer fue dropeado explícitamente
        if trans == 'drop':
            continue

        # caso passthrough (columnas que pasan directo)
        if trans == 'passthrough':
            # cols puede ser lista de nombres o índices
            if isinstance(cols, (list, tuple, np.ndarray)):
                output_names.extend(cols)
            else:
                output_names.append(cols)
            continue

        # si es un Pipeline
        if hasattr(trans, "steps"):
            # agarramos el último step del pipeline
            last_step_name, last_step = trans.steps[-1]

            # si el último step sabe dar nombres:
            if hasattr(last_step, "get_feature_names_out"):
                try:
                    names = last_step.get_feature_names_out(cols)
                except TypeError:
                    # algunos transformers no aceptan 'cols' como arg
                    names = last_step.get_feature_names_out()
                # prepend el nombre del transformer para evitar colisiones
                names = [f"{c}" for c in names]
                output_names.extend(names)
            else:
                # fallback: usa los nombres originales de las columnas
                if isinstance(cols, (list, tuple, np.ndarray)):
                    names = [f"{c}" for c in cols]
                    output_names.extend(names)
                else:
                    output_names.append(f"{cols}")

        # no es Pipeline (ej. directamente OneHotEncoder)
        else:
            if hasattr(trans, "get_feature_names_out"):
                try:
                    names = trans.get_feature_names_out(cols)
                except TypeError:
                    names = trans.get_feature_names_out()
                names = [f"{c}" for c in names]
                output_names.extend(names)
            else:
                # último fallback: solo usar cols crudas
                if isinstance(cols, (list, tuple, np.ndarray)):
                    names = [f"{c}" for c in cols]
                    output_names.extend(names)
                else:
                    output_names.append(f"{cols}")

    return output_names