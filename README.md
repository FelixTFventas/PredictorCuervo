# Predictor Mundial Cuervo

Aplicacion Flask para competir con predicciones de partidos mundialistas.

## Funcionalidades

- Registro, login y logout de usuarios.
- Primer usuario admin automatico si no configuras `ADMIN_EMAIL`.
- Panel admin para crear/editar partidos y cargar resultados.
- Partidos cargados automaticamente con SQLite.
- Predicciones editables antes del inicio del partido.
- Bloqueo automatico cuando el partido ya empezo.
- Calculo de puntos: 3 exacto, 2 por ganador/empate, 0 sin acierto.
- Dashboard, perfil y ranking global.
- Interfaz responsive tipo app deportiva.
- Estructura preparada para API-Football.

## Instalacion en Windows

```bash
cd C:\Users\JUNIOR\predictor_mundial_cuervo
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Luego abre:

```text
http://127.0.0.1:5000
```

## Base de datos

La base SQLite se crea automaticamente en:

```text
instance/database.db
```

Los partidos iniciales se cargan automaticamente la primera vez que inicia la app.

## Admin

Por defecto, si no existe `ADMIN_EMAIL`, el primer usuario registrado sera admin. Si ya tenias usuarios antes de esta mejora, al iniciar la app se asigna como admin al primer usuario si todavia no hay ningun admin.

Tambien puedes definir un email admin especifico antes de iniciar:

```bash
set ADMIN_EMAIL=tuemail@gmail.com
python app.py
```

Cuando ingreses con un usuario admin veras el link `Admin` en la navegacion.

Desde el panel admin puedes:

- crear partidos manualmente
- editar equipos, fecha, sede, fase, ronda y estado
- cargar resultados finales
- recalcular puntos
- probar botones preparados para sincronizacion futura con API

## Preparacion API-Football

La app ya incluye configuracion y servicios base para conectar API-Football mas adelante.

Variables futuras:

```bash
set API_FOOTBALL_KEY=tu_api_key
set WORLD_CUP_LEAGUE_ID=id_del_mundial
set WORLD_CUP_SEASON=2026
```

Por ahora los botones de sincronizacion muestran un aviso si la API no esta configurada.
