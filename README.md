# livecodingmusic

live coding music in python + supercollider

https://vimeo.com/627685761


## install


1. [install SuperCollider](https://supercollider.github.io/download)
2. [install SuperCollider extensions](https://supercollider.github.io/sc3-plugins/)
3. install python requirements:

```
python3 -m pip install -r requirements.txt
```

4. (optional) if using linux you can use tmuxp to easily start everything:

```
apt install tmux tmuxp
```

## run

1. first start JACK:

```
jackd -R -dalsa -dhw:0,0 -r 44100 -p256 -n3 -p1024 -O512
```

2. start SuperCollider:

```
sclang livecoding.sc
```


3. start the livecoding script:

```
python3 -m jurigged -v example.py
```

now edit `example.py` with the editor of your choice and on save it will update automatically.


optionally, if you are using tmux you can run everything at once and use vim to edit:

```
make music
```


## license

MIT