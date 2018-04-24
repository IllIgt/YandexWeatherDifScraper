
# coding: utf-8

import requests
import json
import time
from lxml import html
from datetime import datetime, timedelta
from http.server import BaseHTTPRequestHandler, HTTPServer

#
# класс простейшего сервера


class HttpProcessor(BaseHTTPRequestHandler):

    def get_results(self):
        #По Xpath парсим страницу, собираем данные в result
        results = []
        weather_request = requests.get('https://yandex.ru/pogoda/moscow')
        html_doc = weather_request.text
        tree = html.fromstring(html_doc)
        days_list = tree.xpath("//div[@class='forecast-briefly__days']/div")
        for day_prediction in days_list:
            prediction = day_prediction.xpath(".//span[@class = 'temp__value']/text()")[0]
            date = day_prediction.xpath('.//time/text()')[0]
            results.append(
                           {
                           "date":date,
                           "prediction":prediction
                           })
        #переводим result на грядущие 7 дней в Json и сохраняем в текущей директории
        with open('weather_data_'+ datetime.strftime(datetime.now(), "%m.%d")+'.json', 'w') as json_file:
            json.dump(results[:-2], json_file, ensure_ascii=False, separators=(',', ':'))

    def json_parser(self):
        message_box = []
        current_date = datetime.strftime(datetime.now(), "%m.%d")
        current_json_file = 'weather_data_'+ current_date
            #берем данные из Json сегодняшнего дня
        with open(current_json_file+'.json','r') as current_json:
            current_prediction = json.load(current_json)[0]["prediction"]
        #
        #перебираем последние 7 Json от текущего по datetime и находим в них
        #данные о текущем дне. Формируем MessageBox для вывода
        i = 1;
        while i <= 7:
            target_date = datetime.strftime(datetime.strptime(current_json_file[-5:], "%m.%d")-timedelta(days=i),"%m.%d")
            try:
                with open('weather_data_'+target_date+ '.json','r') as target_json:
                    target_file = json.load(target_json)
                    target_prediction = target_file[i]["prediction"]
                percents = (int(current_prediction) - int(target_prediction))/(int(current_prediction)/100)
                message_box.append("Prediction date {0} (Days passed {1}) differs by {2}%".format(target_date, i, percents))
            except Exception:
                message_box.append("FileException")
            i+=1
        return (message_box)
            
        #очень хочется спать, поэтому while true скрапим, парсим, выводим в браузер,
        #В иделаьном мире - добавить таймер, по таймеру вызывать событие и сохранять в лог
    def start_messaging(self):
        i = 1
        while True:
            i+=100
            self.get_results()
            messages = self.json_parser()
            for message in messages:
                self.wfile.write(message.encode())
            time.sleep(3600*24)

    def do_GET(self):
        self.send_response(200)
        self.send_header('content-type', 'text/html')
        self.end_headers()
        self.wfile.write("Server Started".encode())
        self.start_messaging()
        


ParserSrv = HTTPServer(("127.0.0.1", 80), HttpProcessor)
ParserSrv.serve_forever()





