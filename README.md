# UKW

![](logo.png)

A containerized *U*ptime *K*uma *W*rapper for [uptime-kuma-api](https://github.com/lucasheld/uptime-kuma-api).

It has one single endpoint and purpose: UKW looks through all monitors set up in an Uptime Kuma installation and returns "200, all up" if *all* are returning "UP" status. That's all folks.

Note: For UKW to work, Uptime Kuma needs to be set up with authentication disabled! (I'm runnning my Uptime Kuma in a private [tailscale](https://tailscale.com/) net.)

(In German, "UKW" stands for Very High Frequency. Hence, the logo.)

Disclaimer: I used ChatGPT to create logo and code.

## Usage

Hint: You can customize your Uptime Kuma URL by running `echo "UPTIME_KUMA_URL=https://status.example.com" > .env`

Build & run:

```bash
make build
make run
```

Browse to http://localhost:5000/status/all (default).

## References

- https://uptime-kuma-api.readthedocs.io/en/
- https://hub.docker.com/_/python/