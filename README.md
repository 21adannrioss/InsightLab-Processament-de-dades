# InsightLab – Procesamiento de datos

En InsightLab básicamente se lee un archivo CSV con ventas, detecta las filas que tienen algún dato mal (precio vacío, cantidad vacía, fecha con mal formato) y las elimina. Con lo que queda limpio, calcula algunas estadísticas y lo guarda todo en dos archivos nuevos.

Cuando lo ejecutas te aparece un resumen en la terminal y se crean estos dos archivos dentro de `output/`:

- `resum.json` -> ingresos totales, por categoría, por país, por mes y el top 5 de productos
- `vendes_netes.csv` -> el CSV original pero sin las filas con errores y con tres columnas nuevas añadidas

---

## Lo que necesitas para ejecutarlo

Solo necesitas tener Python instalado, nada más. No he usado ninguna librería externa, todo lo que importo viene incluido con Python.

Descárgalo desde aquí si no lo tienes: [python.org](https://www.python.org/downloads/)

Para comprobar que lo tienes bien instalado:
```bash
python --version
```
Tiene que salir 3.10 o superior.

---

## Cómo ejecutarlo

Clona el repositorio o descarga el ZIP y entra en la carpeta:
```bash
cd InsightLab
```

Ejecuta el script principal:
```bash
python src/processament.py
```

Verás el informe en la terminal y se creará la carpeta `output/` con los dos archivos.

---

## Los tests

He escrito 8 tests a mano para comprobar que la limpieza y los cálculos dan los resultados correctos. Para ejecutarlos:

```bash
python tests/test_processament.py
```

Si todo va bien tiene que salir:
```
Resultat: 8/8 tests passats
```