from pprint import pprint
from bs4 import BeautifulSoup as bs
import requests
import re
import json
from Lesson_3_HW.db_Mongo import db_save
from Lesson_3_HW.db_Mongo import find_wish_salary
from Lesson_3_HW.db_Mongo import update_vacancies

#Запрашиваем вакансию

search_vacancy = input('Вакансия для поиска: ')

start_url_hh = 'https://ekaterinburg.hh.ru/search/vacancy'
headers = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'}

params = {'text' : search_vacancy}

#hh
response = requests.get(start_url_hh,headers=headers, params=params).text
html = bs(response, 'lxml')

#Последняя страница
finish_block = html.findAll('span', {'class', 'pager-item-not-in-short-range'})[2]
finish_page = int(finish_block.find('a', {'class', 'bloko-button HH-Pager-Control'}).getText())

#Функция для парсинга hh
def parse_hh(search_vacancy, finish_page):
    pages = [i for i in range(finish_page)]
    vacancies = []
    for page in pages:
        start_url = 'https://ekaterinburg.hh.ru/search/vacancy'
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'}

        params = {'text': search_vacancy, 'page':page}

        response = requests.get(start_url, headers=headers, params=params).text
        html = bs(response, 'lxml')

        vacancy_block = html.find('div', {'class': 'vacancy-serp'})
        vacancy_list = vacancy_block.findAll('div', {'class':'vacancy-serp-item'})


        for vacancy in vacancy_list:
            vacancy_data = {}
            main_info = vacancy.find('div', {'class' : 'resume-search-item__name'})
            main_info_link = main_info.find('a', {'class' : 'bloko-link HH-LinkModifier'})
            vacancy_title = main_info_link.getText()
            vacancy_link = main_info_link['href']
            salary = vacancy.find('div', {'class' : 'vacancy-serp-item__compensation'})
            if not salary:
                min = None
                max = None
                currency = None

            else:
                salary = salary.getText().replace(u'\xa0', '')

                if re.search('-', salary):
                    salary = salary.split('-')
                    min = salary[0]

                    max = salary[1].split()[0]
                    currency = salary[1].split()[1]

                elif re.search('от', salary):
                    min = int((re.findall(r'\d+', salary))[0])
                    max = None
                    currency = salary.split()[2]

                else:
                    min = None
                    max = int((re.findall(r'\d+', salary))[0])
                    currency = salary.split()[2]

            vacancy_data['title'] = vacancy_title
            vacancy_data['link'] = vacancy_link
            vacancy_data['min'] = min
            vacancy_data['max'] = max
            vacancy_data['currency'] = currency
            vacancy_data['site'] = 'hh'
            vacancies.append(vacancy_data)
    return vacancies
result_hh = parse_hh(search_vacancy, finish_page)

start_url_sj = 'https://www.superjob.ru/vacancy/search/?geo%5Bc%5D%5B0%5D=1'
params = {'keywords': search_vacancy}

response = requests.get(start_url_sj, params=params).text
html = bs(response, 'lxml')

vacancy_list = html.findAll('div', {'class':'_3zucV _2GPIV f-test-vacancy-item i6-sc _3VcZr'})
try:
    finish_page = int(html.findAll('span', {'class' : '_3IDf-'})[-3].getText())
except ValueError:
    finish_page = 1

def parse_sj(search_vacancy, finish_page, vacancies):
    pages = [i for i in range(1, finish_page+1)]
    for page in pages:
        start_url = 'https://www.superjob.ru/vacancy/search/?geo%5Bc%5D%5B0%5D=1'
        params = {'keywords': search_vacancy, 'page': page}
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'}

        response = requests.get(start_url, headers=headers, params=params).text
        html = bs(response, 'lxml')

        vacancy_list = html.findAll('div', {'class': '_3zucV _2GPIV f-test-vacancy-item i6-sc _3VcZr'})

        for item in vacancy_list:
            vacancy_data = {}
            vacancy_title = item.find('div', {'class':'_3mfro CuJz5 PlM3e _2JVkc _3LJqf'}).getText()
            main_link = 'https://superjob.ru'
            vacancy_link = main_link + item.find('a', {'class':'_1QIBo'})['href']
            salary = item.find('span', {'class': '_3mfro _2Wp8I f-test-text-company-item-salary PlM3e _2JVkc _2VHxz'}).getText()
            if re.search('—', salary):
                salary_ = salary.split('—')
                min_ = salary_[0].replace(u'\xa0', '')
                max_ = int(re.findall(r'\d+',(salary_[1].replace(u'\xa0', '')))[0])

            elif re.search('По договорённости', salary):
                min_ = 'По договорённости'
                max_ = 'По договорённости'

            elif re.search('от', salary):
                salary_ = salary.replace(u'\xa0', '')
                min_ = int(re.findall(r'\d+', salary_)[0])
                max_ = None

            else:
                salary_ = salary.replace(u'\xa0', '')
                min_ = None
                max_ = int(re.findall(r'\d+', salary_)[0])
            vacancy_data['title'] = vacancy_title
            vacancy_data['link'] = vacancy_link
            vacancy_data['min'] = min_
            vacancy_data['max'] = max_
            vacancy_data['currency'] = 'Рубли'
            vacancy_data['site'] = 'sj'
            vacancies.append(vacancy_data)
    return vacancies

result = parse_sj(search_vacancy, finish_page, result_hh)
data_json = json.dumps(result)
data = json.loads(data_json)
pprint(data)

#Сохранение в БД Mongo
# db_save(data)

#Поиск и печать вакансий с желаемой зп
find_wish_salary(30000)
#
# #Добавление новых
for obj in data:
    update_vacancies(obj)