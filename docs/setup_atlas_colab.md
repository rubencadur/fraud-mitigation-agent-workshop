# Setup Atlas y Colab

1. Crear un proyecto separado en MongoDB Atlas.
2. Crear un cluster Free.
3. Crear un database user exclusivo.
4. Configurar Network Access según la política aprobada.
5. Copiar la cadena Python del driver.
6. Crear el secreto `MONGODB_URI` en Google Colab.
7. Abrir `00_setup_workshop.ipynb`.
8. Ejecutar el ping y la carga de datos sintéticos.

Si se usa una regla amplia de red temporalmente por las IP variables de Colab, limitar el tiempo, usar datos sintéticos y eliminarla al terminar.
