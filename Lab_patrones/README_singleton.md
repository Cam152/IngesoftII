# Singleton — sistema de configuración global

Implementación del patrón **Singleton** usando una metaclase en Python. El patrón garantiza que una clase tenga una única instancia durante toda la vida de la aplicación y proporciona un punto de acceso global a ella.

---

## Patrones involucrados

| Categoría  | Patrón    |
|------------|-----------|
| Creacional | Singleton |

---

## Estructura

```
SingletonMeta (metaclass)
    └── Config
            ├── get(clave)
            ├── set(clave, valor)
            ├── cargar_desde_dict(datos)
            └── cargar_desde_env()
```

### Clases

- `SingletonMeta` — metaclase que intercepta `__call__` y almacena la única instancia en `_instances`. Cualquier subclase hereda el comportamiento automáticamente.
- `Config` — clase concreta que usa `SingletonMeta`. Mantiene un diccionario de configuración con valores por defecto y métodos para leerlos, modificarlos y cargarlos desde distintas fuentes.

---

## Cómo funciona

```python
cfg1 = Config()
cfg2 = Config()

assert cfg1 is cfg2  # True — siempre la misma instancia
```

La primera llamada a `Config()` crea la instancia y la almacena en `SingletonMeta._instances`. Las llamadas siguientes devuelven esa misma instancia sin ejecutar `__init__` de nuevo.

---

## Uso

```python
# Inicialización única (normalmente al arrancar la app)
cfg = Config()
cfg.cargar_desde_dict({
    "app_name": "MiSistema",
    "debug": True,
    "timeout": 60,
})

# Desde cualquier otro módulo — mismo objeto, mismo estado
from config import Config
cfg = Config()
print(cfg.get("app_name"))   # MiSistema
print(cfg.get("timeout"))    # 60

# Variables de entorno (sobreescriben los valores del dict)
# DEBUG=false TIMEOUT=30 python main.py
cfg.cargar_desde_env()
```

### Métodos disponibles

| Método                      | Descripción                                        |
|-----------------------------|----------------------------------------------------|
| `get(clave, default=None)`  | Lee un valor de configuración                      |
| `set(clave, valor)`         | Escribe un valor en tiempo de ejecución            |
| `cargar_desde_dict(datos)`  | Carga múltiples valores desde un diccionario       |
| `cargar_desde_env()`        | Lee variables de entorno y las convierte al tipo correcto |

### Variables de entorno soportadas

| Variable         | Clave interna    | Tipo    |
|------------------|------------------|---------|
| `APP_NAME`       | `app_name`       | `str`   |
| `APP_VERSION`    | `version`        | `str`   |
| `DEBUG`          | `debug`          | `bool`  |
| `MAX_CONEXIONES` | `max_conexiones` | `int`   |
| `TIMEOUT`        | `timeout`        | `int`   |

---

## Ejecución

```bash
python singleton_config.py
```

Salida esperada:

```
[Servidor] Iniciando 'SistemaFacturación' con timeout=60s
[DB] Abriendo 10 conexiones máx.
[Logger] Nivel de log: DEBUG

Singleton funciona: ambas variables apuntan a la misma instancia.
```

---

## Cuándo usar este patrón

- Configuración global que debe cargarse una sola vez.
- Conexiones a servicios externos costosas de inicializar.
- Registros de log, cachés en memoria o gestores de estado compartido.

## Cuándo evitarlo

- Cuando el estado global dificulta las pruebas unitarias (considera inyección de dependencias en su lugar).
- Cuando se necesitan múltiples configuraciones en paralelo (p. ej. tests con distintos entornos).
