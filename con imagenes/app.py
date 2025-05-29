from flask import Flask, render_template, request
from sentence_transformers import SentenceTransformer, util, InputExample, losses
from torch.utils.data import DataLoader
import numpy as np
import pandas as pd
import os

app = Flask(__name__)

# Cargar modelo

if not os.path.exists("./cartagena_finetuned_moderno"):
    print("Entrenando modelo desde cero...")
    model = SentenceTransformer('msmarco-distilbert-base-tas-b')
    df = pd.read_excel("datos.xlsx", engine="openpyxl") 

# Convertir cada fila en un InputExample
    train_examples = [
    InputExample(texts=[row['x'], row['y']])
    for _, row in df.iterrows()
    
    ]
        
       
    train_dataloader = DataLoader(train_examples, shuffle=True, batch_size=4)
    train_loss = losses.MultipleNegativesRankingLoss(model)
    model.fit(
        train_objectives=[(train_dataloader, train_loss)],
        epochs=3,
        warmup_steps=10,
        show_progress_bar=True
    )
    model.save("./cartagena_finetuned_moderno", safe_serialization=False)
else:
    print("Modelo ya entrenado. Cargando desde disco...")

modelr = SentenceTransformer("./cartagena_finetuned_moderno")

# Leer documentos
with open("indices.txt", "r", encoding="utf-8") as f:
    documents = [line.strip() for line in f if line.strip()]

# Lista de imágenes correspondientes (mismo orden que documentos)
imagenes = [
    "imagenes/ciudad_amurallada.jpg",
    "imagenes/cafe_del_mar.jpg",
    "imagenes/bocagrande.jpg",
    "imagenes/castillo_san_felipe.jpg",
    "imagenes/la_cevicheria.jpg",
    "imagenes/islas_rosario.jpg",
    "imagenes/chiva_rumbera.jpg",
    "imagenes/getsemani.jpg",
    "imagenes/mercado_basurto.jpg",
    "imagenes/la_popa.jpg",
    "imagenes/aereo.jpg",
    "imagenes/transca.jpg",
    "imagenes/paseobahia.jpg",
    "imagenes/utb.jpg",
    "imagenes/udc.jpg",
    "imagenes/serrezuela.jpg",
    "imagenes/plazaboca.jpg",
    "imagenes/museo.jpg",
    "imagenes/manzana.jpg",
    "imagenes/terminal.jpg"]
# Calcular embeddings al inicio
doc_embeddings = modelr.encode(documents, convert_to_tensor=True)

@app.route("/", methods=["GET", "POST"])
def index():
    resultados = []
    if request.method == "POST":
        query = request.form.get("query")
        if query:
            query_embedding = modelr.encode(query, convert_to_tensor=True)
            scores = util.pytorch_cos_sim(query_embedding, doc_embeddings)[0]
            top_k = 3
            top_indices = np.argsort(-scores.cpu().numpy())[:top_k]

            resultados = [
                {
                    "texto": documents[i],
                    "imagen": imagenes[i],
                    "score": f"{scores[i]:.4f}"
                }
                for i in top_indices
            ]
    return render_template("index.html", resultados=resultados)

if __name__ == "__main__":
    app.run(debug=True)