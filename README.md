# ether-agent-coder — Xolotl

Xolotl es un agente para ayudar a programar, con adaptadores iniciales para
`smolagents` (Python) y `Rig` (Rust), usando proveedores compatibles con la API
de OpenAI.

Su tarea es apoyar el desarrollo de software: entender repositorios, planear e
implementar cambios, depurar errores, escribir pruebas, revisar modificaciones
y explicar decisiones técnicas. El contrato detallado del agente está en
`xolotl/agent/README.md`.

## Inicio rápido

1. Instala `just`, `sops`, `age` y `uv`.
2. Genera o coloca tu clave privada age en `~/.age/ether-agent-coder-key.txt`:
   `mkdir -p ~/.age && age-keygen -o ~/.age/ether-agent-coder-key.txt`.
3. Ejecuta `just hooks-install`.
4. Ejecuta `just secrets-edit` para editar la configuración cifrada con `vi`.
5. Ejecuta `just smoke`.

Make se ocupa de construir, validar y probar. Just es la interfaz de tareas y
puede invocar Make; Make no invoca Just.
