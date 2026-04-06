import sys
import os

# Proves bàsiques per verificar les funcions principals de processament.
# Aquest fitxer s'utilitzarà per comprovar automàticament que el programa funciona bé.

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.processament import netejar_dades, calcular_resum


# Dades de prova
# Es crean funcions que retornen dades noves cada vegada perquè la funció netejar_dades modifica els registres originals.
def _dades_valides():
    return [
        {"id": "1", "producte": "Laptop",  "categoria": "Electrònica", "preu": "1000.00",
         "quantitat": "2", "data": "2024-01-10", "client": "Joan", "pais": "Espanya"},
        {"id": "2", "producte": "Cadira",  "categoria": "Mobiliari",   "preu": "250.00",
         "quantitat": "3", "data": "2024-02-15", "client": "Maria", "pais": "França"},
        {"id": "3", "producte": "Monitor", "categoria": "Electrònica", "preu": "400.00",
         "quantitat": "1", "data": "2024-01-20", "client": "Pere", "pais": "Espanya"},
    ]

def _dades_errors():
    return [
        # Preu buit, s'ha d'eliminar
        {"id": "4", "producte": "Ratolí", "categoria": "Electrònica", "preu": "",
        "quantitat": "5", "data": "2024-01-05", "client": "Anna", "pais": "Espanya"},
        # Quantitat buida, s'ha d'eliminar
        {"id": "5", "producte": "Teclat", "categoria": "Electrònica", "preu": "80.00",
        "quantitat": "", "data": "2024-02-10", "client": "Jordi", "pais": "Espanya"},
        # Data invàlida, s'ha d'eliminar
        {"id": "6", "producte": "Hub",    "categoria": "Electrònica", "preu": "60.00",
        "quantitat": "2", "data": "data-dolenta", "client": "Laia", "pais": "Espanya"},
        # Registre completament vàlid
        {"id": "7", "producte": "Webcam", "categoria": "Electrònica", "preu": "79.95",
        "quantitat": "2", "data": "2024-03-05", "client": "Carlos", "pais": "Mèxic"},
    ]


#  TEST 1 - Neteja: registres vàlids
# Es comprova que dades correctes no s'eliminin per error.
def test_neteja_registres_valids():
    nets, stats = netejar_dades(_dades_valides())
    assert len(nets) == 3, "Hauria d'haver 3 registres vàlids"
    assert stats["registres_eliminats"] == 0, "No s'hauria d'eliminar cap registre"
    assert stats["registres_nets"] == 3, "stats hauria de reflectir 3 nets"
    print("[PASS] test_neteja_registres_valids")


# TEST 2 - Neteja: elimina files errònies
# Es verifica que el sistema detecta errors i elimina registres dolents.
def test_neteja_elimina_errors():
    nets, stats = netejar_dades(_dades_errors())
    assert len(nets) == 1, "Només 1 registre hauria de ser vàlid"
    assert stats["registres_eliminats"] == 3, "3 registres s'haurien d'eliminar"
    assert len(stats["errors_detectats"]) >= 3, "Haurien de detectar-se ≥3 errors"
    print("[PASS] test_neteja_elimina_errors")


# TEST 3 - Neteja: conversió de tipus
# Es comprova que els textos del CSV s'han convertit a tipus numèrics correctes.
def test_neteja_tipus_dades():
    nets, _ = netejar_dades(_dades_valides())
    for r in nets:
        assert isinstance(r["preu"], float), "preu ha de ser float"
        assert isinstance(r["quantitat"], int), "quantitat ha de ser int"
        assert isinstance(r["mes"], int), "mes ha de ser int"
        assert isinstance(r["any"], int), "any ha de ser int"
    print("[PASS] test_neteja_tipus_dades")


# TEST 4 - Neteja: total de línia calculat
# Es comprova que el càlcul preu*quantitat es fa correctament.
def test_total_linia():
    nets, _ = netejar_dades(_dades_valides())
    laptop = next(r for r in nets if r["producte"] == "Laptop")
    assert laptop["total_linia"] == 2000.00, (f"total_linia incorrecte: {laptop['total_linia']} ≠ 2000.00")
    print("[PASS] test_total_linia")


# TEST 5 - Resum: total ingressos
# Es comprova que la suma total d'ingressos coincideix amb el càlcul manual.
def test_resum_total_ingressos():
    nets, _ = netejar_dades(_dades_valides())
    resum = calcular_resum(nets)
    # Laptop: 1000×2=2000 | Cadira: 250×3=750 | Monitor: 400×1=400 → total=3150
    assert resum["total_ingressos"] == 3150.00, (f"Ingressos incorrectes: {resum['total_ingressos']} ≠ 3150.00")
    print("[PASS] test_resum_total_ingressos")


# TEST 6 - Resum: categories correctes
# Es comprova que les agrupacions per categoria funcionen.
def test_resum_categories():
    nets, _ = netejar_dades(_dades_valides())
    resum = calcular_resum(nets)
    assert "Electrònica" in resum["per_categoria"], "Ha de tenir categoria Electrònica"
    assert "Mobiliari" in resum["per_categoria"], "Ha de tenir categoria Mobiliari"

    assert resum["per_categoria"]["Electrònica"]["ingressos"] == 2400.00, ("Ingressos Electrònica incorrectes")
    print("[PASS] test_resum_categories")


# TEST 7 - Resum: top 5 productes
# Es comprova que el rànquing de productes funciona i està ordenat.
def test_resum_top5():
    nets, _ = netejar_dades(_dades_valides())
    resum = calcular_resum(nets)
    assert len(resum["top5_productes"]) <= 5, "top5 no pot tenir més de 5 elements"
    assert resum["top5_productes"][0]["producte"] == "Laptop", ("El producte top ha de ser Laptop")
    print("[PASS] test_resum_top5")


#  TEST 8 - Resum: ingressos per país
# Es comprova que els ingressos s'agrupen correctament per país.
def test_resum_per_pais():
    nets, _ = netejar_dades(_dades_valides())
    resum = calcular_resum(nets)
    assert "Espanya" in resum["ingressos_per_pais"], "Ha de tenir Espanya"
    assert "França"  in resum["ingressos_per_pais"], "Ha de tenir França"
    assert resum["ingressos_per_pais"]["Espanya"] == 2400.00, ("Ingressos Espanya incorrectes")
    print("[PASS] test_resum_per_pais")


# Execució de tests
# Aquesta funció executa tots els tests manualment (similar al que faria pytest però fet a mà).
def executar_tots():
    tests = [
        test_neteja_registres_valids,
        test_neteja_elimina_errors,
        test_neteja_tipus_dades,
        test_total_linia,
        test_resum_total_ingressos,
        test_resum_categories,
        test_resum_top5,
        test_resum_per_pais,
    ]

    print()
    print("======================================")
    print("   InsightLab – Executant tests...    ")
    print("======================================")
    print()

    passats = 0
    fallats = 0

    # Executem cada test i capturem errors perquè el programa no pari
    for test in tests:
        try:
            test()
            passats += 1
        except AssertionError as e:
            print(f"  [FAIL] {test.__name__}: {e}")
            fallats += 1
        except Exception as e:
            print(f"  [ERROR] {test.__name__}: {type(e).__name__}: {e}")
            fallats += 1

    print()
    print(f"Resultat: {passats}/{len(tests)} tests passats", end="")
    if fallats:
        print(f"  ·  {fallats} fallats")
    else:
        print("✅")
    print()


if __name__ == "__main__":
    # Permet executar els tests sense pytest, només amb python
    executar_tots()