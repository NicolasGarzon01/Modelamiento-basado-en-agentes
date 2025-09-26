# Modelo de Simulación de Epidemias Basado en Agentes 🦠

Este proyecto presenta un **Modelo Basado en Agentes (ABM)** para simular la propagación de un virus en una población, utilizando el modelo epidemiológico **SIR (Susceptible, Infectado, Recuperado)**. La simulación fue desarrollada en Python utilizando la librería [MESA](https://mesa.readthedocs.io/en/stable/).

El objetivo es observar cómo se comporta una epidemia bajo diferentes condiciones y evaluar el impacto de diversas estrategias de salud pública para mitigar el contagio.

---
## Contenido del Repositorio

Este repositorio contiene dos scripts principales:

1.  `ComportamientoVirus_FINAL.py`:
    * Implementa el **modelo base SIR** sin ninguna intervención. Es útil para observar el comportamiento natural de una epidemia.
      
<img width="396" height="502" alt="image" src="https://github.com/user-attachments/assets/8347d932-6297-44eb-98a7-0c5cb8998813" />


2.  `VirusConEstrategias.py`:
    * Es una **versión avanzada del modelo** que permite simular el impacto de cuatro estrategias de salud pública:
        * **Vacunación Inicial:** Un porcentaje de la población comienza siendo inmune.
        * **Distanciamiento Social:** Los agentes tienen una probabilidad de no moverse.
        * **Cuarentena de Infectados:** Los agentes infectados son aislados de la población general.
        * **Uso de Mascarillas/Higiene:** Se reduce la probabilidad de transmisión durante un encuentro.
  
<img width="562" height="525" alt="image" src="https://github.com/user-attachments/assets/5595742e-c02c-41cb-aa6e-7432d95eb2dd" />


---
## Requisitos

* Python 3.8+
* Mesa
* Pandas

---
## Instalación y Ejecución 🚀

Sigue estos pasos para ejecutar la simulación en tu máquina local.

**1. Clona el repositorio:**
```bash
git clone [URL-DE-TU-REPOSITORIO]
cd [NOMBRE-DE-TU-CARPETA]
```
**2. Crea y activa un entorno virtual:**
```Bash
# Crear el entorno
python -m venv venv

# Activar en Windows (PowerShell)
.\venv\Scripts\Activate.ps1

# Activar en macOS/Linux
source venv/bin/activate
```

**3. Instala las dependencias:**
```bash
pip install mesa pandas
```

**posible error**
```pgsql
ModuleNotFoundError: No module named 'mesa.time'
```

solución: crear archivo time.py (adjunto en los archivos)
```swift
venv/Lib/site-packages/mesa/
```

**4. Ejecuta una simulación:**
```Bash
# Para ejecutar el modelo base
python ComportamientoVirus_FINAL.py

# Para ejecutar el modelo con estrategias
python VirusConEstrategias.py
