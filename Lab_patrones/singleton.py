class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class Config(metaclass=SingletonMeta):
    """
    Configuración global de la aplicación.
    Se carga una sola vez y es accesible desde cualquier módulo.
    """

    def __init__(self):
        self._settings = {
            "app_name": "MiApp",
            "version": "1.0.0",
            "debug": False,
            "max_conexiones": 10,
            "timeout": 30,
        }

    def get(self, clave, default=None):
        return self._settings.get(clave, default)

    def set(self, clave, valor):
        self._settings[clave] = valor

    def cargar_desde_dict(self, datos: dict):
        self._settings.update(datos)

    def cargar_desde_env(self):
        import os
        mapping = {
            "APP_NAME":       ("app_name", str),
            "APP_VERSION":    ("version", str),
            "DEBUG":          ("debug", lambda v: v.lower() == "true"),
            "MAX_CONEXIONES": ("max_conexiones", int),
            "TIMEOUT":        ("timeout", int),
        }
        for env_key, (cfg_key, cast) in mapping.items():
            if env_key in os.environ:
                self._settings[cfg_key] = cast(os.environ[env_key])

    def __repr__(self):
        return f"Config({self._settings})"


# Simulación de uso en distintos módulos 

def modulo_servidor():
    cfg = Config()   # no crea una nueva instancia
    print(f"[Servidor] Iniciando '{cfg.get('app_name')}' "
          f"con timeout={cfg.get('timeout')}s")

def modulo_base_datos():
    cfg = Config()
    print(f"[DB] Abriendo {cfg.get('max_conexiones')} conexiones máx.")

def modulo_logger():
    cfg = Config()
    nivel = "DEBUG" if cfg.get("debug") else "INFO"
    print(f"[Logger] Nivel de log: {nivel}")


if __name__ == "__main__":
    # 1. Primera (y única) inicialización real
    cfg = Config()

    # 2. Sobreescribir valores, por ejemplo desde un archivo .env
    cfg.cargar_desde_dict({
        "app_name": "SistemaFacturación",
        "debug": True,
        "timeout": 60,
    })

    # 3. Otros módulos obtienen la MISMA instancia ya configurada
    modulo_servidor()
    modulo_base_datos()
    modulo_logger()

    # 4. Verificación explícita (igual que en el código original)
    cfg2 = Config()
    if id(cfg) == id(cfg2):
        print("\nSingleton funciona: ambas variables apuntan a la misma instancia.")
    else:
        print("\nFalló: instancias distintas.")