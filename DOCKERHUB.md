# Docker container for Sharry
[![Release](https://img.shields.io/github/release/jlesage/docker-sharry.svg?logo=github&style=for-the-badge)](https://github.com/jlesage/docker-sharry/releases/latest)
[![Docker Image Size](https://img.shields.io/docker/image-size/jlesage/sharry/latest?logo=docker&style=for-the-badge)](https://hub.docker.com/r/jlesage/sharry/tags)
[![Docker Pulls](https://img.shields.io/docker/pulls/jlesage/sharry?label=Pulls&logo=docker&style=for-the-badge)](https://hub.docker.com/r/jlesage/sharry)
[![Docker Stars](https://img.shields.io/docker/stars/jlesage/sharry?label=Stars&logo=docker&style=for-the-badge)](https://hub.docker.com/r/jlesage/sharry)
[![Build Status](https://img.shields.io/github/actions/workflow/status/jlesage/docker-sharry/build-image.yml?logo=github&branch=master&style=for-the-badge)](https://github.com/jlesage/docker-sharry/actions/workflows/build-image.yml)
[![Source](https://img.shields.io/badge/Source-GitHub-blue?logo=github&style=for-the-badge)](https://github.com/jlesage/docker-sharry)
[![Donate](https://img.shields.io/badge/Donate-PayPal-green.svg?style=for-the-badge)](https://paypal.me/JocelynLeSage)

This is a Docker container for [Sharry](https://eikek.github.io/sharry/).



---

[![Sharry logo](https://images.weserv.nl/?url=raw.githubusercontent.com/jlesage/docker-templates/master/jlesage/images/sharry-icon.png&w=110)](https://eikek.github.io/sharry/)[![Sharry](https://images.placeholders.dev/?width=192&height=110&fontFamily=monospace&fontWeight=400&fontSize=52&text=Sharry&bgColor=rgba(0,0,0,0.0)&textColor=rgba(121,121,121,1))](https://eikek.github.io/sharry/)

Sharry allows to share files with others in a simple way. It is a self-hosted web
application. The basic concept is: upload files and get a url back that can then
be shared.

---

## Quick Start

**NOTE**:
    The Docker command provided in this quick start is given as an example
    and parameters should be adjusted to your need.

Launch the Sharry docker container with the following command:
```shell
docker run -d \
    --name=sharry \
    -p 9090:9090 \
    -v /docker/appdata/sharry:/config:rw \
    jlesage/sharry
```

Where:

  - `/docker/appdata/sharry`: This is where the application stores its configuration, states, log and any files needing persistency.

Browse to `http://your-host-ip:9090` to access the Sharry web interface.

## Documentation

Full documentation is available at https://github.com/jlesage/docker-sharry.

## Support or Contact

Having troubles with the container or have questions?  Please
[create a new issue].

For other great Dockerized applications, see https://jlesage.github.io/docker-apps.

[create a new issue]: https://github.com/jlesage/docker-sharry/issues
