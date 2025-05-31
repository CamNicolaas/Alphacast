
![Logo](https://www.alphacast.io/landing/images/alphacast.svg)


# [AlphaCast](https://www.alphacast.io/)

Este repositorio es parte de una entrevista técnica que ha planteado el equipo de Alphacast enfocado en el sector de data. Consiste en la creación de un proceso ETL de una [Fuente](https://www.geopriskindex.com/)  y obtener como resultado un dataframe cargado en su plataforma, utilizando parte de su [SDK Python](https://alphacast-python-sdk.readthedocs.io/en/latest/index.html), que proporcionan a sus clientes y colaboradores.



## 🔧 Instalación

Se recomienda encarecidamente, ejecutar este repositorio en un entorno aislado. Para usos prácticos, se utiliza [virtualenv](https://virtualenv.pypa.io/en/latest/installation.html):

```bash
    git clone https://github.com/CamNicolaas/Alphacast.git
    cd Alphacast
```

Crear el entorno virtual:
```bash
    python -m pip install virtualenv

    virtualenv .

    source ./bin/activate #Linux Ubuntu
    Scripts\activate.bat  #Windows
```
Instalar las dependencias:
```bash
    pip install -r requirements.txt
```
Crear un `.env` para almacenar el Token API de AlphaCast (la estructura base se encuentra en `.env.example`). y Configurar los parámetros generales (Ver en `Configs/general_settings.json`)
```bash
    cp .env.example .env
```
Para ejecutar el proyecto, se debe ir a la ubicación del archivo en: `Modules/Geopriskindex/main.py`
```bash
    python3 Modules/Geopriskindex/main.py
```

## 📈 Opciones a Características Futuras

Aunque el objetivo inicial de este repositorio era realizar un proceso ETL “sencillo” que permitiera cargar un dataframe utilizando el SDK de AlphaCast, se tomó la libertad de incluir un enfoque más amplio, con miras a expandir los límites de la consigna y apuntar a facilitar la creación de nuevos módulos y pipelines, reutilizando componentes del sistema actual.

Se incorporaron funcionalidades que, si bien no se encontraban en los requisitos, aportan una estructura base para nuevos modulos:

- Sistema de scraping asíncrono, adaptable a la mayoría de los escenarios.

- Soporte de handlers para ficheros .csv en local.

- Uso del patrón Singleton, que asegura instancias únicas.

- Sistema básico de notificaciones vía Discord.

- Sistema básico de excepciones personalizadas.

A partir de esta base, se propone un listado de ideas que buscan fortalecer la estructura del proyecto:

- Sistema de proxies: Debido a que cada website presenta diferentes restricciones, un sistema de proxies es necesario para avanzar en la extracción de datos.

- Sistema de logging: Herramientas como [aiologger](https://async-worker.github.io/aiologger/) permitirían tener un mejor control del flujo de trabajo y detectar errores o bugs.

- Sistema de excepciones más robusto: Diseñar un sistema de excepciones más completo que permita contener y gestionar mejor los errores del SDK.

- Orquestación con Airflow: Automatizar tareas periódicas para detectar cambios en las fuentes de datos y mantener actualizado el pipeline actual.
