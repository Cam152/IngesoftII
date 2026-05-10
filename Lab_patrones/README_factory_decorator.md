# Factory Method + Decorator — sistema de reportes

Combinación de un patrón **creacional** y uno **estructural** para construir reportes flexibles: la fábrica decide qué tipo de reporte crear y los decoradores le agregan comportamiento en capas sin modificar las clases originales.

---

## Patrones involucrados

| Categoría   | Patrón         | Responsabilidad                              |
|-------------|----------------|----------------------------------------------|
| Creacional  | Factory Method | Decide qué clase concreta de reporte instanciar |
| Estructural | Decorator      | Agrega capas de comportamiento al reporte    |

---

## Estructura

```
Reporte (ABC)
    ├── ReportePDF
    ├── ReporteCSV
    └── ReporteHTML

ReporteFactory (ABC)
    ├── FactoryPDF      → crea ReportePDF
    ├── FactoryCSV      → crea ReporteCSV
    └── FactoryHTML     → crea ReporteHTML

ReporteDecorator (ABC, implementa Reporte)
    ├── ConEncabezado   → agrega cabecera corporativa
    ├── ConFirma        → agrega firma del autor
    └── ConCifrado      → cifra el contenido completo
```

### Clases

- `Reporte` — interfaz base con un único método `generar() -> str`.
- `ReportePDF / CSV / HTML` — implementaciones concretas del producto.
- `ReporteFactory` — clase base del factory; define `crear_reporte()` como método abstracto y `entregar()` como template method.
- `FactoryPDF / CSV / HTML` — fábricas concretas; implementan `crear_reporte()`.
- `ReporteDecorator` — decorador base que implementa `Reporte` y delega a un reporte interno. Misma interfaz que el producto: los decoradores son intercambiables con los reportes.
- `ConEncabezado / ConFirma / ConCifrado` — decoradores concretos que envuelven cualquier `Reporte` (incluso otro decorador).

---

## Cómo funciona

```python
# 1. La fábrica crea el producto base
reporte = FactoryPDF().crear_reporte("Ventas Q1")

# 2. Los decoradores se apilan: cada uno envuelve al anterior
reporte = ConEncabezado(reporte, empresa="Acme Corp")
reporte = ConFirma(reporte, autor="Ana García")

# 3. generar() recorre la cadena de decoradores de afuera hacia adentro
print(reporte.generar())
```

La clave es que `ReporteDecorator` implementa la misma interfaz `Reporte`. Esto permite:
- Pasar un decorador donde se espera un reporte.
- Apilar decoradores en cualquier orden y cantidad.
- Añadir nuevos decoradores sin modificar las clases existentes.

---

## Uso

```python
factories = {
    "pdf":  FactoryPDF(),
    "csv":  FactoryCSV(),
    "html": FactoryHTML(),
}

# PDF con encabezado y firma
reporte = factories["pdf"].crear_reporte("Ventas Q1 2025")
reporte = ConEncabezado(reporte, empresa="Acme Corp")
reporte = ConFirma(reporte, autor="Ana García")
print(reporte.generar())

# HTML con las tres capas
reporte = factories["html"].crear_reporte("Ventas Q1 2025")
reporte = ConEncabezado(reporte, empresa="Acme Corp")
reporte = ConFirma(reporte, autor="Sofía Ramos")
reporte = ConCifrado(reporte)
print(reporte.generar())
```

---

## Ejecución

```bash
python factory_decorator_reportes.py
```

Salida esperada:

```
── PDF con encabezado y firma ──
© Acme Corp — Confidencial
[PDF] Ventas Q1 2025
Firmado por: Ana García

── CSV con firma ──
[CSV] Ventas Q1 2025
Firmado por: Luis Pérez

── HTML con encabezado + firma + cifrado ──
[CIFRADO]
a9efa3d2c1b...
```

---

## División de responsabilidades

| Patrón         | Qué resuelve                           | Qué no toca                         |
|----------------|----------------------------------------|-------------------------------------|
| Factory Method | Qué clase concreta crear               | Cómo se equipa el reporte           |
| Decorator      | Qué comportamiento agregar y en qué orden | Cómo se crea el reporte base    |

---

## Cuándo usar esta combinación

- Múltiples variantes de un producto que además necesitan comportamiento opcional en capas.
- Cuando el número de combinaciones posibles (tipo × decorador × decorador…) haría inviable una jerarquía de clases por herencia.
- Sistemas de exportación, reportes, middlewares, pipelines de procesamiento.
