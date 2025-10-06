# 🚗 Vehículo Autónomo de Telemetría

Proyecto de aplicación cliente-servidor para monitoreo y control de un vehículo autónomo terrestre. Sistema de telemetría en tiempo real con soporte para múltiples clientes.

## 📋 Descripción

Este proyecto implementa un sistema de telemetría vehicular utilizando sockets TCP/IP. El servidor, desarrollado en C con la API de Sockets Berkeley, gestiona múltiples conexiones concurrentes mediante hilos y transmite datos de telemetría.

## 🖥️ Requisitos del Sistema

Este proyecto utiliza la API de Sockets Berkeley y bibliotecas POSIX que **solo están disponibles en sistemas Linux/Unix**. No es compatible con Windows de forma nativa.

### Opciones para ejecutar en Windows:

1. **WSL (Windows Subsystem for Linux)** - Recomendado
2. **Máquina Virtual con Linux** (VirtualBox, VMware)
3. **Dual Boot con Linux**
4. **Docker con imagen Linux**

### Requisitos de Software

#### Para el Servidor (Linux):

```bash
- GCC (GNU Compiler Collection)
- Make
- pthread (generalmente incluido en Linux)
- Bibliotecas estándar de C
```

#### Para Cliente Python:

```bash
- Python 3.6+
- PyQt5
```

#### Para Cliente Java:

```bash
- JDK 8 o superior
- Librería json-20240303.jar
```

## 🚀 Instalación

### 1. Clonar el Repositorio

```bash
git clone https://github.com/AmazingJuan/p1-telematica
cd p1-telematica
```

### 2. Compilar el Servidor (Linux)

```bash
(Dentro del proyecto) cd server
make
```

Esto generará el ejecutable `server`.

Para limpiar archivos compilados:

```bash
make clean
```

### 3. Configurar Cliente Python

```bash
# Instalar dependencias
pip install PyQt5

# O si usas pip3
pip3 install PyQt5
```

### 4. Compilar Cliente Java

```bash
cd client-java

# Compilar
javac -cp "lib/json-20240303.jar" -d bin CarClient.java

# En algunos sistemas puede ser necesario usar:
javac -cp "lib/json-20240303.jar:." -d bin CarClient.java
```

## 📖 Uso

### Iniciar el Servidor

```bash
cd server
./server <puerto> <archivo_log>
```

**Ejemplo:**
```bash
./server 5000 server.log
```

**Parámetros:**
- `<puerto>`: Puerto en el que el servidor escuchará conexiones (ej: 5000)
- `<archivo_log>`: Archivo donde se guardarán los logs (ej: server.log)

### Ejecutar Cliente Python

```bash
cd client-python
python main.py

# O si usas python3
python3 main.py
```

**Interfaz del Cliente Python:**
1. Selecciona modo **Observer** (solo visualización) o **Administrator** (control total)
2. Ingresa la IP del servidor (localhost si es local, o la IP de la máquina Linux)
3. Ingresa el puerto (ej: 5000)
4. Para modo Administrator, ingresa la contraseña: `admin123`
5. Haz clic en **Connect**

### Ejecutar Cliente Java

```bash
cd client-java

# Ejecutar
java -cp "bin:lib/json-20240303.jar" CarClient

# En algunos sistemas puede ser necesario usar:
java -cp "bin;lib/json-20240303.jar" CarClient
```

**Interfaz del Cliente Java:**
1. Ingresa Host: `localhost` (o la IP del servidor)
2. Ingresa Puerto: `5000`
3. Contraseña (solo admin): `admin123` (dejar vacío para modo observador)
4. Haz clic en **Conectar**

## 🔐 Autenticación

### Observador
- No requiere contraseña
- Solo puede **visualizar** telemetría en tiempo real
- No puede enviar comandos al vehículo

### Administrador
- Contraseña: `admin123`
- Puede **visualizar** telemetría
- Puede **controlar** el vehículo (velocidad, dirección)
- Puede **recargar batería**
- Puede **listar usuarios conectados**

## 🎮 Comandos Disponibles (Solo Admin)

| Comando | Descripción |
|---------|-------------|
| `SPEED UP` | Incrementa la velocidad en 10 km/h |
| `SLOW DOWN` | Reduce la velocidad en 10 km/h |
| `TURN LEFT` | Gira el vehículo a la izquierda |
| `TURN RIGHT` | Gira el vehículo a la derecha |
| `RECHARGE BATTERY` | Recarga la batería al 100% |
| `LIST USERS` | Muestra todos los usuarios conectados |

## 📊 Datos de Telemetría

El servidor envía cada 10 segundos:

#### Ejemplo

```json
{
  "speed": 0.00,
  "battery": 100.00,
  "temperature": 25.00,
  "direction": "STOP"
}
```

- **speed**: Velocidad actual en km/h
- **battery**: Nivel de batería en porcentaje (0-100%)
- **temperature**: Temperatura interna en °C
- **direction**: Dirección actual (STOP, FORWARD, LEFT, RIGHT)


## 📁 Estructura del Proyecto

```
p1-telematica/
├── server/                 # Servidor en C
│   ├── main.c             # Punto de entrada
│   ├── server.c           # Lógica del servidor
│   ├── server.h
│   ├── client_handler.c   # Manejo de clientes
│   ├── client_handler.h
│   ├── car.c              # Lógica del vehículo
│   ├── car.h
│   ├── Makefile           # Compilación
│   └── server.log         # Archivo de logs (generado)
├── client-python/         # Cliente Python con PyQt5
│   ├── main.py            # Punto de entrada
│   ├── welcome_view.py    # Vista de bienvenida
│   ├── observer_view.py   # Vista de observador
│   ├── admin_view.py      # Vista de administrador
│   └── socket_handler.py  # Manejo de conexión
├── client-java/           # Cliente Java con Swing
│   ├── CarClient.java     # Cliente completo
│   ├── lib/               # Librerías
│   │   └── json-20240303.jar
│   └── bin/               # Archivos compilados
└── README.md              # Este archivo
```

## 👥 Autores

- Juan Pablo de Jesús Avendaño Bustamante
- Diego Andrés Gonzalez Graciano
- Daniel Zapata Acevedo

Este proyecto fue desarrollado para el curso de Internet Arquitectura y Protocolos (Telemática) de la Universidad EAFIT
- Fecha: 25 Octubre 2025


---

**Nota:** Este proyecto requiere Linux para el servidor. Los clientes pueden ejecutarse en cualquier sistema operativo que soporte Python/Java, pero deben conectarse a un servidor ejecutándose en Linux.
