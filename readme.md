# AF Transfer Bot

Данный бот позволяет пересылать файлы из Telegram в ICQ и обратно(скоро).

### Рекомендуемые системные требования

- Python 3.8+
- Ubuntu 18.04+
- Windows 10+
- MacOS 10.15+

## Установка и запуск

1. Скачайте и установите [Python](https://python.org) или `apt install python3 python3-pip`.
2. Скачайте репозиторий
3. Установите зависимости: `pip install requements.txt` или `pip3 install requements.txt`.
4. Введите команду: `cd bot-python-icq; python setup.py install` или `cd bot-python-icq; python3 setup.py install`.
5. Для запуска рекомендуется использовать [PM2](https://pm2.keymetrics.io/)
6. Добавьте ваши данные в файл `config.py`
7. Установите NPM и PM2: `apt update; apt install -y npm; npm install pm2 -g`
8. Запустите телеграм бота: `pm2 start main.py --interpreter python3 --name "TG Transfer Bot"`
9. Запустите ICQ бота: `pm2 start icq.py --interpreter python3 --name "ICQ Transfer Bot"`
10. Для автозапуска ботов при перезагрузке сервера: `pm2 startup; pm2 save`
11. 5-10 пункты для Ubuntu 18.04, для Windows 10 можно пропустить.
12. На Windows 10 можно запустить бота через `python main.py` и `python icq.py`

### Контакты
Telegram: [@lunatik_cyber](https://t.me/lunatik_cyber)  
Почта: astrofic.guru@gmail.com

### Донат
**BTC**: _bc1q9qtm3vlq6kwz0lu29d9hn3yph9l900wq6hkwhr_  
**ETH**: _0xD1Ed6545257dC6D7B84211Aa4ffaDD52F271ce1F_  
**TRX**: _TCCCaKnky8gu7XXZpvtLQsTqwLkDv3cNbb_

