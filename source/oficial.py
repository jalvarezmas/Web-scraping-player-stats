from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import requests
import csv

# Donat un país d'entrada, et retorna: id del país i id de la lliga del país
def get_country_id(pais):

    pais = pais.lower()
    if pais == 'españa' or pais == 'espanya' or pais == 'spain':
        return 206, 4
    elif pais == 'italia' or pais == 'italy':
        return 108, 5
    elif pais == 'alemania' or pais == 'alemanya' or pais == 'germany':
        return 81, 3
    elif pais == 'inglaterra' or pais == 'anglaterra' or pais == 'england':
        return 252, 2
    elif pais == 'francia' or pais == 'frança' or pais == 'france':
        return 74, 22


# Donat un país d'entrada, et retorna: id del país i id de la lliga del país
def get_league(pais, headers):

    id_pais, id_lliga = get_country_id(pais)
    url = f"https://es.whoscored.com/Regions/{id_pais}/Tournaments/{id_lliga}/"
    print(url)
    response = requests.get(url, headers = headers)
    if response.status_code == 200:
        return response.content
    else:
        print("Error al intentar obtenir la pàgina:", response.status_code)
        return None


def get_league_seasons_playerstats(pais, headers):

    global_url = 'https://es.whoscored.com'
    x = get_league(pais, headers)
    soup = BeautifulSoup(x, features="html.parser")
    cont = 0
    dic={}
    for season in soup.find(id="seasons").find_all('option'):
        url = f"{global_url}{season['value']}"
        page_2 = requests.get(url, headers=headers)
        soup_2 = BeautifulSoup(page_2.content, features="html.parser")
        if season.get_text() == '2022/2023' and pais == 'Italia':
            soup_5 = soup_2.find(id="stages").find('option')
            url_2 = f"{global_url}{soup_5['value']}"
            page_3 = requests.get(url_2, headers=headers)
            soup_2 = BeautifulSoup(page_3.content, features="html.parser")
        soup_3 = soup_2.find(id="sub-navigation")
        soup_4 = soup_3.find('a', string='Estadísticas de Jugador')

        dic[season.get_text()] = f"{global_url}{soup_4['href']}"

        cont += 1
        if cont == 15:
            break

    return dic


# cerca en el diccionari del país i temporada , retorna la url que toca.
def get_page(country, season, dict_all):

    if country in dict_all and season in dict_all[country]:
        return dict_all[country][season]
    else:
        return None


def write_dict_players(url, player_stats, country, season):
    # Abrir la página en el navegador
    driver = webdriver.Chrome()
    driver.get(url)
    #  Accepta cookies:
    try:
        accept_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'ACEPTO')]"))
        )
        accept_button.click()
    except:
        print("La ventana emergente de cookies no apareció.")

    # Espera a localitzar la taula de jugadors
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, 'top-player-stats-summary-grid'))
    )

    # Obtener el contenido HTML de la página actual
    page_html = driver.page_source
    soup = BeautifulSoup(page_html, 'html.parser')

    # Encontrar la tabla de estadísticas de jugadores
    player_stats_table = soup.find('table', id='top-player-stats-summary-grid')

    # Verificar si se encontró la tabla
    if player_stats_table:
        for row in player_stats_table.find_all('tr'):
            # Crear un diccionario para almacenar las estadísticas de cada jugador
            player_data = {}
            # Obtener los datos de la fila y almacenarlos en el diccionario
            columns = row.find_all('td')
            if len(columns) > 0:
                player_data['Lliga'] = country
                player_data['Temporada'] = season
                player_data['Nom'] = columns[1].find('a').text.strip()

                # Eliminem la ',' del camp equip:
                team = columns[0].find('span', class_='team-name').text.strip()
                player_data['Equip'] = team.rstrip(',')

                meta_data_elements = columns[1].find_all('span', class_='player-meta-data')
                player_data['Edat'] = meta_data_elements[0].text.strip()

                # Eliminem la ', ' del camp posicio:
                posi = meta_data_elements[1].text.strip()
                player_data['Posició'] = posi.lstrip(', ')

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

                # Agregar los datos del jugador a la lista de estadísticas de jugadores -->  player_stats
                player_stats.append(player_data)

    return player_stats

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

web = 'https://es.whoscored.com'
page = requests.get(web, headers = headers)


# ---------------------------------------------------------------------------------------

# LLista de països més destacats
countries = ['Espanya', 'Italia', 'Alemanya', 'Anglaterra', 'França']

seasons = [
    '2009/2010', '2010/2011', '2011/2012', '2012/2013', '2013/2014', '2014/2015',
    '2015/2016', '2016/2017', '2017/2018', '2018/2019', '2019/2020', '2020/2021',
    '2021/2022', '2022/2023', '2023/2024'
]

# Creem un diccionari i l'omplirem amb keys: països i values: diccionari de seasons per cada pais
# el diccionari de seasosn es dirà dict_seasons_pais i contindrà -->  season (key) :  url (value)
dict_all = {}

for country in countries:
    dict_seasons_pais = get_league_seasons_playerstats(country, headers)
    dict_all[country] = dict_seasons_pais


# Crea diccionari de tots els jugadors amb les seves stats ----------------------------------------------------------
player_stats = []

for country in countries:
    print("Country: ", country)
    for season in seasons:
        url = get_page(country, season, dict_all)
        dict_players = write_dict_players(url, player_stats, country, season)
        print(season)



# Ecriptura del diccionari final al csv  -----------------------------------------------------------------------------
csv_file = 'best_players.csv'
headers = player_stats[0].keys()
# Escribir los datos en el archivo CSV
with open(csv_file, 'w', newline='', encoding='utf-8') as file:
    # Crear el escritor CSV
    writer = csv.DictWriter(file, fieldnames=headers)

    # Escribir las cabeceras
    writer.writeheader()

    # Escribir los datos de los jugadores
    for player in dict_players:
        writer.writerow(player)

print(f"Los datos se han guardado en '{csv_file}'.")

