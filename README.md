# TourGuideBot – Recomendador Turístico Inteligente para Cartagena

**TourGuideBot: Smart Tourist Recommender for Cartagena**  
_Based on Natural Language Processing and BERT_  

**Autores:**  
- Juan David Colón Martínez  
- Harlem Hernández Rodríguez  
- Kaleth Benjumea Hernández  

**Afiliación:**  
Universidad Tecnológica de Bolívar, Cartagena, Colombia  

---

## Tabla de Contenidos

1. [Descripción del Proyecto](#descripción-del-proyecto)  
2. [Objetivos](#objetivos)  
3. [Metodología](#metodología)  
   - [Recolección de Datos](#recolección-de-datos)  
   - [Ajuste de BERT](#ajuste-de-bert)  
   - [Desarrollo del Backend (Flask)](#desarrollo-del-backend-flask)  
   - [Desarrollo del Frontend (HTML/CSS/JS)](#desarrollo-del-frontend-htmlcssjs)  
   - [Evaluación del Sistema](#evaluación-del-sistema)  
4. [Resultados Ejemplares](#resultados-ejemplares)  
5. [Estructura del Repositorio](#estructura-del-repositorio)  
6. [Instalación y Dependencias](#instalación-y-dependencias)  
7. [Preparación y Organización de Datos](#preparación-y-organización-de-datos)  
8. [Ejecución del Pipeline Completo](#ejecución-del-pipeline-completo)  
9. [Levantamiento de la Aplicación Web](#levantamiento-de-la-aplicación-web)  
10. [Uso de la Interfaz Web](#uso-de-la-interfaz-web)  
11. [Posibles Mejoras Futuras](#posibles-mejoras-futuras)  
12. [Autores y Créditos](#autores-y-créditos)  
13. [Licencia](#licencia)  

---

## Descripción del Proyecto

**TourGuideBot** es una plataforma web interactiva que ofrece recomendaciones turísticas personalizadas en la ciudad de Cartagena, Colombia. El usuario escribe libremente sus preferencias (“quiero un sitio con vista al mar y música en vivo”) y un modelo de **BERT** ajustado en un dataset propio interpreta esa consulta para sugerir lugares que cumplan con esas características. Toda la lógica de filtrado semántico corre en el backend (Flask), mientras que el frontend (HTML/CSS/JS con Bootstrap y AOS) brinda una experiencia “tipo chatbot” sencilla y atractiva.

---

## Objetivos

1. **Interpretar consultas en lenguaje natural** sin depender de menús o filtros estáticos.  
2. **Utilizar BERT** para capturar la intención y el contexto de la descripción del usuario.  
3. **Proporcionar recomendaciones turísticas** precisas y personalizadas, basadas en una base de datos local de lugares en Cartagena.  
4. **Crear una interfaz web intuitiva** que simule un chat, mostrando resultados con imágenes y puntuaciones de similitud.

---

## Metodología

### Recolección de Datos

- **Fuentes principales**:  
  1. Reseñas y descripciones en redes sociales (Instagram, TikTok, YouTube).  
  2. Información de Google Maps (ubicación, horarios, valoraciones).  
  3. Plataformas turísticas (TripAdvisor, Yelp) para enriquecer y validar atributos.  

- **Formato original**:  
  - `data/raw/datos.xlsx`: Hoja de cálculo con nombres, categorías, direcciones, puntuaciones y breves descripciones.  
  - `data/raw/indices.txt`: Texto plano con campos adicionales de identificación y orígenes.

### Ajuste de BERT

- Base: modelo preentrenado `msmarco-distilbert-base-tas-b` de SentenceTransformers.  
- Tarea: entrenar (fine-tuning) usando pares “consulta ↔ lugar” que reflejen descripciones turísticas en español.  
- Pérdida utilizada: `MultipleNegativesRankingLoss` para que el embedding de la consulta se acerque al embedding del lugar relevante.  
- Salida: `models/bert_model.pt` (modelo afinado listo para inferencia).

### Desarrollo del Backend (Flask)

- **`web/app.py`**:  
  - Define una ruta `/` que acepta `GET` y `POST`.  
  - Al recibir una consulta (`request.form["query"]`), calcula el embedding con el modelo BERT afinado.  
  - Compara semánticamente contra los embeddings precomputados de cada lugar (cargados desde `data/processed/`).  
  - Devuelve un JSON con los lugares ordenados por “score” de similitud.

- **Dependencias clave**:  
  - `flask`  
  - `pandas`  
  - `sentence_transformers` o `transformers + torch`  
  - `numpy`

### Desarrollo del Frontend (HTML/CSS/JS)

- **Plantilla principal**: `web/templates/index.html`  
  - Carrusel de imágenes (ciudad amurallada, Café del Mar, Bocagrande) con Bootstrap.  
  - Capa semitransparente para realzar textos sobre el slider.  
  - Buscador central (ligeramente desplazado a la izquierda) con un ícono de lupa.  
  - Flecha animada (CSS + AOS) que desplaza al usuario a los resultados.  
  - Tarjetas de resultados que muestran imagen, nombre del lugar y puntuación.

- **Estilos personalizados**:  
  - Variables de color definidas en CSS (`:root`).  
  - Tipografía moderna con Google Fonts (`Poppins`, `Playfair Display`).  
  - Hover effects en tarjetas (3D tilt y zoom en la imagen).  
  - Animaciones de entrada con AOS.

- **JavaScript ligero**: `web/static/script.js`  
  - Controla la animación del carrusel (opcional).  
  - Maneja la aparición del botón “Volver arriba.”  
  - Validación mínima del campo de búsqueda.

### Evaluación del Sistema

1. Creación de un conjunto de consultas reales en lenguaje natural (tanto literales como coloquiales).  
2. Comparación de la recomendación top-1 con la expectativa humana (p. ej., “quiero comer mariscos” → “La Cevichería”).  
3. Cálculo de métricas de “ranking accuracy” (top-1, top-3) en un pequeño set de validación manual.  
4. Ajuste de umbrales de similitud semántica para optimizar precisión vs. recall.

---

## Resultados Ejemplares

A continuación, tres consultas de ejemplo y su recomendación principal:

| **Consulta**                                        | **Lugar Recomendado**                                                                                                                                 |
|-----------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------|
| “Quiero comer mariscos con vista al mar”            | **La Cevichería**: Restaurante icónico especializado en mariscos, ubicado en la Ciudad Amurallada, reconocido por su frescura y ambiente caribeño.  |
| “Busco un sitio bohemio, música en vivo y cerveza”  | **Getsemaní** (varios bares): Barrio bohemio repleto de bares con música en vivo, grafitis, ambiente cultural y cerveza artesanal.                   |
| “Necesito ir al aeropuerto para un vuelo”           | **Aeropuerto Internacional Rafael Núñez**: Ubicado en Crespo, principal aeropuerto de Cartagena, con conexiones nacionales e internacionales.           |

---
