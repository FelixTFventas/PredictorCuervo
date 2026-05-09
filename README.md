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
cd C:\Users\JUNIOR\PredictorCuervo
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

## Configuracion recomendada

En desarrollo puedes correr con SQLite sin variables extra. Para un entorno compartido o produccion define al menos:

```bash
set SECRET_KEY=una-clave-larga-y-segura
set APP_TIMEZONE=America/Bogota
set FLASK_DEBUG=0
python app.py
```

Si usas PostgreSQL, define `DATABASE_URL`. La app acepta URLs `postgres://` o `postgresql://` y las normaliza para usar el driver `psycopg`.

```bash
set DATABASE_URL=postgresql://usuario:clave@host:5432/base
```

En produccion (`APP_ENV=production` o `FLASK_ENV=production`) `SECRET_KEY` es obligatoria.

## Despliegue

Para produccion usa PostgreSQL con `DATABASE_URL`. SQLite solo se recomienda para desarrollo local; si no defines `DATABASE_URL`, la app intentara crear `instance/database.db` dentro del contenedor y algunos hostings pueden bloquearlo o perderlo en cada redeploy.

Variables minimas:

```bash
DATABASE_URL=postgresql://usuario:clave@host:5432/base
SECRET_KEY=una-clave-larga-y-segura
APP_ENV=production
APP_TIMEZONE=America/Bogota
FLASK_DEBUG=0
```

Comando de inicio recomendado en Linux/hosting:

```bash
python -m flask db upgrade && gunicorn app:app
```

Si el hosting no permite ejecutar migraciones en el start command, ejecuta antes del despliegue:

```bash
FLASK_APP=app.py python -m flask db upgrade
```

## Migraciones

El proyecto usa Flask-Migrate/Alembic. Para una base nueva, ejecuta:

```bash
set FLASK_APP=app.py
python -m flask db upgrade
```

Si ya tienes una base SQLite local creada antes de migraciones, puedes marcarla como actual sin recrear tablas:

```bash
set FLASK_APP=app.py
python -m flask db stamp head
```

Para crear migraciones futuras despues de modificar modelos:

```bash
set FLASK_APP=app.py
python -m flask db migrate -m "describe el cambio"
python -m flask db upgrade
```

`db.create_all()` se mantiene temporalmente para facilitar desarrollo local, pero los comandos `flask db ...` no lo ejecutan para que Alembic controle el esquema.

## Horarios

Los formularios admin y CSV se interpretan en hora Bogota (`America/Bogota`) y se guardan internamente en UTC. Las plantillas vuelven a mostrar los horarios en Bogota.

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
