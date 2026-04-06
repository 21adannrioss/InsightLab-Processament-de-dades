import csv
import os
import json
from datetime import datetime


# Rutes dels fitxers. Ho posem així per no escriure els paths moltes vegades.
FITXER_ENTRADA = os.path.join("data", "vendes.csv")
FITXER_RESUM = os.path.join("output", "resum.json")
FITXER_NET = os.path.join("output", "vendes_netes.csv")


#  1. Lectura del CSV
def llegir_csv(ruta: str) -> list[dict]:
    """Llegeix el CSV i retorna una llista de diccionaris."""
    registres = []

    # Obrim el fitxer CSV i cada fila es converteix en un diccionari (clau = nom columna, valor = contingut)
    with open(ruta, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for fila in reader:
            # Es fa una còpia com a dict normal per millorar el treball
            registres.append(dict(fila))

    print(f"[OK] Fitxer llegit: {ruta}  ->  {len(registres)} registres carregats")
    return registres


#  2. Neteja de dades
def netejar_dades(registres: list[dict]) -> tuple[list[dict], dict]:
    nets = []
    eliminats = 0
    errors = []

    for i, r in enumerate(registres, start=2): # start=2 perquè la fila 1 és la capçalera
        fila_ok = True

        try:
            if r["preu"].strip() == "": raise ValueError("preu buit")
            r["preu"] = round(float(r["preu"]), 2)

        except (ValueError, KeyError) as e:
            errors.append(f"Fila {i}: preu invàlid ({e})")
            fila_ok = False

        try:
            if r["quantitat"].strip() == "": raise ValueError("quantitat buida")
            r["quantitat"] = int(r["quantitat"])

        except (ValueError, KeyError) as e:
            errors.append(f"Fila {i}: quantitat invàlida ({e})")
            fila_ok = False

        try:
            # S'intenta interpretar la data amb el format esperat
            data_obj = datetime.strptime(r["data"].strip(), "%Y-%m-%d")

            # Es torna a guardar normalitzada
            r["data"] = data_obj.strftime("%Y-%m-%d")

            r["mes"] = data_obj.month
            r["any"] = data_obj.year

        except (ValueError, KeyError) as e:
            errors.append(f"Fila {i}: data invàlida ({e})")
            fila_ok = False

        for camp in ("producte", "categoria", "client", "pais"):
            if not r.get(camp, "").strip():
                errors.append(f"Fila {i}: camp '{camp}' buit")
                fila_ok = False

        if fila_ok:
            # Es calcula el total d'aquesta venda i s'arrodoneix a 2 decimals
            r["total_linia"] = round(r["preu"] * r["quantitat"], 2)
            nets.append(r)
        else:
            eliminats += 1

    # Resum de què ha passat durant la neteja
    stats = {
        "registres_originals": len(registres),
        "registres_nets": len(nets),
        "registres_eliminats": eliminats,
        "errors_detectats": errors,
    }

    print(f"[OK] Neteja completada -> {len(nets)} registres vàlids, {eliminats} eliminats")

    # Es mostrarà errors només si n'hi ha
    if errors:
        print("  Errors trobats:")
        for e in errors: print(f"    · {e}")

    return nets, stats


#  3. Transformació i agregació
def calcular_resum(registres: list[dict]) -> dict:
    """Calcula estadístiques i agregacions sobre les dades netes."""

    # Suma de camps
    total_ingressos = sum(r["total_linia"] for r in registres)
    total_unitats = sum(r["quantitat"] for r in registres)

    # Diccionari on s'acumulen dades per categoria
    per_categoria: dict[str, dict] = {}
    for r in registres:
        cat = r["categoria"]

        if cat not in per_categoria: per_categoria[cat] = {"ingressos": 0.0, "unitats": 0, "transaccions": 0}

        per_categoria[cat]["ingressos"] += r["total_linia"]
        per_categoria[cat]["unitats"] += r["quantitat"]
        per_categoria[cat]["transaccions"] += 1

    # S'arrodoneix per evitar decimals molt llargs
    for cat in per_categoria: per_categoria[cat]["ingressos"] = round(per_categoria[cat]["ingressos"], 2)

    # Agrupació per país
    per_pais: dict[str, float] = {}
    for r in registres:
        pais = r["pais"]
        per_pais[pais] = round(per_pais.get(pais, 0.0) + r["total_linia"], 2)

    # Agrupació per mes (any-mes)
    per_mes: dict[str, float] = {}
    for r in registres:
        clau = f"{r['any']}-{str(r['mes']).zfill(2)}"
        per_mes[clau] = round(per_mes.get(clau, 0.0) + r["total_linia"], 2)

    # Càlcul ingressos totals per producte
    per_producte: dict[str, float] = {}
    for r in registres:
        prod = r["producte"]
        per_producte[prod] = round(per_producte.get(prod, 0.0) + r["total_linia"], 2)

    # Ordenem i ens quedem amb els 5 millors
    top5 = sorted(per_producte.items(), key=lambda x: x[1], reverse=True)[:5]

    # Preu mitjà de tots els productes
    preu_mitja = round(sum(r["preu"] for r in registres) / len(registres), 2)

    resum = {
        "generat_el": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_registres": len(registres),
        "total_ingressos": round(total_ingressos, 2),
        "total_unitats": total_unitats,
        "preu_mitja": preu_mitja,
        "per_categoria": per_categoria,
        "ingressos_per_pais": dict(sorted(per_pais.items(), key=lambda x: x[1], reverse=True)),
        "ingressos_per_mes": dict(sorted(per_mes.items())),
        "top5_productes": [{"producte": p, "ingressos": i} for p, i in top5],
    }
    return resum


#  4. Exportació de resultats
def exportar_json(dades: dict, ruta: str) -> None:

    # Crea la carpeta si encara no existeix
    os.makedirs(os.path.dirname(ruta), exist_ok=True)

    # Indent=2 fa que el JSON sigui fàcil de llegir
    with open(ruta, "w", encoding="utf-8") as f: json.dump(dades, f, ensure_ascii=False, indent=2)

    print(f"[OK] Resum exportat a: {ruta}")


def exportar_csv_net(registres: list[dict], ruta: str) -> None:

    # Comprovació simple per evitar errors si no hi ha dades
    if not registres:
        print("[AVÍS] No hi ha dades per exportar.")
        return

    os.makedirs(os.path.dirname(ruta), exist_ok=True)

    # S'agafa automàticament les columnes del primer registre
    camps = list(registres[0].keys())

    with open(ruta, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=camps)
        writer.writeheader()
        writer.writerows(registres)

    print(f"[OK] CSV net exportat a: {ruta} -> {len(registres)} files")



# Imprimeix un resum visual per la terminal.
def mostrar_informe(resum: dict, stats_neteja: dict) -> None:
    separador = "─" * 50
 
    print()
    print("||           InsightLab - Informe de Vendes         ||")
    print()
 
    print("RESUM GENERAL")
    print(separador)
    print(f"  Total registres vàlids : {resum['total_registres']}")
    print(f"  Total ingressos        : {resum['total_ingressos']:>10.2f} €")
    print(f"  Total unitats venudes  : {resum['total_unitats']}")
    print(f"  Preu mitjà producte    : {resum['preu_mitja']:>10.2f} €")
    print()
 
    print("PER CATEGORIA")
    print(separador)
    for cat, dades in resum["per_categoria"].items():
        print(f"  {cat:<20} {dades['ingressos']:>10.2f} €   "
              f"({dades['transaccions']} vendes, {dades['unitats']} u.)")
    print()
 
    print("INGRESSOS PER PAÍS (TOP 5)")
    print(separador)
    for pais, total in list(resum["ingressos_per_pais"].items())[:5]:
        print(f"  {pais:<15} {total:>10.2f} €")
    print()
 
    print("INGRESSOS PER MES")
    print(separador)
    for mes, total in resum["ingressos_per_mes"].items():
        print(f"  {mes}   {total:>10.2f} €")
    print()
 
    print("TOP 5 PRODUCTES PER INGRESSOS")
    print(separador)
    for pos, item in enumerate(resum["top5_productes"], start=1):
        print(f"  {pos}. {item['producte']:<25} {item['ingressos']:>10.2f} €")
    print()
 
    print("QUALITAT DE LES DADES")
    print(separador)
    orig = stats_neteja["registres_originals"]
    nets = stats_neteja["registres_nets"]
    elim = stats_neteja["registres_eliminats"]
    pct = round((nets / orig) * 100, 1) if orig else 0
    print(f"  Registres originals : {orig}")
    print(f"  Registres vàlids    : {nets}  ({pct}%)")
    print(f"  Registres eliminats : {elim}")
    print()
 


#  Punt d'entrada del programa
def main() -> None:
    print()
    print("Iniciant InsightLab...")
    print()

    # 1. Es llegeix dades del CSV
    registres_bruts = llegir_csv(FITXER_ENTRADA)

    # 2. Es netejan dades incorrectes
    registres_nets, stats_neteja = netejar_dades(registres_bruts)

    # 3. Es calculen les estadístiques
    resum = calcular_resum(registres_nets)
    resum["neteja"] = stats_neteja   # afegim info extra al JSON

    # 4. Es guarden els resultats als fitxers
    exportar_json(resum, FITXER_RESUM)
    exportar_csv_net(registres_nets, FITXER_NET)

    # 5. Es mostra l'informe final per pantalla
    mostrar_informe(resum, stats_neteja)

    print("Procés finalitzat correctament.")
    print()


# aquest if fa que el programa només s'executi si aquest fitxer és el principal
if __name__ == "__main__": main()