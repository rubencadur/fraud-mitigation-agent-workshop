# Fraud Mitigation Agent Workshop

Repositorio incremental para construir un prototipo didáctico de prevención de fraude con Python, Google Colab, MongoDB Atlas Free y un LLM opcional.

## Especificación para continuidad

`PROJECT_SPECIFICATION.md` contiene la arquitectura, contratos, limitaciones, reglas de seguridad y protocolo para que otro desarrollador o LLM pueda continuar el proyecto.

## Rutas

### Ruta core de 3 horas

1. `notebooks/core/00_setup_workshop.ipynb` — [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/rubencadur/fraud-mitigation-agent-workshop/blob/main/notebooks/core/00_setup_workshop.ipynb)
2. `notebooks/core/01_prompt_agent.ipynb` — [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/rubencadur/fraud-mitigation-agent-workshop/blob/main/notebooks/core/01_prompt_agent.ipynb)
3. `notebooks/core/02_transaction_tool.ipynb` — [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/rubencadur/fraud-mitigation-agent-workshop/blob/main/notebooks/core/02_transaction_tool.ipynb)
4. `notebooks/core/03_context_tools.ipynb` — [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/rubencadur/fraud-mitigation-agent-workshop/blob/main/notebooks/core/03_context_tools.ipynb)
5. `notebooks/core/04_rule_tools.ipynb` — [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/rubencadur/fraud-mitigation-agent-workshop/blob/main/notebooks/core/04_rule_tools.ipynb)
6. `notebooks/core/05_behavior_analysis.ipynb` — [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/rubencadur/fraud-mitigation-agent-workshop/blob/main/notebooks/core/05_behavior_analysis.ipynb)
7. `notebooks/core/06_vector_search_manual.ipynb` — [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/rubencadur/fraud-mitigation-agent-workshop/blob/main/notebooks/core/06_vector_search_manual.ipynb)
8. `notebooks/core/07_dynamic_scoring.ipynb` — [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/rubencadur/fraud-mitigation-agent-workshop/blob/main/notebooks/core/07_dynamic_scoring.ipynb)
9. `notebooks/core/08_decision_engine.ipynb` — [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/rubencadur/fraud-mitigation-agent-workshop/blob/main/notebooks/core/08_decision_engine.ipynb)

### Ruta avanzada

* `notebooks/advanced/06_automated_embeddings_atlas.ipynb` — [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/rubencadur/fraud-mitigation-agent-workshop/blob/main/notebooks/advanced/06_automated_embeddings_atlas.ipynb)
* `notebooks/advanced/09_realtime_fraud_engine.ipynb` — [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/rubencadur/fraud-mitigation-agent-workshop/blob/main/notebooks/advanced/09_realtime_fraud_engine.ipynb)
* `notebooks/advanced/10_evaluation_precision_recall.ipynb` — [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/rubencadur/fraud-mitigation-agent-workshop/blob/main/notebooks/advanced/10_evaluation_precision_recall.ipynb)

## Seguridad

* Usar únicamente datos sintéticos.
* Guardar `MONGODB_URI` y cualquier `LLM_API_KEY` en Colab Secrets.
* No subir credenciales, archivos `.env` ni datos de clientes a GitHub.
* Usar un usuario de base de datos exclusivo para el workshop.
* Eliminar el cluster Free y las reglas temporales de red al terminar.

## Ejecutar en Google Colab

1. Abrir el notebook con el link "Open In Colab" correspondiente en la sección [Rutas](#rutas).
2. En `00_setup_workshop`, configurar `REPO_URL` con la URL del repositorio.
3. Crear en Colab Secret el valor `MONGODB_URI`.
4. Ejecutar primero `00_setup_workshop`.
5. Ejecutar los notebooks en orden.

Los notebooks funcionan con `MockLLMProvider` sin API externa. Para probar un LLM compatible con OpenAI, configurar opcionalmente:

```text
LLM_PROVIDER=openai_compatible
LLM_API_KEY=...
LLM_BASE_URL=...
LLM_MODEL=...
```

El scoring y la decisión final son determinísticos; el LLM solo interpreta, orquesta y explica.
