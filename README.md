# TENDENCIA

**Un partido político que no existe.**

Su programa electoral se reescribe a cada rato a partir de lo que es tendencia
en internet, hasta contradecirse: una obra satírica sobre la política como
veleta del algoritmo. Las promesas se generan automáticamente desde fuentes
abiertas; cualquier parecido con el vacío del discurso de campaña es el objeto
de la pieza.

> **TENDENCIA es una obra de arte satírica.** El partido que representa es
> ficticio, no concurre a ninguna elección y no representa a ninguna persona ni
> formación real. No debe presentarse ni difundirse como si fuera real.

## Cómo funciona

- `index.html` — la obra: una pantalla que muestra, en bucle, discursos de
  campaña generados a partir de tendencias reales.
- `motor_tendencias.py` — busca lo que es tendencia en **fuentes abiertas**
  (Google Trends y Google News de varios países, Wikipedia, titulares por RSS,
  Hacker News, Reddit) y lo convierte en promesas de campaña dentro de
  `trends.json`.
- `trends.json` — el banco de discursos que lee la obra.
- `.github/workflows/actualizar-tendencias.yml` — un proceso programado que
  ejecuta el motor cada pocas horas y actualiza las tendencias solo.

No utiliza X, TikTok, Instagram ni Facebook: esas plataformas no abren sus
tendencias y extraerlas incumpliría sus condiciones de uso. La pieza se apoya
únicamente en fuentes públicas pensadas para ser consultadas.

## Autoría y uso

© 2026 Alejandro Osuna Pacheco. Todos los derechos reservados.
Prohibida su reproducción, modificación o reutilización sin permiso.
Consulta [`LICENCIA.txt`](LICENCIA.txt). Contacto: aleosupa@gmail.com
