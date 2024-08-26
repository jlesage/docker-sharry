# Docker container for Sharry
[![Release](https://img.shields.io/github/release/jlesage/docker-sharry.svg?logo=github&style=for-the-badge)](https://github.com/jlesage/docker-sharry/releases/latest)
[![Docker Image Size](https://img.shields.io/docker/image-size/jlesage/sharry/latest?logo=docker&style=for-the-badge)](https://hub.docker.com/r/jlesage/sharry/tags)
[![Docker Pulls](https://img.shields.io/docker/pulls/jlesage/sharry?label=Pulls&logo=docker&style=for-the-badge)](https://hub.docker.com/r/jlesage/sharry)
[![Docker Stars](https://img.shields.io/docker/stars/jlesage/sharry?label=Stars&logo=docker&style=for-the-badge)](https://hub.docker.com/r/jlesage/sharry)
[![Build Status](https://img.shields.io/github/actions/workflow/status/jlesage/docker-sharry/build-image.yml?logo=github&branch=master&style=for-the-badge)](https://github.com/jlesage/docker-sharry/actions/workflows/build-image.yml)
[![Donate](https://img.shields.io/badge/Donate-PayPal-green.svg?style=for-the-badge)](https://paypal.me/JocelynLeSage)

This project implements a Docker container for [Sharry](https://eikek.github.io/sharry/).



---

[![Sharry logo](https://images.weserv.nl/?url=raw.githubusercontent.com/jlesage/docker-templates/master/jlesage/images/sharry-icon.png&w=110)](https://eikek.github.io/sharry/)[![Sharry](https://images.placeholders.dev/?width=192&height=110&fontFamily=monospace&fontWeight=400&fontSize=52&text=Sharry&bgColor=rgba(0,0,0,0.0)&textColor=rgba(121,121,121,1))](https://eikek.github.io/sharry/)

Sharry allows to share files with others in a simple way. It is a self-hosted web
application. The basic concept is: upload files and get a url back that can then
be shared.

---

## Table of Content

   * [Quick Start](#quick-start)
   * [Usage](#usage)
      * [Environment Variables](#environment-variables)
         * [Deployment Considerations](#deployment-considerations)
      * [Data Volumes](#data-volumes)
      * [Ports](#ports)
      * [Changing Parameters of a Running Container](#changing-parameters-of-a-running-container)
   * [Docker Compose File](#docker-compose-file)
   * [Docker Image Versioning](#docker-image-versioning)
   * [Docker Image Update](#docker-image-update)
      * [Synology](#synology)
      * [unRAID](#unraid)
   * [User/Group IDs](#usergroup-ids)
   * [Accessing the GUI](#accessing-the-gui)
   * [Shell Access](#shell-access)
   * [Built-in Administrator Account](#built-in-administrator-account)
   * [Customizing Sharry Configuration](#customizing-sharry-configuration)
      * [Configuration File](#configuration-file)
      * [Environment Variables](#environment-variables-1)
   * [Exposing Sharry to the Internet](#exposing-sharry-to-the-internet)
   * [Support or Contact](#support-or-contact)

## Quick Start

> [!IMPORTANT]
> The Docker command provided in this quick start is given as an example and
> parameters should be adjusted to your need.

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

## Usage

```shell
docker run [-d] \
    --name=sharry \
    [-e <VARIABLE_NAME>=<VALUE>]... \
    [-v <HOST_DIR>:<CONTAINER_DIR>[:PERMISSIONS]]... \
    [-p <HOST_PORT>:<CONTAINER_PORT>]... \
    jlesage/sharry
```

| Parameter | Description |
|-----------|-------------|
| -d        | Run the container in the background. If not set, the container runs in the foreground. |
| -e        | Pass an environment variable to the container. See the [Environment Variables](#environment-variables) section for more details. |
| -v        | Set a volume mapping (allows to share a folder/file between the host and the container). See the [Data Volumes](#data-volumes) section for more details. |
| -p        | Set a network port mapping (exposes an internal container port to the host). See the [Ports](#ports) section for more details. |

### Environment Variables

To customize some properties of the container, the following environment
variables can be passed via the `-e` parameter (one for each variable). Value
of this parameter has the format `<VARIABLE_NAME>=<VALUE>`.

| Variable       | Description                                  | Default |
|----------------|----------------------------------------------|---------|
|`USER_ID`| ID of the user the application runs as.  See [User/Group IDs](#usergroup-ids) to better understand when this should be set. | `1000` |
|`GROUP_ID`| ID of the group the application runs as.  See [User/Group IDs](#usergroup-ids) to better understand when this should be set. | `1000` |
|`SUP_GROUP_IDS`| Comma-separated list of supplementary group IDs of the application. | (no value) |
|`UMASK`| Mask that controls how permissions are set for newly created files and folders.  The value of the mask is in octal notation.  By default, the default umask value is `0022`, meaning that newly created files and folders are readable by everyone, but only writable by the owner.  See the online umask calculator at http://wintelguy.com/umask-calc.pl. | `0022` |
|`LANG`| Set the [locale](https://en.wikipedia.org/wiki/Locale_(computer_software)), which defines the application's language, **if supported**.  Format of the locale is `language[_territory][.codeset]`, where language is an [ISO 639 language code](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes), territory is an [ISO 3166 country code](https://en.wikipedia.org/wiki/ISO_3166-1#Current_codes) and codeset is a character set, like `UTF-8`.  For example, Australian English using the UTF-8 encoding is `en_AU.UTF-8`. | `en_US.UTF-8` |
|`TZ`| [TimeZone](http://en.wikipedia.org/wiki/List_of_tz_database_time_zones) used by the container.  Timezone can also be set by mapping `/etc/localtime` between the host and the container. | `Etc/UTC` |
|`KEEP_APP_RUNNING`| When set to `1`, the application will be automatically restarted when it crashes or terminates. | `0` |
|`APP_NICENESS`| Priority at which the application should run.  A niceness value of -20 is the highest priority and 19 is the lowest priority.  The default niceness value is 0.  **NOTE**: A negative niceness (priority increase) requires additional permissions.  In this case, the container should be run with the docker option `--cap-add=SYS_NICE`. | `0` |
|`INSTALL_PACKAGES`| Space-separated list of packages to install during the startup of the container.  List of available packages can be found at https://mirrors.alpinelinux.org.  **ATTENTION**: Container functionality can be affected when installing a package that overrides existing container files (e.g. binaries). | (no value) |
|`PACKAGES_MIRROR`| Mirror of the repository to use when installing packages. List of mirrors is available at https://mirrors.alpinelinux.org. | (no value) |
|`CONTAINER_DEBUG`| Set to `1` to enable debug logging. | `0` |
|`SHARRY_BACKEND_AUTH_FIXED_USER`| Username of the built-in administrator account. Setting this variable to an empty value disables this account. | `admin` |
|`SHARRY_BACKEND_AUTH_FIXED_PASSWORD`| Password of the built-in administrator account. Setting this variable to an empty value disables this account. | `changeme` |

#### Deployment Considerations

Many tools used to manage Docker containers extract environment variables
defined by the Docker image and use them to create/deploy the container. For
example, this is done by:
  - The Docker application on Synology NAS
  - The Container Station on QNAP NAS
  - Portainer
  - etc.

While this can be useful for the user to adjust the value of environment
variables to fit its needs, it can also be confusing and dangerous to keep all
of them.

A good practice is to set/keep only the variables that are needed for the
container to behave as desired in a specific setup. If the value of variable is
kept to its default value, it means that it can be removed. Keep in mind that
all variables are optional, meaning that none of them is required for the
container to start.

Removing environment variables that are not needed provides some advantages:

  - Prevents keeping variables that are no longer used by the container. Over
    time, with image updates, some variables might be removed.
  - Allows the Docker image to change/fix a default value. Again, with image
    updates, the default value of a variable might be changed to fix an issue,
    or to better support a new feature.
  - Prevents changes to a variable that might affect the correct function of
    the container. Some undocumented variables, like `PATH` or `ENV`, are
    required to be exposed, but are not meant to be changed by users. However,
    container management tools still show these variables to users.
  - There is a bug with the Container Station on QNAP and the Docker application
    on Synology, where an environment variable without value might not be
    allowed. This behavior is wrong: it's absolutely fine to have a variable
    without value. In fact, this container does have variables without value by
    default. Thus, removing unneeded variables is a good way to prevent
    deployment issue on these devices.

### Data Volumes

The following table describes data volumes used by the container. The mappings
are set via the `-v` parameter. Each mapping is specified with the following
format: `<HOST_DIR>:<CONTAINER_DIR>[:PERMISSIONS]`.

| Container path  | Permissions | Description |
|-----------------|-------------|-------------|
|`/config`| rw | This is where the application stores its configuration, states, log and any files needing persistency. |

### Ports

Here is the list of ports used by the container.

When using the default bridge network, ports can be mapped to the host via the
`-p` parameter (one per port mapping). Each mapping is defined with the
following format: `<HOST_PORT>:<CONTAINER_PORT>`. The port number used inside
the container might not be changeable, but you are free to use any port on the
host side.

See the [Docker Container Networking](https://docs.docker.com/config/containers/container-networking)
documentation for more details.

| Port | Protocol | Mapping to host | Description |
|------|----------|-----------------|-------------|
| 9090 | TCP | Mandatory | Port used to access the web interface of the application. |

### Changing Parameters of a Running Container

As can be seen, environment variables, volume and port mappings are all specified
while creating the container.

The following steps describe the method used to add, remove or update
parameter(s) of an existing container. The general idea is to destroy and
re-create the container:

  1. Stop the container (if it is running):
```shell
docker stop sharry
```

  2. Remove the container:
```shell
docker rm sharry
```

  3. Create/start the container using the `docker run` command, by adjusting
     parameters as needed.

> [!NOTE]
> Since all application's data is saved under the `/config` container folder,
> destroying and re-creating a container is not a problem: nothing is lost and
> the application comes back with the same state (as long as the mapping of the
> `/config` folder remains the same).

## Docker Compose File

Here is an example of a `docker-compose.yml` file that can be used with
[Docker Compose](https://docs.docker.com/compose/overview/).

Make sure to adjust according to your needs. Note that only mandatory network
ports are part of the example.

```yaml
version: '3'
services:
  sharry:
    image: jlesage/sharry
    ports:
      - "9090:9090"
    volumes:
      - "/docker/appdata/sharry:/config:rw"
```

## Docker Image Versioning

Each release of a Docker image is versioned. Prior to october 2022, the
[semantic versioning](https://semver.org) was used as the versioning scheme.

Since then, versioning scheme changed to
[calendar versioning](https://calver.org). The format used is `YY.MM.SEQUENCE`,
where:
  - `YY` is the zero-padded year (relative to year 2000).
  - `MM` is the zero-padded month.
  - `SEQUENCE` is the incremental release number within the month (first release
    is 1, second is 2, etc).

## Docker Image Update

Because features are added, issues are fixed, or simply because a new version
of the containerized application is integrated, the Docker image is regularly
updated. Different methods can be used to update the Docker image.

The system used to run the container may have a built-in way to update
containers. If so, this could be your primary way to update Docker images.

An other way is to have the image be automatically updated with [Watchtower].
Watchtower is a container-based solution for automating Docker image updates.
This is a "set and forget" type of solution: once a new image is available,
Watchtower will seamlessly perform the necessary steps to update the container.

Finally, the Docker image can be manually updated with these steps:

  1. Fetch the latest image:
```shell
docker pull jlesage/sharry
```

  2. Stop the container:
```shell
docker stop sharry
```

  3. Remove the container:
```shell
docker rm sharry
```

  4. Create and start the container using the `docker run` command, with the
the same parameters that were used when it was deployed initially.

[Watchtower]: https://github.com/containrrr/watchtower

### Synology

For owners of a Synology NAS, the following steps can be used to update a
container image.

  1.  Open the *Docker* application.
  2.  Click on *Registry* in the left pane.
  3.  In the search bar, type the name of the container (`jlesage/sharry`).
  4.  Select the image, click *Download* and then choose the `latest` tag.
  5.  Wait for the download to complete. A notification will appear once done.
  6.  Click on *Container* in the left pane.
  7.  Select your Sharry container.
  8.  Stop it by clicking *Action*->*Stop*.
  9.  Clear the container by clicking *Action*->*Reset* (or *Action*->*Clear* if
      you don't have the latest *Docker* application). This removes the
      container while keeping its configuration.
  10. Start the container again by clicking *Action*->*Start*. **NOTE**:  The
      container may temporarily disappear from the list while it is re-created.

### unRAID

For unRAID, a container image can be updated by following these steps:

  1. Select the *Docker* tab.
  2. Click the *Check for Updates* button at the bottom of the page.
  3. Click the *update ready* link of the container to be updated.

## User/Group IDs

When using data volumes (`-v` flags), permissions issues can occur between the
host and the container. For example, the user within the container may not
exist on the host. This could prevent the host from properly accessing files
and folders on the shared volume.

To avoid any problem, you can specify the user the application should run as.

This is done by passing the user ID and group ID to the container via the
`USER_ID` and `GROUP_ID` environment variables.

To find the right IDs to use, issue the following command on the host, with the
user owning the data volume on the host:

    id <username>

Which gives an output like this one:
```text
uid=1000(myuser) gid=1000(myuser) groups=1000(myuser),4(adm),24(cdrom),27(sudo),46(plugdev),113(lpadmin)
```

The value of `uid` (user ID) and `gid` (group ID) are the ones that you should
be given the container.

## Accessing the GUI

Assuming that container's ports are mapped to the same host's ports, the
interface of the application can be accessed with a web browser at:

```text
http://<HOST IP ADDR>:9090
```

## Shell Access

To get shell access to the running container, execute the following command:

```shell
docker exec -ti CONTAINER sh
```

Where `CONTAINER` is the ID or the name of the container used during its
creation.

## Built-in Administrator Account

By default, Sharry comes with a built-in administrator account,
with credentials defined by the following environment variables:

| Variable                             | Description | Default Value |
|--------------------------------------|-------------|---------------|
| `SHARRY_BACKEND_AUTH_FIXED_USER`     | Username    | `admin`       |
| `SHARRY_BACKEND_AUTH_FIXED_PASSWORD` | Password    | `changeme`    |

This account can be used to login to the web interface of Sharry.

> [!CAUTION]
> For security reason, it is strongly recommended to set a strong password. Do
> not use the default one!

If not needed, this account can be disabled by setting any of these two
variables to an empty value.

## Customizing Sharry Configuration

Sharry configuration can be customized via two methods:
  1. Environment variables.
  2. Configuration file.

All configuration parameters supported by Sharry can be consulted
at https://eikek.github.io/sharry/doc/configure

### Configuration File

The configuration file of Sharry is located at
`/config/sharry.conf` inside the container. It can be adjusted directly as
needed.

### Environment Variables

Container environment variables can be used to override values from the config
file. Variable names always start with `SHARRY_` and the remainder can be
derived from the corresponding config option by replacing period `.` and dash
`-` characters by an underscore `_`, but excluding the root namespace
`sharry.restserver`. For example, the config option
`sharry.restserver.bind.port` would be `SHARRY_BIND_PORT` as environment
variable. A value given as environment variable has priority.

## Exposing Sharry to the Internet

Sharry cannot be exposed directly to the Internet. Features
required to allow this is out of scope for Sharry. Instead, it
should run behind a reverse proxy. A reverse proxy can offer a secure access via
HTTPs to the web interface, while also providing a valid certificate that can be
verified by browsers.

See https://eikek.github.io/sharry/doc/reverseproxy for more details.

## Support or Contact

Having troubles with the container or have questions?  Please
[create a new issue].

For other great Dockerized applications, see https://jlesage.github.io/docker-apps.

[create a new issue]: https://github.com/jlesage/docker-sharry/issues
