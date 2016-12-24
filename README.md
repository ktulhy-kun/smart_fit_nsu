# smart_fit_nsu
Новостная доска. Используются новости с сайта http://fit.nsu.ru  
Несколько раз в час с сайта ФИТ НГУ собираются новости и отображаются на сайте.  
Помимо самого текста новостей поддерживается тегирование каждой новости.  
Есть возможность просматривать новости с одним тегом.

TODO:  
* Telegram канал
* Поиск по тегам
* Облако тегов
* Поиск по тексту новостей
* Контакты разработчиков

## CI:
https://travis-ci.org/ktulhy-kun/smart_fit_nsu/branches  

## Heroku:
https://dashboard.heroku.com/apps/smart-fit-nsu  

## Jira:
https://ktulhykun.atlassian.net/secure/RapidBoard.jspa?rapidView=1&projectKey=SFN&view=planning.nodetail

## GitHub
https://github.com/ktulhy-kun/smart_fit_nsu

## Запуск на локальной машине
gunicorn manage:app
