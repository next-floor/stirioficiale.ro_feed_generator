# stirioficiale.ro_feed_generator
Utilitar pentru generarea unui feed rss/atom cu informatiile oficiale despre situatia COVID-19 din Romania

Importati feedul(rss sau atom) de la adresa localhost:5000/feed/[rss|atom] in readerul preferat

![alt text](https://raw.githubusercontent.com/next-floor/stirioficiale.ro_feed_generator/master/example.png)

## Instalare si rulare
Instalati dependintele si rulati aplicatia web

```
pip install -r requirements.txt
python runner.py
```

sau folositi fisierul Dockerfile pentru a rula aplicatia intr-un container Docker

```
docker build -t feeder/stirioficiale .
docker run -p 5000:5000 feeder/stirioficiale
