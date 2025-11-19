# Estructura del Proyecto - Aplicación de Conceptos

Este documento explica dónde se aplican los conceptos de programación en el proyecto.

## 📁 Estructura de Directorios

```
DAO_Grupo_79_4K2/
├── entities/              # Entidades del dominio (OOP)
│   ├── persona.py        # Clase base abstracta (Herencia)
│   ├── cliente.py         # Clase hija (Herencia y Polimorfismo)
│   ├── empleado.py       # Clase hija (Herencia y Polimorfismo)
│   ├── vehiculo.py       # Clase de entidad (OOP)
│   └── alquiler.py       # Clase de entidad (OOP)
├── persistence/           # Capa de persistencia
│   ├── database_connection.py  # Patrón Singleton
│   ├── dao_base.py        # Clase base abstracta (Herencia)
│   ├── cliente_dao.py     # DAO para Cliente (Persistencia)
│   ├── empleado_dao.py   # DAO para Empleado (Persistencia)
│   ├── vehiculo_dao.py   # DAO para Vehiculo (Persistencia)
│   └── alquiler_dao.py   # DAO para Alquiler (Persistencia)
├── patterns/              # Patrones de diseño
│   ├── observer.py       # Patrón Observer
│   └── factory.py        # Patrón Factory
├── services/             # Servicios de negocio
│   └── reportes_service.py  # Servicio de reportes (OOP)
└── validations.py        # Validaciones (Programación Funcional)
```

## 🎯 Conceptos Aplicados

### 1. Programación Estructurada
**Ubicación**: Todas las funciones y métodos están bien estructurados

- **`database.py`**: Funciones `init_db()`, `seed_sample_data()` - funciones bien estructuradas
- **`persistence/*_dao.py`**: Métodos `create()`, `read()`, `update()`, `delete()` - funciones estructuradas
- **`services/alquiler_service.py`**: Método `registrar_alquiler()` - función estructurada

### 2. Programación Funcional
**Ubicación**: Uso de funciones puras, map, filter

- **`persistence/cliente_dao.py`** (línea ~45): 
  ```python
  # Programación Funcional - map para transformar datos
  return list(map(lambda row: Cliente.from_dict(dict(row)), rows))
  ```

- **`persistence/vehiculo_dao.py`** (línea ~60):
  ```python
  # Programación Funcional - filter para filtrar datos
  return list(filter(lambda v: v.esta_disponible(), todos))
  ```

- **`patterns/observer.py`** (línea ~50):
  ```python
  # Programación Funcional - map para notificar a todos
  list(map(lambda obs: obs.update(event_type, data), self._observers))
  ```

- **`validations.py`**: Funciones puras de validación (sin efectos secundarios)

### 3. Programación Orientada a Objetos (OOP)

#### Encapsulación
- **`entities/persona.py`**: Propiedades con getters/setters
- **`entities/cliente.py`**: Encapsulación de datos con propiedades
- **`entities/vehiculo.py`**: Encapsulación de estado y comportamiento

#### Clases y Objetos
- **`entities/`**: Todas las clases de entidades (Cliente, Empleado, Vehiculo, Alquiler)
- **`persistence/`**: Clases DAO para acceso a datos
- **`services/`**: Clases de servicio para lógica de negocio

### 4. Herencia y Polimorfismo

#### Herencia
- **`entities/persona.py`**: Clase base abstracta `Persona`
  - **`entities/cliente.py`**: Clase `Cliente` hereda de `Persona`
  - **`entities/empleado.py`**: Clase `Empleado` hereda de `Persona`

- **`persistence/dao_base.py`**: Clase base abstracta `DAOBase`
  - **`persistence/cliente_dao.py`**: `ClienteDAO` hereda de `DAOBase`
  - **`persistence/empleado_dao.py`**: `EmpleadoDAO` hereda de `DAOBase`
  - **`persistence/vehiculo_dao.py`**: `VehiculoDAO` hereda de `DAOBase`
  - **`persistence/alquiler_dao.py`**: `AlquilerDAO` hereda de `DAOBase`

#### Polimorfismo
- **`entities/persona.py`**: Método abstracto `tipo_persona()` - cada clase hija implementa su versión
- **`entities/persona.py`**: Método `nombre_completo()` - puede ser sobrescrito
- **`persistence/dao_base.py`**: Métodos abstractos que cada DAO implementa de forma diferente

### 5. Persistencia

#### Patrón DAO (Data Access Object)
- **`persistence/dao_base.py`**: Clase base abstracta para DAOs
- **`persistence/cliente_dao.py`**: DAO para persistencia de Clientes
- **`persistence/empleado_dao.py`**: DAO para persistencia de Empleados
- **`persistence/vehiculo_dao.py`**: DAO para persistencia de Vehículos
- **`persistence/alquiler_dao.py`**: DAO para persistencia de Alquileres

