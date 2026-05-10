# Factory Method + Facade + Strategy — procesador de pagos

Combinación de tres patrones de diseño (creacional, estructural y de comportamiento) para construir un sistema de pagos extensible, donde cada patrón resuelve un problema distinto sin invadir el territorio de los demás.

---

## Patrones involucrados

| Categoría      | Patrón         | Responsabilidad                                        |
|----------------|----------------|--------------------------------------------------------|
| Creacional     | Factory Method | Decide qué procesador instanciar según el medio de pago |
| Estructural    | Facade         | Unifica la interfaz de múltiples pasarelas externas    |
| Comportamiento | Strategy       | Intercambia el algoritmo de cálculo de comisiones      |

---

## Estructura

```
EstrategiaComision (ABC)
    ├── ComisionFija          → valor fijo por transacción
    ├── ComisionPorcentaje    → porcentaje sobre el monto
    └── ComisionEscalonada    → porcentaje variable según tramos

_APIStripe  ─┐
_APIPayPal  ─┤→  FachadaPasarela  (cobrar_tarjeta / cobrar_paypal / cobrar_transferencia)
_APITransferencia ─┘

ProcesadorPago (ABC)
    ├── ProcesadorTarjeta      → usa fachada.cobrar_tarjeta()
    ├── ProcesadorPayPal       → usa fachada.cobrar_paypal()
    └── ProcesadorTransferencia → usa fachada.cobrar_transferencia()

ProcesadorFactory
    └── crear(medio, comision) → instancia el procesador correcto con la estrategia correcta
```

---

## Cómo funciona cada patrón

### Factory Method — `ProcesadorFactory.crear()`

El cliente nunca instancia procesadores directamente. La fábrica recibe el medio de pago y el nombre de la estrategia, y devuelve el objeto correcto:

```python
procesador = ProcesadorFactory.crear("tarjeta", comision="escalonada")
resultado  = procesador.procesar(250.00, token="tok_visa_4242")
```

Añadir un nuevo medio (p. ej. criptomonedas) solo requiere crear una nueva subclase de `ProcesadorPago` y registrarla en el diccionario `_procesadores` de la fábrica.

### Facade — `FachadaPasarela`

Stripe, PayPal y la API bancaria tienen interfaces completamente distintas. La fachada expone tres métodos uniformes y oculta toda la complejidad interna:

```python
# Lo que ve el procesador (simple)
resultado = self._fachada.cobrar_tarjeta(token, monto)

# Lo que ocurre dentro de la fachada (complejo)
self._stripe.autenticar("sk_live_xxx")
cargo = self._stripe.crear_cargo(token, int(monto * 100), "USD")
self._stripe.confirmar_pago(cargo["id"])
```

Si Stripe cambia su SDK mañana, solo cambia `FachadaPasarela.cobrar_tarjeta()` — nada más.

### Strategy — `EstrategiaComision`

El algoritmo de cálculo de comisión se inyecta al procesador en construcción y se puede cambiar sin tocar ninguna otra clase:

```python
# Comisión fija de $2.50 — independiente del monto
procesador = ProcesadorFactory.crear("transferencia", comision="fija")

# Comisión escalonada: 5% / 3% / 1.5% según tramos
procesador = ProcesadorFactory.crear("tarjeta", comision="escalonada")
```

---

## Estrategias de comisión disponibles

| Clave         | Clase                 | Comportamiento                             |
|---------------|-----------------------|--------------------------------------------|
| `fija`        | `ComisionFija`        | $2.50 por transacción, sin importar el monto |
| `porcentaje`  | `ComisionPorcentaje`  | 3.5% sobre el monto                        |
| `escalonada`  | `ComisionEscalonada`  | 5% (< $100) · 3% ($100–$999) · 1.5% (≥ $1000) |

---

## Medios de pago disponibles

| Clave           | Clase                    | Pasarela usada        |
|-----------------|--------------------------|-----------------------|
| `tarjeta`       | `ProcesadorTarjeta`      | Stripe                |
| `paypal`        | `ProcesadorPayPal`       | PayPal                |
| `transferencia` | `ProcesadorTransferencia`| API bancaria          |

---

## Uso

```python
# Tarjeta con comisión escalonada (por defecto)
procesador = ProcesadorFactory.crear("tarjeta")
resultado  = procesador.procesar(250.00, token="tok_visa_4242")

# PayPal con comisión porcentual
procesador = ProcesadorFactory.crear("paypal", comision="porcentaje")
resultado  = procesador.procesar(89.99, email="cliente@email.com")

# Transferencia con comisión fija
procesador = ProcesadorFactory.crear("transferencia", comision="fija")
resultado  = procesador.procesar(5000.00, cuenta="001-456-789")
```

Cada llamada a `procesar()` devuelve un diccionario con:

```python
{
    "referencia":   "ch_stripe_001",
    "estado":       "aprobado",
    "monto_bruto":  250.00,
    "comision":     7.50,
    "estrategia":   "Escalonada: 5% / 3% / 1.5%",
    "monto_neto":   242.50,
}
```

---

## Ejecución

```bash
python procesador_pagos.py
```

Salida esperada:

```
── Tarjeta de crédito ──────────────────────
  Referencia  : ch_stripe_001
  Estado      : aprobado
  Monto bruto : $250.00
  Comisión    : $7.50  (Escalonada: 5% / 3% / 1.5%)
  Monto neto  : $242.50

── PayPal ──────────────────────────────────
  Referencia  : PAY-pp-002
  Estado      : aprobado
  Monto bruto : $89.99
  Comisión    : $3.15  (Porcentaje: 3.5%)
  Monto neto  : $86.84

── Transferencia bancaria ──────────────────
  Referencia  : TRF-bank-003
  Estado      : liquidada
  Monto bruto : $5000.00
  Comisión    : $2.50  (Fija: $2.50)
  Monto neto  : $4997.50
```

---

## Cómo extender el sistema

### Agregar un nuevo medio de pago

```python
class ProcesadorCrypto(ProcesadorPago):
    def procesar(self, monto: float, **datos) -> dict:
        resultado = self._fachada.cobrar_crypto(datos["wallet"], monto)
        return self._resumen(monto, resultado)

# Registrar en la fábrica
ProcesadorFactory._procesadores["crypto"] = ProcesadorCrypto
```

### Agregar una nueva estrategia de comisión

```python
class ComisionCero(EstrategiaComision):
    def calcular(self, monto: float) -> float:
        return 0.0

    def descripcion(self) -> str:
        return "Sin comisión"

ProcesadorFactory._estrategias["gratis"] = ComisionCero()
```

Ninguno de los cambios anteriores toca el código existente — principio abierto/cerrado (OCP).

---

## Cuándo usar esta combinación

- Sistemas con múltiples proveedores externos intercambiables (pagos, envíos, notificaciones).
- Cuando el algoritmo de negocio (comisión, descuento, impuesto) debe variar independientemente del objeto que lo usa.
- Cuando se quiere aislar la complejidad de APIs externas del resto del sistema.
