from abc import ABC, abstractmethod

#  COMPONENTE BASE

class Reporte(ABC):
    @abstractmethod
    def generar(self) -> str:
        pass



#  PRODUCTOS CONCRETOS

class ReportePDF(Reporte):
    def __init__(self, titulo: str):
        self.titulo = titulo

    def generar(self) -> str:
        return f"[PDF] {self.titulo}"


class ReporteCSV(Reporte):
    def __init__(self, titulo: str):
        self.titulo = titulo

    def generar(self) -> str:
        return f"[CSV] {self.titulo}"


class ReporteHTML(Reporte):
    def __init__(self, titulo: str):
        self.titulo = titulo

    def generar(self) -> str:
        return f"[HTML] {self.titulo}"


#  FACTORY METHOD

class ReporteFactory(ABC):
    """Clase base: define el factory method."""

    @abstractmethod
    def crear_reporte(self, titulo: str) -> Reporte:
        pass

    def entregar(self, titulo: str) -> str:
        """Template method: crea y entrega el reporte."""
        reporte = self.crear_reporte(titulo)
        return reporte.generar()


class FactoryPDF(ReporteFactory):
    def crear_reporte(self, titulo: str) -> Reporte:
        return ReportePDF(titulo)


class FactoryCSV(ReporteFactory):
    def crear_reporte(self, titulo: str) -> Reporte:
        return ReporteCSV(titulo)


class FactoryHTML(ReporteFactory):
    def crear_reporte(self, titulo: str) -> Reporte:
        return ReporteHTML(titulo)


#  DECORATOR BASE

class ReporteDecorator(Reporte):
    """Envuelve un Reporte y delega la llamada base."""

    def __init__(self, reporte: Reporte):
        self._reporte = reporte

    def generar(self) -> str:
        return self._reporte.generar()


#  DECORADORES CONCRETOS

class ConEncabezado(ReporteDecorator):
    def __init__(self, reporte: Reporte, empresa: str):
        super().__init__(reporte)
        self.empresa = empresa

    def generar(self) -> str:
        encabezado = f"© {self.empresa} — Confidencial"
        return f"{encabezado}\n{self._reporte.generar()}"


class ConFirma(ReporteDecorator):
    def __init__(self, reporte: Reporte, autor: str):
        super().__init__(reporte)
        self.autor = autor

    def generar(self) -> str:
        return f"{self._reporte.generar()}\nFirmado por: {self.autor}"


class ConCifrado(ReporteDecorator):
    def generar(self) -> str:
        contenido = self._reporte.generar()
        cifrado = contenido.encode("utf-8").hex()  # simulación simple
        return f"[CIFRADO]\n{cifrado[:40]}..."



#  USO

if __name__ == "__main__":
    factories = {
        "pdf":  FactoryPDF(),
        "csv":  FactoryCSV(),
        "html": FactoryHTML(),
    }

    titulo = "Ventas Q1 2025"

    # Reporte PDF con encabezado y firma
    reporte = factories["pdf"].crear_reporte(titulo)
    reporte = ConEncabezado(reporte, empresa="Acme Corp")
    reporte = ConFirma(reporte, autor="Ana García")
    print("── PDF con encabezado y firma ──")
    print(reporte.generar())

    print()

    # Reporte CSV solo con firma
    reporte = factories["csv"].crear_reporte(titulo)
    reporte = ConFirma(reporte, autor="Luis Pérez")
    print("── CSV con firma ──")
    print(reporte.generar())

    print()

    # Reporte HTML con encabezado, firma y cifrado (capas apiladas)
    reporte = factories["html"].crear_reporte(titulo)
    reporte = ConEncabezado(reporte, empresa="Acme Corp")
    reporte = ConFirma(reporte, autor="Sofía Ramos")
    reporte = ConCifrado(reporte)
    print("── HTML con encabezado + firma + cifrado ──")
    print(reporte.generar())