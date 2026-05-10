from abc import ABC, abstractmethod


# ═══════════════════════════════════════════════════════
#  STRATEGY — algoritmos de comisión intercambiables
# ═══════════════════════════════════════════════════════

class EstrategiaComision(ABC):
    @abstractmethod
    def calcular(self, monto: float) -> float:
        pass

    @abstractmethod
    def descripcion(self) -> str:
        pass


class ComisionFija(EstrategiaComision):
    def __init__(self, valor: float):
        self.valor = valor

    def calcular(self, monto: float) -> float:
        return self.valor

    def descripcion(self) -> str:
        return f"Fija: ${self.valor:.2f}"


class ComisionPorcentaje(EstrategiaComision):
    def __init__(self, porcentaje: float):
        self.porcentaje = porcentaje

    def calcular(self, monto: float) -> float:
        return round(monto * self.porcentaje / 100, 2)

    def descripcion(self) -> str:
        return f"Porcentaje: {self.porcentaje}%"


class ComisionEscalonada(EstrategiaComision):
    """Comisión variable según el monto de la transacción."""

    def calcular(self, monto: float) -> float:
        if monto < 100:
            return round(monto * 0.05, 2)   # 5% para montos pequeños
        elif monto < 1000:
            return round(monto * 0.03, 2)   # 3% para montos medianos
        else:
            return round(monto * 0.015, 2)  # 1.5% para montos grandes

    def descripcion(self) -> str:
        return "Escalonada: 5% / 3% / 1.5%"


# ═══════════════════════════════════════════════════════
#  FACADE — oculta la complejidad de pasarelas externas
# ═══════════════════════════════════════════════════════

class _APIStripe:
    """Simula el SDK real de Stripe (complejo e interno)."""
    def autenticar(self, api_key: str): pass
    def crear_cargo(self, token: str, monto: int, moneda: str) -> dict:
        return {"id": "ch_stripe_001", "status": "succeeded", "amount": monto}
    def confirmar_pago(self, charge_id: str) -> bool:
        return True


class _APIPayPal:
    """Simula el SDK real de PayPal (distinta interfaz)."""
    def login(self, client_id: str, secret: str): pass
    def ejecutar_pago(self, email: str, amount: float) -> dict:
        return {"payment_id": "PAY-pp-002", "state": "approved", "amount": amount}
    def capturar(self, payment_id: str) -> dict:
        return {"capture_id": "CAP-pp-002", "status": "completed"}


class _APITransferencia:
    """Simula una API bancaria (otra interfaz totalmente distinta)."""
    def conectar(self, banco: str, cuenta: str): pass
    def iniciar_transferencia(self, origen: str, destino: str, valor: float) -> str:
        return "TRF-bank-003"
    def verificar_estado(self, ref: str) -> str:
        return "LIQUIDADA"


class FachadaPasarela:
    """
    Facade: una interfaz uniforme para tres sistemas externos
    con APIs completamente distintas.
    """

    def __init__(self):
        self._stripe = _APIStripe()
        self._paypal = _APIPayPal()
        self._banco  = _APITransferencia()

    def cobrar_tarjeta(self, token: str, monto: float) -> dict:
        self._stripe.autenticar("sk_live_xxx")
        cargo = self._stripe.crear_cargo(token, int(monto * 100), "USD")
        self._stripe.confirmar_pago(cargo["id"])
        return {"referencia": cargo["id"], "estado": "aprobado", "monto": monto}

    def cobrar_paypal(self, email: str, monto: float) -> dict:
        self._paypal.login("client_id_xxx", "secret_xxx")
        pago = self._paypal.ejecutar_pago(email, monto)
        self._paypal.capturar(pago["payment_id"])
        return {"referencia": pago["payment_id"], "estado": "aprobado", "monto": monto}

    def cobrar_transferencia(self, cuenta_destino: str, monto: float) -> dict:
        self._banco.conectar("BancoNacional", "cuenta_empresa_001")
        ref = self._banco.iniciar_transferencia("cuenta_empresa_001", cuenta_destino, monto)
        estado = self._banco.verificar_estado(ref)
        return {"referencia": ref, "estado": estado.lower(), "monto": monto}


