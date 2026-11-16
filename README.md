# AseguraTech Core — Plataforma de Emisión y Validación de Pólizas

Sistema basado en microservicios contenerizados sobre **Red Hat OpenShift** con integración y despliegue continuo mediante **GitHub Actions**.

## Arquitectura
- `cotizador-service` (Puerto 8081): Cálculo dinámico de primas automotrices con autoescalado horizontal (`HPA`).

## Flujo de Desarrollo
1. Crear una rama desde `main`: `git checkout -b feature/mi-cambio`
2. Realizar cambios y subir la rama: `git push -u origin feature/mi-cambio`
3. Abrir un **Pull Request** hacia `main` para validar la construcción de Docker y los manifiestos YAML.
4. Al aprobar el Pull Request, GitHub Actions despliega automáticamente en Red Hat OpenShift.
