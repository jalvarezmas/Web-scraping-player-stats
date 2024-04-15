# Pràctica 1: Web scraping

## Descripció
Aquesta pràctica s'ha realitzat sota el context de l'assignatura Tipologia i cicle de vida de les dades, que pertany al Màster en Ciència de Dades de la Universitat Oberta de Catalunya. S'hi apliquen tècniques de web scraping mitjançant el llenguatge de programació Python per extreure així dades del web WhoScored.com i generar un conjunt de dades.
S'extreuen les estadístiques generals, com gols, targetes i valoració, entre d'altres, dels 10 millors jugadors de la temporada de les 5 grans lligues d'Europa: La Liga, la Serie A, la Bundesliga, la Premier League i la Ligue 1, des de la temporada 2009/2010 fins a la temporada actual. 

## Integrants del grup
- Juan Antonio Alvarez Masdeu
- Marc LLadó Maldonado

## Arxius del repositori
- **requirements.txt**: Llista de dependències necessàries per executar el codi.
- **source/oficial.py**: Script principal que conté les funcions i el codi principal del projecte.
- **dataset/best_players.csv**: Fitxer CSV on es guardaran les dades finals dels jugadors.

## Funcionament
Primer de tot hem d'instalar les llibreries que necessitem per executar el codi. Pots instal·lar-les executant el següent comandament des de la línia de comandes:
```
pip install -r requirements.txt
```
Posteriorment executem el script principal des de la línia de comandes:
```
python source/oficial.py
```
El codi utilitzarà les lligues i temporades predefinides a les variables ````countries```` i ````seasons```` del fitxer **source/oficial.py**.
El funcionament del projecte està limitat per les 5 grans lligues d'Europa (Espanya, Itàlia, Alemanya, Anglaterra i França) i per a les temporades que van des de la 2009/2010 fins a la 2023/2024. Dins d'aquests paràmetres pots modificar les variables esmentades anteriorment per provar altres escenaris.

## DOI de Zenodo del dataset
https://doi.org/10.5281/zenodo.10975068
