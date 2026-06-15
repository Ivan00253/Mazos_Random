import requests
import csv
from datetime import date
import time
from random import randint,choice
from cartasIniciales import cartasIniciales

cartas_iniciales = cartasIniciales

class Carta_magic():
    def __init__(self,NOMBRE,COLOR,COSTEMANA,TIPOS,EDICION,FECHA,DESCRIPCION,ESTADISTICAS,CANTIDAD):
        self.NOMBRE = NOMBRE
        self.COLOR = COLOR
        self.COSTEMANA = COSTEMANA
        self.TIPOS = TIPOS
        self.EDICION = EDICION
        self.FECHA = date.fromisoformat(FECHA)
        self.DESCRIPCION = DESCRIPCION
        self.ESTADISTICAS = ESTADISTICAS
        self.CANTIDAD = int(CANTIDAD)
    
    def __str__(self):
        return (
        f"{self.NOMBRE} ({self.EDICION})\n"
        f"Coste: {self.COSTEMANA} | Color: {self.COLOR}\n"
        f"Tipo: {self.TIPOS}\n"
        f"{self.DESCRIPCION}\n"
        f"Stats: {self.ESTADISTICAS} | Cantidad: {self.CANTIDAD}"
        )
#region API

def respuesta_parser(respuesta,cantidad):
    carta = Carta_magic(
        respuesta["NOMBRE"],
        respuesta["COLOR"],
        respuesta["COSTEMANA"],
        respuesta["TIPOS"],
        respuesta["EDICION"],
        respuesta["FECHA"],
        respuesta["DESCRIPCION"],
        respuesta["ESTADISTICAS"],
        cantidad
    )
    return carta

def get_card_data(nombre):
    url = f"https://api.scryfall.com/cards/named"
    
    headers = {
        "User-Agent": "MazosAleatorios (ivanmachgon@gmail.com)"
    }

    for i in range(5):
        r = requests.get(url,
                         params={"fuzzy": nombre},
                         headers=headers)
         
        if r.status_code != 200 and r.status_code != 429:
            raise Exception(f"Falló: {r.status_code}\nDescripción: {r.text}")
        elif r.status_code == 429:
            time.sleep(1 * i + 1)
        else:
            break

    data = r.json()
    
    res = {
        "NOMBRE": data.get("name"),
        "COLOR": "".join(data.get("colors", [])),
        "COSTEMANA": data.get("mana_cost"),
        "TIPOS": data.get("type_line"),
        "EDICION": data.get("set_name"),
        "FECHA": data.get("released_at").replace("\n",""),
        "DESCRIPCION": data.get("oracle_text"),
        "ESTADISTICAS": f"{data.get('power','')}/{data.get('toughness','')}"
    }
    return res

#endregion
#region MANIPULAR CSV

def escribir_csv(carta):
    with open("cartas.csv", "a",newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter=";", quoting=csv.QUOTE_MINIMAL, escapechar="\\")
        writer.writerow([
            carta.NOMBRE,
            carta.COLOR,
            carta.COSTEMANA,
            carta.TIPOS,
            carta.EDICION,
            carta.FECHA,
            carta.DESCRIPCION,
            carta.ESTADISTICAS,
            carta.CANTIDAD
        ])

def sobre_escribir_csv(lista_cartas):
    with open("cartas.csv" ,"w" ,newline="" ,encoding="utf-8") as f:
        writer = csv.writer(f, delimiter=";", quoting=csv.QUOTE_MINIMAL, escapechar="\\")
        writer.writerow([
            "NOMBRE",
            "COLOR",
            "COSTEMANA",
            "TIPOS",
            "EDICION",
            "FECHA",
            "DESCRIPCION",
            "ESTADISTICAS",
            "CANTIDAD"
        ])
        for carta in lista_cartas:
            writer.writerow([
                carta.NOMBRE,
                carta.COLOR,
                carta.COSTEMANA,
                carta.TIPOS,
                carta.EDICION,
                carta.FECHA,
                carta.DESCRIPCION,
                carta.ESTADISTICAS,
                carta.CANTIDAD
            ])

def add_card(carta, cantidad):
    lista_nombres = [nt.NOMBRE for nt in leer_archivo()]

    if not carta in lista_nombres:
        try:
            respuesta = get_card_data(carta)
            respuesta_parseada = respuesta_parser(respuesta,cantidad)
            escribir_csv(respuesta_parseada)
            print("Carta añadida.")
        except:
            print("Algo a salido mal. Pruebe otra vez")
            interfaz_añadir_carta()
    else:
        lista_cartas = []
        for card in leer_archivo():
            if card.NOMBRE == carta:
                card.CANTIDAD += cantidad
            lista_cartas.append(card)
        sobre_escribir_csv(lista_cartas)

