# Principios SOLID

Los principios SOLID son cinco reglas del diseño de software orientado a objetos el cual ayuda a crear software más mantenible, flexible y escalable.

---

## S — Single Responsibility Principle (Principio de Responsabilidad Única)

> *"Una clase debe tener una, y solo una, razón para cambiar."*

Cada clase o módulo debe encargarse de una sola responsabilidad. Si una clase hace demasiadas cosas, un cambio en una de ellas puede romper las demás.

### Mal ejemplo

```python
class Usuario:
    def __init__(self, nombre, email):
        self.nombre = nombre
        self.email = email

    def guardar_en_bd(self):
        # Lógica de base de datos mezclada con la entidad
        print(f"Guardando {self.nombre} en la base de datos...")

    def enviar_bienvenida(self):
        # Lógica de email mezclada con la entidad
        print(f"Enviando email de bienvenida a {self.email}...")
```

### Buen ejemplo aplicando SRP

```python
class Usuario:
    def __init__(self, nombre, email):
        self.nombre = nombre
        self.email = email

class UsuarioRepositorio:
    def guardar(self, usuario: Usuario):
        print(f"Guardando {usuario.nombre} en la base de datos...")

class UsuarioNotificador:
    def enviar_bienvenida(self, usuario: Usuario):
        print(f"Enviando email de bienvenida a {usuario.email}...")
```

Cada clase tiene una única razón para cambiar: `Usuario` si cambia el modelo, `UsuarioRepositorio` si cambia la persistencia, y `UsuarioNotificador` si cambia la lógica de notificaciones.

---

## O — Open/Closed Principle (Principio Abierto/Cerrado)

> *"Las entidades de software deben estar abiertas para extensión, pero cerradas para modificación."*

Debes poder agregar nuevas funcionalidades sin modificar el código existente, usando herencia, composición o interfaces.

### Mal ejemplo

```python
class CalculadoraDescuento:
    def calcular(self, tipo_cliente, precio):
        if tipo_cliente == "regular":
            return precio * 0.95
        elif tipo_cliente == "vip":
            return precio * 0.80
        # Cada nuevo tipo de cliente obliga a modificar esta clase
```

### Buen ejemplo aplicando OCP

```python
from abc import ABC, abstractmethod

class Descuento(ABC):
    @abstractmethod
    def aplicar(self, precio: float) -> float:
        pass

class DescuentoRegular(Descuento):
    def aplicar(self, precio: float) -> float:
        return precio * 0.95

class DescuentoVIP(Descuento):
    def aplicar(self, precio: float) -> float:
        return precio * 0.80

class DescuentoNuevoCliente(Descuento):  # Extensión sin modificar nada anterior
    def aplicar(self, precio: float) -> float:
        return precio * 0.70

class CalculadoraDescuento:
    def calcular(self, descuento: Descuento, precio: float) -> float:
        return descuento.aplicar(precio)
```

Agregar un nuevo tipo de descuento no requiere tocar `CalculadoraDescuento`.

---

## L — Liskov Substitution Principle (Principio de Sustitución de Liskov)

> *"Los objetos de una subclase deben poder reemplazar a los de la clase base sin alterar el comportamiento correcto del programa."*

Una subclase no debe romper las expectativas definidas por su clase padre.

### Mal ejemplo

```python
class Rectangulo:
    def __init__(self, ancho, alto):
        self.ancho = ancho
        self.alto = alto

    def area(self):
        return self.ancho * self.alto

class Cuadrado(Rectangulo):
    def __init__(self, lado):
        super().__init__(lado, lado)

    # El problema surge al modificar dimensiones:
    # Un cuadrado no puede tener ancho y alto independientes,
    # lo que viola el contrato del Rectangulo.
    @Rectangulo.ancho.setter
    def ancho(self, valor):
        self._ancho = valor
        self._alto = valor  # ¡Efecto secundario inesperado!
```

### Buen ejemplo aplicando LSP

