import os
from pathlib import Path

from flask import Flask, render_template, request, url_for
from sentence_transformers import SentenceTransformer, util, InputExample, losses
from torch.utils.data import DataLoader
import pandas as pd
import numpy as np

app = Flask(__name__)

# 1) Directorio base del script
BASE_DIR = Path(__file__).resolve().parent

# 2) Rutas a recursos
EXCEL_PATH   = BASE_DIR / "datos.xlsx"
INDICES_PATH = BASE_DIR / "indices.txt"
MODEL_DIR    = BASE_DIR / "cartagena_finetuned_moderno"

# Subcarpeta DENTRO de `static/` donde están las imágenes
STATIC_IMGS_SUBFOLDER = "imagenes"

# 3) Carga/entrena el modelo
if not MODEL_DIR.exists():
    print("🔧 Entrenando modelo desde cero...")
    model = SentenceTransformer('msmarco-distilbert-base-tas-b')

    df = pd.read_excel(EXCEL_PATH, engine="openpyxl")
    ejemplos = [
        InputExample(texts=[row['x'], row['y']])
        for _, row in df.iterrows()
    ]
    loader = DataLoader(ejemplos, shuffle=True, batch_size=4)
    loss_fn = losses.MultipleNegativesRankingLoss(model)
    model.fit(
        train_objectives=[(loader, loss_fn)],
        epochs=3,
        warmup_steps=10,
        show_progress_bar=True
    )
    model.save(str(MODEL_DIR), safe_serialization=False)
else:
    print("✅ Modelo ya entrenado. Cargando desde disco...")
    model = SentenceTransformer(str(MODEL_DIR))

# 4) Lee documentos
with open(INDICES_PATH, "r", encoding="utf-8") as f:
    documents = [line.strip() for line in f if line.strip()]

# 5) Lista de nombres de archivos (en el mismo orden que `documents`)
imagenes = [
    "ciudad_amurallada.jpg",
    "cafe_del_mar.jpg",
    "bocagrande.jpg",
    "castillo_san_felipe.jpg",
    "la_cevicheria.jpg",
    "islas_rosario.jpg",
    "chiva_rumbera.jpg",
    "getsemani.jpg",
    "mercado_basurto.jpg",
    "la_popa.jpg",
    "aereo.jpg",
    "transca.jpg",
    "paseobahia.jpg",
    "utb.jpg",
    "udc.jpg",
    "serrezuela.jpg",
    "plazaboca.jpg",
    "museo.jpg",
    "manzana.jpg",
    "terminal.jpg"
]

# 6) Precompute embeddings de los documentos
doc_embeddings = model.encode(documents, convert_to_tensor=True)

@app.route("/", methods=["GET", "POST"])
def index():
    resultados = []

    if request.method == "POST":
        query = request.form.get("query", "").strip()
        if query:
            # Embedding de la consulta
            q_emb = model.encode(query, convert_to_tensor=True)
            scores = util.pytorch_cos_sim(q_emb, doc_embeddings)[0]
            top_k = 3
            top_idxs = np.argsort(-scores.cpu().numpy())[:top_k]

            # Verifica existencia en disco (debug)
            for idx in top_idxs:
                nombre = imagenes[idx]
                path = BASE_DIR / "static" / STATIC_IMGS_SUBFOLDER / nombre
                if not path.exists():
                    print(f"⚠️ No existe en disco: {path}")

            # Construye resultados con URL a static
            for i in top_idxs:
                resultados.append({
                    "texto": documents[i],
                    "imagen_url": url_for(
                        'static',
                        filename=f"{STATIC_IMGS_SUBFOLDER}/{imagenes[i]}"
                    ),
                    "score": f"{scores[i]:.4f}"
                })

    return render_template("index.html", resultados=resultados)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