def leer_archivo():
    with open("cartas.csv", encoding="utf-8") as f:
        lista_cartas = []
        lector = csv.reader(f, delimiter=";")
        next(lector)
        for NOMBRE,COLOR,COSTEMANA,TIPOS,EDICION,FECHA,DESCRIPCION,ESTADISTICAS,CANTIDAD in lector:
            carta = Carta_magic(NOMBRE,COLOR,COSTEMANA,TIPOS,EDICION,FECHA,DESCRIPCION,ESTADISTICAS,CANTIDAD)
            lista_cartas.append(carta)
        return lista_cartas

def cargar_csv(sobreescribir = False):
    lista_cartas = []
    for nombre,cantidad in cartas_iniciales:
        respuesta = get_card_data(nombre)
        respuesta_parseada = respuesta_parser(respuesta,cantidad)
        if not sobreescribir:
            escribir_csv(respuesta_parseada)
        else:
            lista_cartas.append(respuesta_parseada)
    if sobreescribir:
        sobre_escribir_csv(lista_cartas)

#endregion
#region INTERFAZ

def parseCoste(costemana):
    costeTotal = 0
    if costemana != None:
        lista_costes = costemana.replace("{","")
        lista_costes = lista_costes.split("}")
        for elem in lista_costes:
            if elem == "" or elem == None:
                continue
            try:
                costeTotal += int(elem)
            except ValueError:
                costeTotal += 1
    return costeTotal

def mostrar_cartas(filtros, mazo_aleatorio):
    cartas = leer_archivo()
    lista_filtrada = []
    if filtros == {}:
        lista_filtrada = cartas
    else:
        for carta in cartas:
            cumple_filtros = 1
            for filtro,valor in filtros.items():
                if filtro == "colores":
                    if not any(color in valor for color in carta.COLOR):
                        cumple_filtros *= 0
                        break
                if filtro == "costemana":
                    coste = parseCoste(carta.COSTEMANA)
                    if not coste == filtros["costemana"]:
                        cumple_filtros *= 0
                        break
                if filtro == "tipos":
                    entra_lista = False
                    for tipo in filtros["tipos"]:
                        if tipo.lower() == carta.TIPOS.lower():
                            entra_lista = True
                            break
                    if not entra_lista:
                        cumple_filtros *= 0
                        break
                if filtro == "ediciones":
                    entra_lista = False
                    for edicion in filtros["ediciones"]:
                        if carta.EDICION.lower() == edicion.lower():
                            entra_lista = True
                            break
                    if not entra_lista:
                        cumple_filtros *= 0
                        break
                if filtro == "fecha":
                    if not carta.FECHA.year == filtros["fecha"]:
                        cumple_filtros *= 0
                        break
                if filtro == "cantidad":
                    if not carta.CANTIDAD == filtros["cantidad"]:
                        cumple_filtros *= 0
                        break
            if cumple_filtros == 1:
                lista_filtrada.append(carta)

    for carta_filtrada in lista_filtrada:
        print(carta_filtrada,flush=True)
        print("="*40,flush=True)

    if mazo_aleatorio:
        return lista_filtrada, filtros
    else:
        interfaz()

def interfaz_añadir_carta():
    print()
    print("Para añadir una carta escriba el nombre en INGLES y cuantas cartas tienes (por defecto 1).")
    print()
    nombre = input("Nombre: ")
    cantidad = int(input("Cantidad: "))
    add_card(nombre,cantidad)
    print()
    print("¿Añadir otra?")
    volver_add = input("S/N: ")
    if volver_add.lower() in ["s","si","y","yes"]:
        interfaz_añadir_carta()
    else:
        interfaz()

def interfaz_ver_cartas(mazo_aleatorio = False):
    print()
    print("¿Quieres aplicar algún filtro?")
    print()
    filtro = input("S/N: ")
    filtros= dict()
    if filtro.lower() in ["si","s","yes","y"]:
        fin = False
        while not fin:
            print()
            print("¿Que quieres filtrar?")
            print("1. Color.")
            print("2. Coste de mana.")
            print("3. Tipo.")
            print("4. Edición.")
            print("5. Año de salida.")
            print("6. Cantidad.")
            opcion = int(input())
            match opcion:
                case 1:
                    print("Elige que colores quieres que se vean: Azul (U), Rojo (R), Verde (G), Blanco (W), Negro (B), Incoloro (I)")
                    lista_colores = input("Escribe las letras en parentesis separadas por coma: ")
                    lista_colores = lista_colores.split(",")
                    if filtros.get("colores") == None:
                        filtros["colores"] = lista_colores
                    else:
                        filtros["colores"].extend(lista_colores)
                case 2:
                    coste = int(input("Introduzca el coste de maná convertido: "))
                    filtros["costemana"] = coste
                case 3:
                    tipos = input("Escriba los tipos por los que quiera que aparezcan separado por comas: ")
                    if filtros.get("tipos") == None:
                        filtros["tipos"] = tipos.split(",")
                    else:
                        filtros["tipos"].extend(tipos)
                case 4:
                    edicion = input("Escriba las ediciones que quiera que aparezcan separado por comas: ")
                    if filtros.get("ediciones") == None:
                        filtros["ediciones"] = edicion.split(",")
                    else:
                        filtros["ediciones"].extend(edicion)
                case 5:
                    anyo = int(input("Introduzca el año que quiera que aparezcan: "))
                    filtros["fecha"] = anyo
                case 6:
                    cantidad = int(input("Introduzca la cantidad que quiera que aparezcan: "))
                    filtros["cantidad"] = cantidad
            print("¿Quieres filtrar la lista ya?")
            salir = input("S/N: ")
            if salir.lower() in ["si", "s", "yes", "y"]:
                fin = True
    if mazo_aleatorio:
        return mostrar_cartas(filtros,mazo_aleatorio)
    else:
        mostrar_cartas(filtros,mazo_aleatorio)
        buscar_otra = input("¿Quieres hacer otra busqueda?")
        if buscar_otra.lower() in ["si","s","yes","y"]:
            interfaz_ver_cartas()
        else:
            interfaz()


