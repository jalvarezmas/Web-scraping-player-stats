from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import requests
import csv

def get_country_id(pais):
    """
    Aquesta funció rep el nom d'un país i retorna una tupla que conté l'ID del país i l'ID de la lliga del país.

    Args:
        pais (str): El nom del país en català (no té en compte les majúscules/minúscules).

    Returns:
        tuple: Una tupla que conté dos enters:
            - El primer element és l'ID del país (per exemple, 206 per Espanya).
            - El segon element és l'Id de la lliga (per exemple, 4 per 'Espanya').
    """

    # Convertim el nom del país introduït a minúscules per a la comparació
    # sense tenir en compte les majúscules/minúscules
    pais = pais.lower()

    # Comprovem les diferents grafies/llengües per a cada país
    if pais in ('españa', 'espanya', 'spain'):
        return 206, 4
    elif pais in ('italia', 'italy'):
        return 108, 5
    elif pais in ('alemania', 'alemanya', 'germany'):
        return 81, 3
    elif pais in ('inglaterra', 'anglaterra', 'england'):
        return 252, 2
    elif pais in ('francia', 'frança', 'france'):
        return 74, 22

def get_league(pais, headers):
    """
    Aquesta funció obté la pàgina web de la lliga d'un país determinat.

    Args:
        pais (str): El nom del país (no té en compte les majúscules/minúscules).
        headers (dict): Diccionari amb les capçaleres necessàries per a la petició HTTP.

    Returns:
        bytes: El contingut de la pàgina web obtinguda (si l'obtenció és correcta),
               o bé None en cas d'error.
    """

    # Obtenim l'ID del país i l'ID de la lliga a partir del nom del país
    id_pais, id_lliga = get_country_id(pais)

    # Construïm l'URL de la pàgina web de la lliga
    url = f"https://es.whoscored.com/Regions/{id_pais}/Tournaments/{id_lliga}/"
    print(url)

    # Intentem obtenir la pàgina web mitjançant una petició GET
    response = requests.get(url, headers=headers)

    # Comprovem si la petició s'ha realitzat correctament (codi d'estat 200)
    if response.status_code == 200:
        return response.content
    else:
        print("Error al intentar obtenir la pàgina:", response.status_code)
        return None

def get_league_seasons_playerstats(pais, headers):
    """
    Aquesta funció obté les URLs de les estadístiques dels jugadors per a cada temporada d'una lliga específica.

    Args:
        pais (str): El nom del país (no té en compte les majúscules/minúscules).
        headers (dict): Diccionari amb les capçaleres necessàries per a la petició HTTP.

    Returns:
        dict: Diccionari on les claus són temporades de la lliga (en format text) i els valors són les URLs de les
              estadístiques dels jugadors per a cada temporada.
    """

    global_url = 'https://es.whoscored.com'

    # Obtenim el contingut de la pàgina web de la lliga
    x = get_league(pais, headers)

    # Parsegem el contingut HTML amb BeautifulSoup
    soup = BeautifulSoup(x, features="html.parser")

    # Diccionari per emmagatzemar les URLs per temporada
    dic = {}

    # Convertim el nom del país a minúscules per a comparacions posteriors
    pais = pais.lower()

    # Busquem el menú de temporades ("seasons")
    seasons_menu = soup.find(id="seasons")

    # Iniciem el comptador
    cont = 0

    # Iterem sobre cada opció (temporada) del menú
    for season in seasons_menu.find_all('option'):
        # Obtenim la temporada
        temporada = season.get_text()

        # Construïm l'URL de la pàgina de la temporada
        url = f"{global_url}{season['value']}"

        # Obtenim el contingut de la pàgina de la temporada
        page_2 = requests.get(url, headers=headers)
        soup_2 = BeautifulSoup(page_2.content, features="html.parser")

        # Cas especial per a Itàlia (temporada 2022/2023): obtenim l'etapa
        if temporada == '2022/2023' and pais in ('italia', 'italy'):
            stages_menu = soup_2.find(id="stages")
            stage = stages_menu.find('option')
            url_2 = f"{global_url}{stage['value']}"
            page_3 = requests.get(url_2, headers=headers)
            soup_2 = BeautifulSoup(page_3.content, features="html.parser")

        # Busquem el submenú de navegació ("sub-navigation")
        sub_menu = soup_2.find(id="sub-navigation")

        # Busquem l'enllaç "Estadísticas de Jugador" dins del submenú
        player_stats_link = sub_menu.find('a', string='Estadísticas de Jugador')

        # Guardem l'URL de les estadístiques dels jugadors per a la temporada
        dic[temporada] = f"{global_url}{player_stats_link['href']}"

        # Limitem l'iteració a les 15 primeres temporades
        cont += 1
        if cont == 15:
            break

    # Retornem el diccionari amb les URLs per temporada
    return dic

def get_page(country, season, dict_all):
    """
    Aquesta funció obté del diccionari la URL de les estadístiques d'una lliga per una temporada.

    Args:
        country (str): El nom del país (no té en compte les majúscules/minúscules).
        season (str): La temporada de la lliga (format text, per exemple "2023/2024").
        dict_all (dict): Diccionari on les claus són països (en minúscules) i els
                         valors són sub-diccionaris on les claus són temporades
                         (format text) i els valors són les URLs de les pàgines
                         corresponents.

    Returns:
        str: L'URL de la pàgina buscada.
    """

    # Comprovem si el país existeix al diccionari principal
    if country in dict_all:
        # Comprovem si la temporada existeix al sub-diccionari del país
        if season in dict_all[country]:
            return dict_all[country][season]
        else:
            return None
    else:
        return None

