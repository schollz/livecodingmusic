# livecoding.py
live coding in python + supercollider

## install

```
python3 -m pip install -r requirements.txt
```


## run

```
python3 -m jurigged -v livecoding.py
```

my own notes. using a USB audio device on Linux required setting up JACK manually using `hw:1` instead of `hw:0`:

```
jackd -R -dalsa -dhw:1,0 -r 44100 -p256 -n3 -p1024 -O512
```