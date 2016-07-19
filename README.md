# Tic-Tac-Toe

- [Play Tic-Tac-Toe](http://game.badzyo.pp.ua) online vs humans!  
- Choose grid size and game rules that you like  
- Use in-game chat to communicate with your opponent  
- View games history and replays in your profile  
<br>

[![](misc/Screenshot.png?raw=true)]()  

_Looks better in Google Chrome ;)_


Install
=======
```
$ git clone https://github.com/Badzyo/tic-tac-toe.git
$ cd tic-tac-toe
$ python3 -m venv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
$ python manage.py db init
$ python manage.py db migrate
$ python manage.py db upgrade
```
Run
=====
```
$ python3 run.py
```

Powered by 
====
- Flask
- Tornado
- jQuery
- Websockets



Author
======
Denys Badzo  
https://badzyo.pp.ua  
denys.badzo@gmail.com