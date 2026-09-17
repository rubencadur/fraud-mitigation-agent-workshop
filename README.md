# Fraud Mitigation Agent Workshop

Repositorio incremental para construir un prototipo didáctico de prevención de fraude con Python, Google Colab, MongoDB Atlas Free y un LLM opcional.

## Especificación para continuidad

`PROJECT_SPECIFICATION.md` contiene la arquitectura, contratos, limitaciones, reglas de seguridad y protocolo para que otro desarrollador o LLM pueda continuar el proyecto.

## Rutas

### Ruta core

1. `notebooks/core/00_setup_workshop.ipynb` — <a href="https://colab.research.google.com/github/rubencadur/fraud-mitigation-agent-workshop/blob/main/notebooks/core/00_setup_workshop.ipynb" target="_blank" rel="noopener noreferrer"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"></a>
2. `notebooks/core/01_prompt_agent.ipynb` — <a href="https://colab.research.google.com/github/rubencadur/fraud-mitigation-agent-workshop/blob/main/notebooks/core/01_prompt_agent.ipynb" target="_blank" rel="noopener noreferrer"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"></a>
3. `notebooks/core/02_transaction_tool.ipynb` — <a href="https://colab.research.google.com/github/rubencadur/fraud-mitigation-agent-workshop/blob/main/notebooks/core/02_transaction_tool.ipynb" target="_blank" rel="noopener noreferrer"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"></a>
4. `notebooks/core/03_context_tools.ipynb` — <a href="https://colab.research.google.com/github/rubencadur/fraud-mitigation-agent-workshop/blob/main/notebooks/core/03_context_tools.ipynb" target="_blank" rel="noopener noreferrer"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"></a>
5. `notebooks/core/04_rule_tools.ipynb` — <a href="https://colab.research.google.com/github/rubencadur/fraud-mitigation-agent-workshop/blob/main/notebooks/core/04_rule_tools.ipynb" target="_blank" rel="noopener noreferrer"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"></a>
6. `notebooks/core/05_behavior_analysis.ipynb` — <a href="https://colab.research.google.com/github/rubencadur/fraud-mitigation-agent-workshop/blob/main/notebooks/core/05_behavior_analysis.ipynb" target="_blank" rel="noopener noreferrer"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"></a>
7. `notebooks/core/06_vector_search_manual.ipynb` — <a href="https://colab.research.google.com/github/rubencadur/fraud-mitigation-agent-workshop/blob/main/notebooks/core/06_vector_search_manual.ipynb" target="_blank" rel="noopener noreferrer"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"></a>
8. `notebooks/core/07_dynamic_scoring.ipynb` — <a href="https://colab.research.google.com/github/rubencadur/fraud-mitigation-agent-workshop/blob/main/notebooks/core/07_dynamic_scoring.ipynb" target="_blank" rel="noopener noreferrer"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"></a>
9. `notebooks/core/08_decision_engine.ipynb` — <a href="https://colab.research.google.com/github/rubencadur/fraud-mitigation-agent-workshop/blob/main/notebooks/core/08_decision_engine.ipynb" target="_blank" rel="noopener noreferrer"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"></a>

### Ruta avanzada

* `notebooks/advanced/06_automated_embeddings_atlas.ipynb` — <a href="https://colab.research.google.com/github/rubencadur/fraud-mitigation-agent-workshop/blob/main/notebooks/advanced/06_automated_embeddings_atlas.ipynb" target="_blank" rel="noopener noreferrer"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"></a>
* `notebooks/advanced/09_realtime_fraud_engine.ipynb` — <a href="https://colab.research.google.com/github/rubencadur/fraud-mitigation-agent-workshop/blob/main/notebooks/advanced/09_realtime_fraud_engine.ipynb" target="_blank" rel="noopener noreferrer"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"></a>
* `notebooks/advanced/10_evaluation_precision_recall.ipynb` — <a href="https://colab.research.google.com/github/rubencadur/fraud-mitigation-agent-workshop/blob/main/notebooks/advanced/10_evaluation_precision_recall.ipynb" target="_blank" rel="noopener noreferrer"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"></a>

## Seguridad

* Usar únicamente datos sintéticos.
* Guardar `MONGODB_URI` y cualquier `LLM_API_KEY` en Colab Secrets.
* No subir credenciales, archivos `.env` ni datos de clientes a GitHub.
* Usar un usuario de base de datos exclusivo para el workshop.
* Eliminar el cluster Free y las reglas temporales de red al terminar.

## Ejecutar en Google Colab

1. Abrir el notebook con el link "Open In Colab" correspondiente en la sección [Rutas](#rutas).
2. En `00_setup_workshop`, `REPO_URL` ya viene precargada con este repositorio; cámbiala solo si vas a trabajar sobre tu propio fork.
3. Crear en Colab Secret el valor `MONGODB_URI`.
4. Ejecutar primero `00_setup_workshop`.
5. Ejecutar los notebooks en orden.

Los notebooks funcionan con `MockLLMProvider` sin API externa. Si quieres probar un LLM real, `OpenAICompatibleProvider` acepta cualquier endpoint compatible con la API de OpenAI, así que puedes usar cualquier servicio, propio o de un tercero. Configura opcionalmente en Colab Secrets:

```text
LLM_PROVIDER=openai_compatible
LLM_API_KEY=...
LLM_BASE_URL=...
LLM_MODEL=...
```

### Opciones gratuitas

Estos tres servicios exponen un endpoint compatible con OpenAI y su capa gratuita no pide tarjeta de crédito al registrarse (verifica siempre los términos vigentes, ya que límites y modelos disponibles cambian con el tiempo):

| Proveedor | Obtener API key | `LLM_BASE_URL` | `LLM_MODEL` de ejemplo | Límites free tier (referencial) |
|---|---|---|---|---|
| **Groq Cloud** | [console.groq.com/keys](https://console.groq.com/keys) | `https://api.groq.com/openai/v1` | `llama-3.3-70b-versatile` | 30 req/min, 14 400 req/día |
| **NVIDIA NIM** (build.nvidia.com) | [build.nvidia.com](https://build.nvidia.com) | `https://integrate.api.nvidia.com/v1` | `meta/llama-3.1-70b-instruct` | 1000 créditos gratis al registrarte, 40 req/min |
| **Google AI Studio** (Gemini) | [aistudio.google.com/apikey](https://aistudio.google.com/apikey) | `https://generativelanguage.googleapis.com/v1beta/openai/` | `gemini-2.5-flash` | ~10-15 req/min según el modelo |

El scoring y la decisión final son determinísticos; el LLM solo interpreta, orquesta y explica.
