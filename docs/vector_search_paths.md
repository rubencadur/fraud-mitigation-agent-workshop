# Rutas de embeddings

## Ruta manual

`06_vector_search_manual.ipynb` crea o usa embeddings precalculados y consulta un índice Vector Search. Es la ruta obligatoria.

## Ruta Automated Embeddings

`06_automated_embeddings_atlas.ipynb` prepara una definición de índice `autoEmbed` y consulta texto. Esta capacidad puede depender de la disponibilidad de la funcionalidad Preview en el cluster y región elegidos; el notebook incluye fallback a la ruta manual.
