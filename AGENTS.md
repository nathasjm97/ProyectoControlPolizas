# AGENTS.md

Este archivo proporciona instrucciones y contexto para agentes de IA que trabajan en el proyecto **ProyectoControlPolizas**.

## Estructura del proyecto

```
ProyectoControlPolizas/
├── AGENTS.md
└── Insumos_Control_Polizas/
    ├── Maestro_Clientes.xlsx
    └── polizas/
        ├── Poliza_AIS-2026-0001.pdf
        ├── Poliza_AIS-2026-0002.pdf
        ├── Poliza_AIS-2026-0003.pdf
        ├── Poliza_AIS-2026-0004.pdf
        ├── Poliza_AIS-2026-0005.pdf
        ├── Poliza_PCS-2026-0001.pdf
        ├── Poliza_PCS-2026-0002.pdf
        ├── Poliza_PCS-2026-0003.pdf
        ├── Poliza_PCS-2026-0004.pdf
        ├── Poliza_PCS-2026-0005.pdf
        ├── Poliza_PCS-2026-0006.pdf
        ├── Poliza_PCS-2026-0007.pdf
        ├── Poliza_PCS-2026-0008.pdf
        ├── Poliza_PCS-2026-0009.pdf
        ├── Poliza_SPC-2026-0001.pdf
        ├── Poliza_SPC-2026-0002.pdf
        ├── Poliza_SPC-2026-0003.pdf
        ├── Poliza_SPC-2026-0004.pdf
        ├── Poliza_SPC-2026-0005.pdf
        └── Poliza_SPC-2026-0006.pdf
```

## Configuración de Git

- **Usuario:** `nathasjm97`
- **Correo:** `nathasjm@gmail.com`
- Configuración establecida a nivel global (`--global`).

## Convenciones

- Los archivos de pólizas siguen el patrón: `Poliza_<TIPO>-<AÑO>-<NUMERO>.pdf`
  - Tipos: `AIS`, `PCS`, `SPC`
  - Ejemplo: `Poliza_AIS-2026-0001.pdf`
- El archivo `Maestro_Clientes.xlsx` contiene la base de clientes.

## Notas para agentes

- No hay repositorio Git inicializado todavía en este directorio (verifica con `git status` antes de hacer commits).
- Los archivos PDF en `polizas/` son pólizas de ejemplo para el control de pólizas.
- El proyecto se encuentra en carpeta con nombre con espacios (`Nathalie Curso\ProyectoControlPolizas`).
