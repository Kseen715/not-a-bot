# N-A-B
<p align="center">
  <img src="https://github.com/Kseen715/imgs/blob/main/sakura_kharune.png?raw=true" width="160" height="160"/>
    &
  <img src="https://raw.githubusercontent.com/Kseen715/imgs/00b68ab912af709b492d889dba47cfa5e57f40fa/not-a-bot/not-a-bot_logo.svg" width="160" height="160"/>
</p>

## Description
This is musical Discord bot.

### Features
- `ping` - check connection to the server
- `radio [name]` - play direct radio stream from the lib
- `radiolist` - show lib of radiostations
- `stop` - stop whatever plays now
- `prune [count]` - delete [count] messages (admin only)
- `prunetime [time (XXdXXhXXmXXs)]` - delete messages that was sent in [time] period (admin only)
- `play` - (WIP) play audio from YT video

## Usage

### Docker-compose:

```
version: '3.8'
services:
  not-a-bot:
    image: kseen/not-a-bot:latest
    container_name: not-a-bot
    restart: unless-stopped
    environment:
      TOKEN: "<your Discord app token>"
      PREFIX: "<prefix for a bot, like '!', '>', '-' and etc.>"
```

### Raw python:

Install [FFmpeg](https://ffmpeg.org/download.html).

```
python3 pip install -r requirements.txt
```

Then create `.env` file with fields as:

```
TOKEN=<your Discord app token>
PREFIX=<prefix for a bot, like '!', '>', '-' and etc.>
```

Now you're ready to run app:

```
python3 main.py
```

### Python venv:

Install [FFmpeg](https://ffmpeg.org/download.html).

#### On Linux:

Create venv:
```
python3 -m venv venv
```

Activate venv:
```
venv\Scripts\activate
```

Update pip module inside of the venv (I use [pypa](https://github.com/pypa/get-pip) script):
```
curl -s https://bootstrap.pypa.io/get-pip.py -o get-pip.py && python get-pip.py && rm get-pip.py
```

Install all dependencies:
```
pip install -r requirements.txt --no-cache-dir --quiet
```

Run app:
```
python main.py
```

#### On Windows:

For the first run use `venv-setup.ps1`. It will create new venv and setup all needed stuff. Or to use already created run venv, use script `venv-run.ps1`. After that just run:
```
python main.py
```



