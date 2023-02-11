# Импорт
import requests
from bs4 import BeautifulSoup
import datetime
import time
import pandas as pd

# Функция парсит дату
def GetDateFromString(s):
    monthes = {"января" : 1, "февраля" : 2, "марта" : 3, "апреля" : 4, "мая" : 5, "июня" : 6, "июля" : 7, "августа" : 8, "сентября" : 9, "октября" : 10, "ноября" : 11, "декабря" : 12}
    day = int(s.split(' ')[0])
    month = monthes[s.split(' ')[1]]
    year = int(s.split(' ')[2][:-1])
    return datetime.date(year, month, day)

# Функция возвращает список ингредиентов (без повторов - множество)
def GetListOfIngredients(url):
    recipe_page = BeautifulSoup(requests.get(url).text, 'html.parser')
    ingredients = set()
    for ingredient in recipe_page.findAll('li', {'itemprop' : 'recipeIngredient'}):
        ingredients.add(ingredient.findAll('span')[0].text)
    return ingredients


def GetInfoAboutRecipe(url):
    # Получение страницы рецепта
    recipe_page = BeautifulSoup(requests.get(url).text, 'html.parser')

    # Получение имя автора (если существует)
    if len(recipe_page.findAll('span', {'itemprop': 'author'})) != 0:
        author = recipe_page.findAll('span', {'itemprop': 'author'})[0].text
    else:
        author = None

    # Получение даты публикации
    date_of_publication = GetDateFromString(recipe_page.findAll('span', {'class': 'i-time'})[0].text)

    # Получение количества просмотров
    amount_of_views = int(recipe_page.findAll('span', {'class': 'i-views'})[0].text)

    # Получение категории (если существует, иначе - дефолтная)
    if len(recipe_page.findAll('span', {'itemprop': 'recipeCategory'})) != 0:
        category = recipe_page.findAll('span', {'itemprop': 'recipeCategory'})[-1].findAll('a')[0].text.strip()
    else:
        category = "Десерты"

    # Получение спика ингредиентов
    list_of_ingredients = GetListOfIngredients(url)
    amount_of_ingredients = len(list_of_ingredients)
    is_milk = False
    if "Молоко" in list_of_ingredients:
        is_milk = True

    # Получение БЖУ на 100 граммов
    nutrients = []
    for i in range(7, 10):
        for x in recipe_page.findAll('div', {'itemprop': 'nutrition'}):
            nutrients.append(float(x.findAll('td')[i].findAll('strong')[0].text.split(' ')[0]))

    proteins = nutrients[0]
    fats = nutrients[1]
    carbons = nutrients[2]

    return author, date_of_publication, amount_of_views, category, amount_of_ingredients, is_milk, proteins, fats, carbons

# Словарь ссылок на страницы с конкретными рецептами
recipes_urls = {};
# Словарь с информацией о конкретном рецепте
recipes_info = {};

# Ссылка на страницу с рецептами
url = "https://www.povarenok.ru/recipes/category/30/~0"

# Цикл для перехода на следующую страницу
for i in range(1, 8):
    # Изменение адреса сайта для перехода на следующую страницу
    url = url[:-1]
    url += str(i)

    # Получение общей страницы
    page = BeautifulSoup(requests.get(url).text, 'html.parser')

    # Цикл по разделам превью рецептов (сбор ссылок)
    for recipe in page.findAll('article', {'class': 'item-bl'}):
        recipe_name = list(recipe.findAll('a'))[1].text;
        recipes_urls[recipe_name] = list(recipe.findAll('a'))[0]['href']
        recipes_info[recipe_name] = (None, None, None, None, None, None, None, None, None)

# Цикл по страницам рецептов
for recipe in recipes_urls:
    recipes_info[recipe] = GetInfoAboutRecipe(recipes_urls[recipe])
    time.sleep(2)

# Сохранение данных в датафрейм
df = pd.DataFrame(recipes_info).T
df.columns = ["Автор рецепта", "Дата публикации", "Количество просмотров", "Категория", "Количество ингредиентов", "Есть ли молоко", "Белки", "Жиры", "Углеводы"]
df.to_excel("Recipes.xlsx")