```python
from abc import ABC, abstractmethod

class Forma(ABC):
    @abstractmethod
    def area(self) -> float:
        pass

class Rectangulo(Forma):
    def __init__(self, ancho: float, alto: float):
        self.ancho = ancho
        self.alto = alto

    def area(self) -> float:
        return self.ancho * self.alto

class Cuadrado(Forma):
    def __init__(self, lado: float):
        self.lado = lado

    def area(self) -> float:
        return self.lado ** 2

def imprimir_area(forma: Forma):
    print(f"Área: {forma.area()}")

# Ambos son intercambiables sin sorpresas
imprimir_area(Rectangulo(4, 5))  # Área: 20
imprimir_area(Cuadrado(4))       # Área: 16
```

Ambas clases cumplen el contrato de `Forma` sin comportamientos inesperados.

---

## I — Interface Segregation Principle (Principio de Segregación de Interfaces)

> *"Los clientes no deben estar obligados a depender de interfaces que no utilizan."*

Es mejor tener varias interfaces pequeñas y específicas que una sola interfaz grande y genérica.

### Mal ejemplo

```python
from abc import ABC, abstractmethod

class Trabajador(ABC):
    @abstractmethod
    def trabajar(self): pass

    @abstractmethod
    def comer(self): pass

    @abstractmethod
    def dormir(self): pass

class Robot(Trabajador):
    def trabajar(self):
        print("Robot trabajando...")

    def comer(self):
        raise NotImplementedError("Los robots no comen")  # ¡Violación!

    def dormir(self):
        raise NotImplementedError("Los robots no duermen")  # ¡Violación!
```

### Buen ejemplo aplicando ISP

```python
from abc import ABC, abstractmethod

class Trabajable(ABC):
    @abstractmethod
    def trabajar(self): pass

class Alimentable(ABC):
    @abstractmethod
    def comer(self): pass

class Descansable(ABC):
    @abstractmethod
    def dormir(self): pass

class Humano(Trabajable, Alimentable, Descansable):
    def trabajar(self): print("Humano trabajando...")
    def comer(self):    print("Humano comiendo...")
    def dormir(self):   print("Humano durmiendo...")

class Robot(Trabajable):
    def trabajar(self): print("Robot trabajando...")
    # Solo implementa lo que necesita
```

Cada clase implementa únicamente las interfaces que le corresponden.

---

## D — Dependency Inversion Principle (Principio de Inversión de Dependencias)

> *"Los módulos de alto nivel no deben depender de módulos de bajo nivel. Ambos deben depender de abstracciones."*

Las clases no deben instanciar sus propias dependencias directamente; deben recibirlas desde el exterior (inyección de dependencias).

### Mal ejemplo

```python
class MySQLConexion:
    def guardar(self, datos):
        print(f"Guardando en MySQL: {datos}")

class PedidoServicio:
    def __init__(self):
        # Acoplado directamente a MySQL
        self.db = MySQLConexion()

    def procesar(self, pedido):
        self.db.guardar(pedido)
```

### Buen ejemplo aplicando DIP

```python
from abc import ABC, abstractmethod

class BaseDeDatos(ABC):
    @abstractmethod
    def guardar(self, datos): pass

class MySQLConexion(BaseDeDatos):
    def guardar(self, datos):
        print(f"Guardando en MySQL: {datos}")

class MongoConexion(BaseDeDatos):
    def guardar(self, datos):
        print(f"Guardando en MongoDB: {datos}")

class PedidoServicio:
    def __init__(self, db: BaseDeDatos):  # Depende de la abstracción
        self.db = db

    def procesar(self, pedido):
        self.db.guardar(pedido)

# Se puede cambiar la implementación sin tocar PedidoServicio
servicio = PedidoServicio(MySQLConexion())
servicio.procesar({"id": 1, "producto": "Laptop"})

servicio_mongo = PedidoServicio(MongoConexion())
servicio_mongo.procesar({"id": 2, "producto": "Mouse"})
```

`PedidoServicio` no sabe ni le importa qué base de datos se usa; solo conoce la abstracción.

---

## Resumen

Aplicar SOLID de forma consistente resulta en código más limpio, fácil de probar y preparado para crecer sin convertirse en un caos.