def write_list_players(url, player_stats, country, season):
    """
    Aquesta funció obté les estadístiques dels jugadors d'una pàgina web i les emmagatzema en un diccionari.

    Args:
        url (str): L'URL de la pàgina web que conté les estadístiques dels jugadors.
        player_stats (list): Llista on s'emmagatzemaran les estadístiques dels jugadors.
        country (str): El nom del país (no té en compte les majúscules/minúscules).
        season (str): La temporada de la lliga (format text, per exemple "2023/2024").
    """

    # Iniciem el controlador de Chrome per interactuar amb la pàgina web
    driver = webdriver.Chrome()
    driver.get(url)

    # Acceptem les cookies si apareix el missatge emergent
    try:
        accept_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'ACEPTO')]"))
        )
        accept_button.click()
    except:
        print("La ventana emergente de cookies no apareció.")

    # Esperem a que la taula de jugadors estigui carregada
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, 'top-player-stats-summary-grid'))
    )

    # Obtenim el contingut HTML de la pàgina actual
    page_html = driver.page_source
    soup = BeautifulSoup(page_html, 'html.parser')

    # Trobem la taula de estadístiques dels jugadors
    player_stats_table = soup.find('table', id='top-player-stats-summary-grid')

    # Comprovem si s'ha trobat la taula
    if player_stats_table:
        # Iterem sobre cada fila de la taula
        for row in player_stats_table.find_all('tr'):
            # Diccionari per emmagatzemar les estadístiques de cada jugador
            player_data = {}

            # Obtenim les dades de cada fila i les emmagatzemem al diccionari
            columns = row.find_all('td')
            if len(columns) > 0:
                player_data['Lliga'] = country
                player_data['Temporada'] = season
                player_data['Nom'] = columns[1].find('a').text.strip()

                # Eliminem la coma (',') del camp equip
                team = columns[0].find('span', class_='team-name').text.strip().rstrip(',')
                player_data['Equip'] = team

                meta_data_elements = columns[1].find_all('span', class_='player-meta-data')
                player_data['Edat'] = meta_data_elements[0].text.strip()

                # Eliminem la coma (', ') del camp posició
                posi = meta_data_elements[1].text.strip().lstrip(', ')
                player_data['Posició'] = posi

                player_data['Partits'] = columns[2].text.strip()
                player_data['Minuts jugats'] = columns[3].text.strip()
                player_data['Gols'] = columns[4].text.strip()
                player_data['Assistències'] = columns[5].text.strip()
                player_data['Targetes grogues'] = columns[6].text.strip()
                player_data['Targetes vermelles'] = columns[7].text.strip()
                player_data['Xuts per partit'] = columns[8].text.strip()
                player_data['Efectivitat passades'] = columns[9].text.strip()
                player_data['Duels aeris guanyats per partit'] = columns[10].text.strip()
                player_data['MVP'] = columns[11].text.strip()
                player_data['Valoració'] = columns[12].text.strip()

                # Afegim les dades del jugador a la llista d'estadístiques
                player_stats.append(player_data)

    return player_stats

# ----------------------------------------------------------------------------------------------------------------------

# Modificació de l'User Agent per poder fer el requests.get() satisfactòriament
headers = {
"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,\
*/*;q=0.8",
"Accept-Encoding": "gzip, deflate, sdch, br",
"Accept-Language": "en-US,en;q=0.8",
"Cache-Control": "no-cache",
"dnt": "1",
"Pragma": "no-cache",
"Upgrade-Insecure-Requests": "1",
"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 \
              (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
}

# LLista de països més destacats
countries = ['Espanya', 'Italia', 'Alemanya', 'Anglaterra', 'França']

seasons = [
    '2009/2010', '2010/2011', '2011/2012', '2012/2013', '2013/2014', '2014/2015',
    '2015/2016', '2016/2017', '2017/2018', '2018/2019', '2019/2020', '2020/2021',
    '2021/2022', '2022/2023', '2023/2024'
]

# Diccionari per emmagatzemar les URLs de les temporades de cada país
dict_all = {}

# Iterem sobre cada país de la llista
for country in countries:
    dict_seasons_pais = get_league_seasons_playerstats(country, headers)
    dict_all[country] = dict_seasons_pais


# Crea una llista de tots els jugadors amb les seves estadístiques
player_stats = []
# Iterem sobre cada país de la llista i sobre cada temporada
for country in countries:
    print("Country: ", country)
    for season in seasons:
        url = get_page(country, season, dict_all)
        write_list_players(url, player_stats, country, season)
        print(season)

# Ecriptura del diccionari final al csv
csv_file = 'best_players.csv'
headers = player_stats[0].keys()

# Obrim el fitxer CSV en mode d'escriptura
with open(csv_file, 'w', newline='', encoding='utf-8') as file:
  # Objecte per escriure les dades al CSV
  writer = csv.DictWriter(file, fieldnames=headers)

  # Escrivim la fila d'encapçalaments
  writer.writeheader()

  # Iterem sobre les estadístiques dels jugadors i les escrivim al CSV
  for player in player_stats:
    writer.writerow(player)

print(f"S'han desat les dades al fitxer '{csv_file}'.")