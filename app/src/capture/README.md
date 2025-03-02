# Capture

## Create a capture

Manually:

``` 
mosquitto_pub -h localhost -t /cmd/capture -m "{\"action\":\"START\", \"name\":\"test\"}"
```

``` 
mosquitto_pub -h localhost -t /cmd/capture -m "{\"action\":\"STOP\"}"
```

``` 
mosquitto_pub -h localhost -t /cmd/capture -m "{\"action\":\"STORE\"}"
```


## Play a capture

``` 
python play_capture.py --capture-file capture/DANCE.cap
``` 