Cada DAO implementa:
- `create()`: Crear entidad
- `read()`: Leer entidad por ID
- `update()`: Actualizar entidad
- `delete()`: Eliminar entidad
- `list_all()`: Listar todas las entidades

### 6. Patrones de Diseño

#### Patrón Singleton
**Ubicación**: `persistence/database_connection.py`

```python
class DatabaseConnection:
    """
    Patrón Singleton - Garantiza una única instancia de conexión
    """
    _instance = None
    
    def __new__(cls):
        """Patrón Singleton - Implementación del patrón creacional"""
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
        return cls._instance
```

**Uso**: 
- `database.py`: Función `get_connection()` usa el Singleton
- Todos los DAOs usan `DatabaseConnection()` que siempre retorna la misma instancia

#### Patrón Observer
**Ubicación**: `patterns/observer.py`

```python
class Subject:
    """Patrón Observer - Sujeto observable"""
    def notify(self, event_type, data):
        """Patrón Observer - Notifica a todos los observadores"""
        list(map(lambda obs: obs.update(event_type, data), self._observers))

class AlquilerNotifier(Subject):
    """Patrón Observer - Sujeto específico para alquileres"""
    def alquiler_creado(self, alquiler):
        """Patrón Observer - Notifica cuando se crea un alquiler"""
        self.notify("alquiler_creado", alquiler)
```

**Uso**: 
- Los patrones están implementados y disponibles para uso futuro
- Actualmente el código usa directamente `models.registrar_alquiler()` y `database.get_connection()`
- Observadores: `LogObserver`, `EmailObserver` implementan la interfaz `Observer`

#### Patrón Factory
**Ubicación**: `patterns/factory.py`

```python
class EntityFactory:
    """Patrón Factory - Factory para crear entidades"""
    @staticmethod
    def create_cliente(...):
        """Patrón Factory - Crea una instancia de Cliente"""
        return Cliente(...)

class DAOFactory:
    """Patrón Factory - Factory para crear DAOs"""
    @staticmethod
    def get_cliente_dao():
        """Patrón Factory - Obtiene instancia de ClienteDAO"""
        if 'cliente' not in DAOFactory._daos:
            DAOFactory._daos['cliente'] = ClienteDAO()
        return DAOFactory._daos['cliente']
```

**Uso**: 
- Los patrones están implementados y disponibles para uso futuro
- Actualmente el código crea entidades directamente usando constructores
- Los DAOs pueden obtenerse mediante `DAOFactory.get_cliente_dao()`

## 📝 Ejemplos de Uso

### Ejemplo 1: Crear un Cliente (OOP + Factory + Persistencia)
```python
from patterns.factory import EntityFactory
from persistence.cliente_dao import ClienteDAO

# Patrón Factory - Crear entidad
cliente = EntityFactory.create_cliente("Juan", "Pérez", "12345678")

# Persistencia - Guardar usando DAO
dao = ClienteDAO()
cliente = dao.create(cliente)
```

### Ejemplo 2: Usar Herencia y Polimorfismo
```python
from entities.cliente import Cliente
from entities.empleado import Empleado

cliente = Cliente("Juan", "Pérez")
empleado = Empleado("María", "González", cargo="Vendedor")

# Polimorfismo - Ambos tienen el método nombre_completo()
print(cliente.nombre_completo())  # "Juan Pérez"
print(empleado.nombre_completo())  # "María González"

# Polimorfismo - Cada uno implementa tipo_persona() diferente
print(cliente.tipo_persona())     # "Cliente"
print(empleado.tipo_persona())    # "Empleado"
```

### Ejemplo 3: Usar Reportes Service
```python
from services.reportes_service import ReportesService

# Patrón Singleton - El servicio usa DatabaseConnection internamente
reportes_service = ReportesService()

# Obtener reportes
alquileres_por_cliente = reportes_service.alquileres_por_cliente()
vehiculos_mas_alquilados = reportes_service.vehiculos_mas_alquilados()
```

## 🔍 Búsqueda de Conceptos

Para encontrar dónde está aplicado cada concepto, busca en el código:

- **"Patrón Singleton"**: `persistence/database_connection.py`
- **"Patrón Observer"**: `patterns/observer.py` (implementado, disponible para uso futuro)
- **"Patrón Factory"**: `patterns/factory.py` (implementado, disponible para uso futuro)
- **"Herencia y Polimorfismo"**: `entities/persona.py`, `entities/cliente.py`, `entities/empleado.py`
- **"Persistencia"**: Todo el directorio `persistence/`
- **"Programación Funcional"**: `persistence/*_dao.py` (métodos `list_all`), `patterns/observer.py`
- **"Programación Estructurada"**: Todas las funciones y métodos del proyecto