def interfaz_buscar_carta():
    print()
    nombre = input("Introduzca el nombre de la carta en Ingles: ")
    existe_carta = False
    for carta in leer_archivo():
        if carta.NOMBRE.lower() == nombre.lower():
            print("="*20 + " Carta encontrada " + "="*20)
            print(carta)
            print("="*40)
            existe_carta = True
            break
    if not existe_carta:
        print("="*20 + " Carta no encontrada " + "="*20)
    interfaz()

def interfaz_mazo_aleatorio():
    seleccion = dict()
    print()
    print("¿Cuantas cartas que no sean tierra quieres, o no pongas nada para un numero desde el 30 hasta el 80?")
    print("¿Se pueden repetir cartas?")
    repetir = input("S/N: ")
    try:
        num_cartas = int(input("Ingrese un número de cartas: "))
    except:
        num_cartas = None
    if num_cartas == None:
        num_cartas = randint(30,80)
    print("¿Quieres que se apliquen filtros?")
    opcion = input("S/N: ")
    if opcion.lower() in ["si", "s", "yes", "y"]:
        lista_filtrada,filtros = interfaz_ver_cartas(mazo_aleatorio=True)
    else:
        lista_filtrada = leer_archivo()
        filtros = {}

    cartas_seleccionadas = 0
    while cartas_seleccionadas < num_cartas:
        carta = choice(lista_filtrada)
        if carta.NOMBRE in seleccion and carta.CANTIDAD > seleccion[carta.NOMBRE] and repetir.lower() in ["si", "s", "yes", "y"] and seleccion[carta.NOMBRE] < 4:
            seleccion[carta.NOMBRE] += 1
            cartas_seleccionadas += 1
        elif not carta.NOMBRE in seleccion:
            seleccion[carta.NOMBRE] = 1
            cartas_seleccionadas += 1
    print()
    print("¡Selección de cartas hecha!")
    print(f"Total de cartas no tierra: {num_cartas}. Filtros: {filtros.keys()}")
    for clave,valor in seleccion.items():
        print(f"La carta {clave}, {valor} veces.")
    print("¿Quieres otro mazo?")
    volver_rolear = input("S/N: ")
    if volver_rolear.lower() in ["si", "s", "yes", "y"]:
        interfaz_mazo_aleatorio()
    else:
        interfaz()

def interfaz_poblar_csv():
    print()
    print("!!!Cuidado esto borrará las cartas que no esten en la lista inicial¡¡¡")
    opcion = input("¿Seguro que quieres poblar el csv? S/N: ")
    if opcion.lower() in ["si", "s", "yes", "y"]:
        opcion2 = input("¿ESTAS REALMENTE SEGURO?")
        if opcion2.lower() in ["si", "s", "yes", "y"]:
            cargar_csv(True)
    interfaz()

def interfaz():
    print()
    print("========================== MAZOS RANDOMIZER ==========================")
    print()
    print("¿Qué quieres hacer?")
    print("1. Añadir carta.")
    print("2. Ver tus cartas.")
    print("3. Buscar una carta.")
    print("4. Crear un mazo aleatorio.")
    print("5. Poblar archivo csv.")
    try:
        opcion = int(input())
        match opcion:
            case 1:
                interfaz_añadir_carta()
            case 2:
                interfaz_ver_cartas()
            case 3:
                interfaz_buscar_carta()
            case 4:
                interfaz_mazo_aleatorio()
            case 5:     
                interfaz_poblar_csv()
    except ValueError:
        print("Por favor introduzca un número.")
        interfaz()
    

#endregion
#region MAIN

def main():
    interfaz()

if __name__ == "__main__":
    main()