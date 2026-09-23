# Minecraft Server Status Bot

Ein Discord-Bot, den ich gebaut habe, um einen Minecraft-Server im Blick zu behalten. Er postet eine Nachricht in Discord, die zeigt ob der Server online oder offline ist, wie viele Spieler drauf sind und welche Version läuft. Man muss also keine Website checken oder den Server selbst anpingen, der Bot aktualisiert die Nachricht einfach jede Minute von selbst.

English version: README.md

## Was der Bot macht

Man gibt einen Befehl ein und der Bot richtet alles automatisch ein:

- erstellt einen Textkanal namens #server-activity
- erstellt eine Rolle, die steuert wer diesen Kanal sehen kann
- postet eine Nachricht mit dem Serverstatus in den Kanal
- aktualisiert diese eine Nachricht alle 60 Sekunden, statt ständig neue zu schicken
- speichert die Serveradresse in einer Datenbank, damit sie nach einem Neustart nicht verloren geht

Das funktioniert auch pro Discord-Server, das heißt wenn man den Bot auf mehreren Servern hat, kann jeder davon einen anderen Minecraft-Server tracken.

## Befehle

!setup <host> [port] - nur für Admins, richtet Kanal und Rolle ein und startet das Tracking für den angegebenen Server. Wenn man keinen Port angibt, wird 25565 genutzt.

!info - gibt einem selbst die Rolle, damit man den Status-Kanal sehen kann.

## Womit es gebaut ist

- Python 3.12
- discord.py für den Bot selbst, mit tasks.loop aus discord.ext für die Update-Schleife im Hintergrund
- mcstatus um den Minecraft-Server tatsächlich abzufragen
- sqlite3 um Serveradresse, Channel-ID, Rollen-ID usw. pro Discord-Server zu speichern
- python-dotenv damit der Bot-Token nicht fest im Code steht

## Installation

Repo klonen und Abhängigkeiten installieren:

```
git clone https://github.com/deinname/deinrepo.git
cd deinrepo
python -m venv venv
venv\Scripts\activate   (oder source venv/bin/activate auf mac/linux)
pip install -r requirements.txt
```

Dann im Discord Developer Portal (discord.com/developers/applications) eine Bot-Anwendung erstellen, den Token kopieren und unter dem Bot-Tab folgende Intents aktivieren:
- message content intent
- server members intent

Beim Einladen über OAuth2 braucht der Bot diese Berechtigungen: manage roles, manage channels, send messages, read message history.

Im Projektordner eine .env Datei anlegen mit:

```
DISCORD_TOKEN=dein_token_hier
```

Dann einfach starten mit:

```
python bot.py
```

Die Datenbankdatei wird beim ersten Start automatisch erstellt.

## Wie die Update-Schleife funktioniert

Alle 60 Sekunden geht der Bot alle gespeicherten Server durch (aus der Datenbank), fragt jeden mit mcstatus ab und bearbeitet die vorhandene Statusnachricht, statt eine neue zu senden. Wenn ein Server offline oder nicht erreichbar ist, wird das nur für diesen einen angezeigt, der Rest läuft trotzdem normal weiter.

## Was noch fehlt / was ich noch machen will

- ein Befehl um das Setup wieder zu entfernen (aktuell erstellt !setup beim zweiten Ausführen einfach eine zweite Rolle und einen zweiten Kanal, es gibt kein Aufräumen)

## Warum ich das gemacht habe

Ich bin in der 10. Klasse in Deutschland und suche eine Ausbildung als Softwareentwickler in Berlin. Ich wollte etwas für mein Portfolio haben, das wirklich von Anfang bis Ende funktioniert, mit einer externen API kommuniziert, im Hintergrund läuft, Daten speichert und mit Discord-Rechten und Rollen umgeht.

## Lizenz

MIT, damit kann jeder machen was er will.
