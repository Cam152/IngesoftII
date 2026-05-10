import copy


class Prototype:
    """
    Clase base. Cualquier subclase hereda la capacidad de clonarse.
    """

    def clonar(self) -> "Prototype":
        return copy.deepcopy(self)


# Caso de uso: plantillas de notificaciones 

class Notificacion(Prototype):
    def __init__(self, tipo: str, asunto: str, cuerpo: str, destinatarios: list):
        self.tipo = tipo
        self.asunto = asunto
        self.cuerpo = cuerpo
        self.destinatarios = destinatarios  # lista mutable → deepcopy es clave

    def __repr__(self):
        return (
            f"Notificacion(tipo={self.tipo!r}, asunto={self.asunto!r}, "
            f"destinatarios={self.destinatarios})"
        )


if __name__ == "__main__":
    # 1. Plantilla base creada una sola vez
    plantilla_bienvenida = Notificacion(
        tipo="email",
        asunto="¡Bienvenido a MiApp!",
        cuerpo="Hola {nombre}, gracias por registrarte.",
        destinatarios=[],
    )

    # 2. Clonar y personalizar para cada usuario
    #    → no se toca la plantilla original
    for nombre, email in [
        ("Ana",   "ana@email.com"),
        ("Luis",  "luis@email.com"),
        ("Sofía", "sofia@email.com"),
    ]:
        notif = plantilla_bienvenida.clonar()
        notif.cuerpo = plantilla_bienvenida.cuerpo.replace("{nombre}", nombre)
        notif.destinatarios.append(email)
        print(notif)

    # 3. La plantilla original quedó intacta
    print(f"\nPlantilla original intacta: {plantilla_bienvenida.destinatarios}")

    # 4. Verificación: clon es una copia independiente, no el mismo objeto
    clon = plantilla_bienvenida.clonar()
    print(f"\nEs el mismo objeto: {clon is plantilla_bienvenida}")   # False
    print(f"Tiene el mismo contenido: {clon.asunto == plantilla_bienvenida.asunto}")  # True