# ═══════════════════════════════════════════════════════
#  FACTORY METHOD — crea el procesador según el medio
# ═══════════════════════════════════════════════════════

class ProcesadorPago(ABC):
    """
    Clase base. Define el factory method `crear_procesador`
    y el flujo común de cobro.
    """

    def __init__(self, estrategia: EstrategiaComision):
        self.estrategia  = estrategia
        self._fachada    = FachadaPasarela()

    @abstractmethod
    def procesar(self, monto: float, **datos) -> dict:
        pass

    def _resumen(self, monto: float, resultado: dict) -> dict:
        comision   = self.estrategia.calcular(monto)
        neto       = round(monto - comision, 2)
        return {
            **resultado,
            "monto_bruto":  monto,
            "comision":     comision,
            "estrategia":   self.estrategia.descripcion(),
            "monto_neto":   neto,
        }


class ProcesadorTarjeta(ProcesadorPago):
    def procesar(self, monto: float, **datos) -> dict:
        resultado = self._fachada.cobrar_tarjeta(datos["token"], monto)
        return self._resumen(monto, resultado)


class ProcesadorPayPal(ProcesadorPago):
    def procesar(self, monto: float, **datos) -> dict:
        resultado = self._fachada.cobrar_paypal(datos["email"], monto)
        return self._resumen(monto, resultado)


class ProcesadorTransferencia(ProcesadorPago):
    def procesar(self, monto: float, **datos) -> dict:
        resultado = self._fachada.cobrar_transferencia(datos["cuenta"], monto)
        return self._resumen(monto, resultado)


class ProcesadorFactory:
    """Factory Method: decide qué procesador instanciar."""

    _estrategias = {
        "fija":        ComisionFija(2.50),
        "porcentaje":  ComisionPorcentaje(3.5),
        "escalonada":  ComisionEscalonada(),
    }

    _procesadores = {
        "tarjeta":      ProcesadorTarjeta,
        "paypal":       ProcesadorPayPal,
        "transferencia": ProcesadorTransferencia,
    }

    @classmethod
    def crear(cls, medio: str, comision: str = "escalonada") -> ProcesadorPago:
        if medio not in cls._procesadores:
            raise ValueError(f"Medio desconocido: {medio!r}")
        if comision not in cls._estrategias:
            raise ValueError(f"Estrategia desconocida: {comision!r}")

        estrategia = cls._estrategias[comision]
        return cls._procesadores[medio](estrategia)


# ═══════════════════════════════════════════════════════
#  USO
# ═══════════════════════════════════════════════════════

def imprimir_resultado(resultado: dict):
    print(f"  Referencia  : {resultado['referencia']}")
    print(f"  Estado      : {resultado['estado']}")
    print(f"  Monto bruto : ${resultado['monto_bruto']:.2f}")
    print(f"  Comisión    : ${resultado['comision']:.2f}  ({resultado['estrategia']})")
    print(f"  Monto neto  : ${resultado['monto_neto']:.2f}")


if __name__ == "__main__":

    # 1. Pago con tarjeta — comisión escalonada (por defecto)
    print("── Tarjeta de crédito ──────────────────────")
    procesador = ProcesadorFactory.crear("tarjeta")
    resultado  = procesador.procesar(250.00, token="tok_visa_4242")
    imprimir_resultado(resultado)

    # 2. Pago con PayPal — comisión porcentual
    print("\n── PayPal ──────────────────────────────────")
    procesador = ProcesadorFactory.crear("paypal", comision="porcentaje")
    resultado  = procesador.procesar(89.99, email="cliente@email.com")
    imprimir_resultado(resultado)

    # 3. Transferencia bancaria — comisión fija
    print("\n── Transferencia bancaria ──────────────────")
    procesador = ProcesadorFactory.crear("transferencia", comision="fija")
    resultado  = procesador.procesar(5000.00, cuenta="001-456-789")
    imprimir_resultado(resultado)