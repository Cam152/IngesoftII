# Prototype — plantillas de notificaciones

Implementación del patrón **Prototype** en Python. El patrón permite clonar objetos existentes sin depender de su clase concreta, evitando el costo de construirlos desde cero cada vez.

---

## Patrones involucrados

| Categoría  | Patrón    |
|------------|-----------|
| Creacional | Prototype |

---

## Estructura

```
Prototype (base)
    └── Notificacion
            ├── tipo
            ├── asunto
            ├── cuerpo
            ├── destinatarios
            └── clonar()  ← heredado
```

### Clases

- `Prototype` — clase base con el método `clonar()` implementado usando `copy.deepcopy`. Cualquier subclase hereda la capacidad de clonarse sin código adicional.
- `Notificacion` — clase concreta que representa un mensaje con tipo, asunto, cuerpo y lista de destinatarios. Actúa como plantilla reutilizable.

---

## Cómo funciona

```python
# Se construye la plantilla una sola vez
plantilla = Notificacion(
    tipo="email",
    asunto="¡Bienvenido!",
    cuerpo="Hola {nombre}, gracias por registrarte.",
    destinatarios=[],
)

# Cada clon es independiente — deepcopy copia también los atributos mutables
clon = plantilla.clonar()
clon.destinatarios.append("ana@email.com")

assert clon is not plantilla              # objetos distintos
assert plantilla.destinatarios == []      # la plantilla no fue modificada
```

El punto crítico es `copy.deepcopy`: sin él, todos los clones compartirían la misma lista `destinatarios` y modificar una afectaría a todas las demás.

---

## Uso

```python
plantilla_bienvenida = Notificacion(
    tipo="email",
    asunto="¡Bienvenido a MiApp!",
    cuerpo="Hola {nombre}, gracias por registrarte.",
    destinatarios=[],
)

for nombre, email in usuarios:
    notif = plantilla_bienvenida.clonar()
    notif.cuerpo = plantilla_bienvenida.cuerpo.replace("{nombre}", nombre)
    notif.destinatarios.append(email)
    enviar(notif)
```

---

## Ejecución

```bash
python prototype_notificaciones.py
```

Salida esperada:

```
Notificacion(tipo='email', asunto='¡Bienvenido a MiApp!', destinatarios=['ana@email.com'])
Notificacion(tipo='email', asunto='¡Bienvenido a MiApp!', destinatarios=['luis@email.com'])
Notificacion(tipo='email', asunto='¡Bienvenido a MiApp!', destinatarios=['sofia@email.com'])

Plantilla original intacta: []

Es el mismo objeto: False
Tiene el mismo contenido: True
```

---

## `copy.copy` vs `copy.deepcopy`

| Método          | Qué copia                              | Atributos mutables        |
|-----------------|----------------------------------------|---------------------------|
| `copy.copy`     | El objeto — referencias a sus atributos | Compartidos con el original |
| `copy.deepcopy` | El objeto y todos sus atributos recursivamente | Independientes            |

Para objetos con listas, diccionarios u otros objetos mutables, siempre usar `deepcopy`.

---

## Cuándo usar este patrón

- Crear muchos objetos similares con pequeñas variaciones (plantillas de emails, documentos, configuraciones).
- Cuando construir un objeto desde cero es costoso (conexiones, parsing, cálculos pesados).
- Cuando se quiere preservar el estado de un objeto en un momento dado (snapshot).

## Cuándo evitarlo

- Objetos simples sin atributos mutables: una construcción directa es más clara.
- Cuando la copia profunda de objetos circulares o muy grandes tiene un costo prohibitivo.
