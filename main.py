import json
from datetime import datetime, timedelta
from pathlib import Path

import requests

API = "https://api.coingecko.com/api/v3/simple/price"
ARCHIVO = Path(__file__).parent / "historial.json"
MONEDAS = "bitcoin,ethereum"


def obtener_precio():
    try:
        respuesta = requests.get(
            API,
            params={"ids": MONEDAS, "vs_currencies": "usd,eur"},
            timeout=10,
        )
        respuesta.raise_for_status()
    except requests.RequestException as error:
        print(f"Error al consultar la API: {error}")
        return None
    return respuesta.json()


def cargar_historial():
    if not ARCHIVO.exists():
        return []
    with ARCHIVO.open(encoding="utf-8") as f:
        return json.load(f)


def guardar_historial(historial):
    with ARCHIVO.open("w", encoding="utf-8") as f:
        json.dump(historial, f, ensure_ascii=False, indent=2)


def consultar(historial):
    precios = obtener_precio()
    if precios is None:
        return

    ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ahora}]")
    for nombre in precios:
        print(f"  1 {nombre.upper()} = {precios[nombre]['usd']} USD ({precios[nombre]['eur']} EUR)")

    historial.append({"fecha": ahora, **precios})
    guardar_historial(historial)


def ver_historial(historial):
    if not historial:
        print("Todavía no hay consultas guardadas.")
        return
    for c in historial:
        partes = [f"{nombre.upper()} {c[nombre]['usd']} USD" for nombre in MONEDAS.split(",")]
        print(f"{c['fecha']}  {' | '.join(partes)}")


def ultimo_mes(historial):
    if not historial:
        return []
    limite = datetime.now() - timedelta(days=30)
    return [
        c for c in historial
        if datetime.strptime(c["fecha"], "%Y-%m-%d %H:%M:%S") >= limite
    ]


def estadisticas(historial):
    recientes = ultimo_mes(historial)
    if not recientes:
        if historial:
            print("No hay consultas en el último mes.")
        else:
            print("Todavía no hay consultas guardadas.")
        return

    print(f"Último mes ({len(recientes)} consultas):")
    for nombre in MONEDAS.split(","):
        precios = [c[nombre]["usd"] for c in recientes]
        print(
            f"  {nombre.upper()}: mín {min(precios)} USD "
            f"/ máx {max(precios)} USD / prom {sum(precios) / len(precios):.2f} USD"
        )


def main():
    historial = cargar_historial()
    print("=== PRECIO BITCOIN ===")

    while True:
        opcion = input("Opción: 1 consultar, 2 historial, 3 estadísticas, salir: ").strip().lower()

        if opcion == "salir":
            print("¡Hasta luego!")
            break
        elif opcion == "1":
            consultar(historial)
        elif opcion == "2":
            ver_historial(historial)
        elif opcion == "3":
            estadisticas(historial)
        else:
            print("Opción no válida.")


if __name__ == "__main__":
    main()
