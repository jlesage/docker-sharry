# Docker container for Sharry
[![Release](https://img.shields.io/github/release/jlesage/docker-sharry.svg?logo=github&style=for-the-badge)](https://github.com/jlesage/docker-sharry/releases/latest)
[![Docker Image Size](https://img.shields.io/docker/image-size/jlesage/sharry/latest?logo=docker&style=for-the-badge)](https://hub.docker.com/r/jlesage/sharry/tags)
[![Docker Pulls](https://img.shields.io/docker/pulls/jlesage/sharry?label=Pulls&logo=docker&style=for-the-badge)](https://hub.docker.com/r/jlesage/sharry)
[![Docker Stars](https://img.shields.io/docker/stars/jlesage/sharry?label=Stars&logo=docker&style=for-the-badge)](https://hub.docker.com/r/jlesage/sharry)
[![Build Status](https://img.shields.io/github/actions/workflow/status/jlesage/docker-sharry/build-image.yml?logo=github&branch=master&style=for-the-badge)](https://github.com/jlesage/docker-sharry/actions/workflows/build-image.yml)
[![Donate](https://img.shields.io/badge/Donate-PayPal-green.svg?style=for-the-badge)](https://paypal.me/JocelynLeSage)

This project provides a lightweight and secure Docker container for
[Sharry](https://eikek.github.io/sharry/).

> [!NOTE]
> This Docker container is entirely unofficial and not made by the creators of
> Sharry.

---

[![Sharry logo](https://images.weserv.nl/?url=raw.githubusercontent.com/jlesage/docker-templates/master/jlesage/images/sharry-icon.png&w=110)](https://eikek.github.io/sharry/)[![Sharry](https://images.placeholders.dev/?width=192&height=110&fontFamily=monospace&fontWeight=400&fontSize=52&text=Sharry&bgColor=rgba(0,0,0,0.0)&textColor=rgba(121,121,121,1))](https://eikek.github.io/sharry/)

Sharry allows to share files with others in a simple way. It is a self-hosted web
application. The basic concept is: upload files and get a url back that can then
be shared.

---

## Table of Contents

   * [Quick Start](#quick-start)
   * [Usage](#usage)
      * [Environment Variables](#environment-variables)
         * [Deployment Considerations](#deployment-considerations)
      * [Data Volumes](#data-volumes)
      * [Ports](#ports)
      * [Changing Parameters of a Running Container](#changing-parameters-of-a-running-container)
      * [Docker Compose File](#docker-compose-file)
   * [Docker Image Versioning and Tags](#docker-image-versioning-and-tags)
   * [Docker Image Update](#docker-image-update)
      * [Synology](#synology)
      * [unRAID](#unraid)
   * [User/Group IDs](#usergroup-ids)
   * [Shell Access](#shell-access)
   * [Accessing the GUI](#accessing-the-gui)
   * [Built-in Administrator Account](#built-in-administrator-account)
   * [Customizing Sharry Configuration](#customizing-sharry-configuration)
      * [Configuration File](#configuration-file)
      * [Environment Variables](#environment-variables-1)
   * [Exposing Sharry to the Internet](#exposing-sharry-to-the-internet)
   * [Support or Contact](#support-or-contact)

## Quick Start

> [!IMPORTANT]
> The Docker command provided in this quick start is an example, and parameters
> should be adjusted to suit your needs.

Launch the Sharry docker container with the following command:

```shell
docker run -d \
    --name=sharry \
    -p 9090:9090 \
    -v /docker/appdata/sharry:/config:rw \
    jlesage/sharry
```

Where:

  - `/docker/appdata/sharry`: Stores the application's configuration, state, logs, and any files requiring persistency.

Access the Sharry GUI by browsing to `http://your-host-ip:9090`.

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
| -d        | Runs the container in the background. If not set, the container runs in the foreground. |
| -e        | Passes an environment variable to the container. See [Environment Variables](#environment-variables) for details. |
| -v        | Sets a volume mapping to share a folder or file between the host and the container. See [Data Volumes](#data-volumes) for details. |
| -p        | Sets a network port mapping to expose an internal container port to the host). See [Ports](#ports) for details. |

### Environment Variables

To customize the container's behavior, you can pass environment variables using
the `-e` parameter in the format `<VARIABLE_NAME>=<VALUE>`.

| Variable       | Description                                  | Default |
|----------------|----------------------------------------------|---------|
|`USER_ID`| ID of the user the application runs as. See [User/Group IDs](#usergroup-ids) for details. | `1000` |
|`GROUP_ID`| ID of the group the application runs as. See [User/Group IDs](#usergroup-ids) for details. | `1000` |
|`SUP_GROUP_IDS`| Comma-separated list of supplementary group IDs for the application. | (no value) |
|`UMASK`| Mask controlling permissions for newly created files and folders, specified in octal notation. By default, `0022` ensures files and folders are readable by all but writable only by the owner. See the umask calculator at http://wintelguy.com/umask-calc.pl. | `0022` |
|`LANG`| Sets the [locale](https://en.wikipedia.org/wiki/Locale_(computer_software)), defining the application's language, if supported. Format is `language[_territory][.codeset]`, where language is an [ISO 639 language code](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes), territory is an [ISO 3166 country code](https://en.wikipedia.org/wiki/ISO_3166-1#Current_codes), and codeset is a character set, like `UTF-8`. For example, Australian English using UTF-8 is `en_AU.UTF-8`. | `en_US.UTF-8` |
|`TZ`| [TimeZone](http://en.wikipedia.org/wiki/List_of_tz_database_time_zones) used by the container. The timezone can also be set by mapping `/etc/localtime` between the host and the container. | `Etc/UTC` |
|`KEEP_APP_RUNNING`| When set to `1`, the application is automatically restarted if it crashes or terminates. | `0` |
|`APP_NICENESS`| Priority at which the application runs. A niceness value of `-20` is the highest, `19` is the lowest and `0` the default. **NOTE**: A negative niceness (priority increase) requires additional permissions. The container must be run with the Docker option `--cap-add=SYS_NICE`. | `0` |
|`INSTALL_PACKAGES`| Space-separated list of packages to install during container startup. List of available packages can be found at https://pkgs.alpinelinux.org. | (no value) |
|`PACKAGES_MIRROR`| Mirror of the repository to use when installing packages. List of mirrors is available at https://mirrors.alpinelinux.org. | (no value) |
|`CONTAINER_DEBUG`| When set to `1`, enables debug logging. | `0` |
|`SHARRY_BASE_URL`| The external URL where Sharry can be reached (e.g. `https://sharry.example.com`). This is used to create absolute URLs and to configure the authentication cookie. These URLs are sent to the client, so they must resolve back to the Sharry server. If "network error" error messages are seen in the browser, then this setting is probably not correct. If the default value is used, the external URL is obtained dynamically by inspecting HTTP headers of the request. | `http://localhost:9090` |
|`SHARRY_BACKEND_AUTH_FIXED_USER`| Username of the built-in administrator account. Setting this variable to an empty value disables this account. | `admin` |
|`SHARRY_BACKEND_AUTH_FIXED_PASSWORD`| Password of the built-in administrator account. Setting this variable to an empty value disables this account. | `changeme` |

#### Deployment Considerations

Many tools used to manage Docker containers extract environment variables
defined by the Docker image to create or deploy the container.

For example, this behavior is seen in:
  - The Docker application on Synology NAS
  - The Container Station on QNAP NAS
  - Portainer
  - etc.

While this is useful for users to adjust environment variable values to suit
their needs, keeping all of them can be confusing and even risky.

A good practice is to set or retain only the variables necessary for the
container to function as desired in your setup. If a variable is left at its
default value, it can be removed. Keep in mind that all environment variables
are optional; none are required for the container to start.

Removing unneeded environment variables offers several benefits:

  - Prevents retaining variables no longer used by the container. Over time,
    with image updates, some variables may become obsolete.
  - Allows the Docker image to update or fix default values. With image updates,
    default values may change to address issues or support new features.
  - Avoids changes to variables that could disrupt the container's
    functionality. Some undocumented variables, like `PATH` or `ENV`, are
    required but not meant to be modified by users, yet container management
    tools may expose them.
  - Addresses a bug in Container Station on QNAP and the Docker application on
    Synology, where variables without values may not be allowed. This behavior
    is incorrect, as variables without values are valid. Removing unneeded
    variables prevents deployment issues on these devices.

### Data Volumes

The following table describes the data volumes used by the container. Volume
mappings are set using the `-v` parameter with a value in the format
`<HOST_DIR>:<CONTAINER_DIR>[:PERMISSIONS]`.

| Container path  | Permissions | Description |
|-----------------|-------------|-------------|
|`/config`| rw | Stores the application's configuration, state, logs, and any files requiring persistency. |

### Ports

The following table lists the ports used by the container.

When using the default bridge network, ports can be mapped to the host using the
`-p` parameter with value in the format `<HOST_PORT>:<CONTAINER_PORT>`. The
internal container port may not be changeable, but you can use any port on the
host side.

See the Docker [Docker Container Networking](https://docs.docker.com/config/containers/container-networking)
documentation for details.

| Port | Protocol | Mapping to Host | Description |
|------|----------|-----------------|-------------|
| 9090 | TCP | Mandatory | Port used to access the web interface of the application. |

### Changing Parameters of a Running Container

Environment variables, volume mappings, and port mappings are specified when
creating the container. To modify these parameters for an existing container,
follow these steps:

  1. Stop the container (if it is running):
```shell
docker stop sharry
```

  2. Remove the container:
```shell
docker rm sharry
```

  3. Recreate and start the container using the `docker run` command, adjusting
     parameters as needed.

> [!NOTE]
> Since all application data is saved under the `/config` container folder,
> destroying and recreating the container does not result in data loss, and the
> application resumes with the same state, provided the `/config` folder
> mapping remains unchanged.

### Docker Compose File

Below is an example `docker-compose.yml` file for use with
[Docker Compose](https://docs.docker.com/compose/overview/).

Adjust the configuration to suit your needs. Only mandatory settings are
included in this example.

```yaml
services:
  sharry:
    image: jlesage/sharry
    ports:
      - "9090:9090"
    volumes:
      - "/docker/appdata/sharry:/config:rw"
```

## Docker Image Versioning and Tags

Each release of a Docker image is versioned, and each version as its own image
tag. Before October 2022, the versioning scheme followed
[semantic versioning](https://semver.org).

Since then, the versioning scheme has shifted to
[calendar versioning](https://calver.org) with the format `YY.MM.SEQUENCE`,
where:
  - `YY` is the zero-padded year (relative to year 2000).
  - `MM` is the zero-padded month.
  - `SEQUENCE` is the incremental release number within the month (first release
    is 1, second is 2, etc).

View all available tags on [Docker Hub] or check the [Releases] page for version
details.

[Releases]: https://github.com/jlesage/docker-sharry/releases
[Docker Hub]: https://hub.docker.com/r/jlesage/sharry/tags

## Docker Image Update

The Docker image is regularly updated to incorporate new features, fix issues,
or integrate newer versions of the containerized application. Several methods
can be used to update the Docker image.

If your system provides a built-in method for updating containers, this should
be your primary approach.

Alternatively, you can use [Watchtower], a container-based solution for
automating Docker image updates. Watchtower seamlessly handles updates when a
new image is available.

To manually update the Docker image, follow these steps:

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

  4. Recreate and start the container using the `docker run` command, with the
     same parameters used during initial deployment.

[Watchtower]: https://github.com/containrrr/watchtower

### Synology

For Synology NAS users, follow these steps to update a container image:

  1.  Open the *Docker* application.
  2.  Click *Registry* in the left pane.
  3.  In the search bar, type the name of the container (`jlesage/sharry`).
  4.  Select the image, click *Download*, and choose the `latest` tag.
  5.  Wait for the download to complete. A notification will appear once done.
  6.  Click *Container* in the left pane.
  7.  Select your Sharry container.
  8.  Stop it by clicking *Action* -> *Stop*.
  9.  Clear the container by clicking *Action* -> *Reset* (or *Action* ->
      *Clear* if you don't have the latest *Docker* application). This removes
      the container while keeping its configuration.
  10. Start the container again by clicking *Action* -> *Start*. **NOTE**:  The
      container may temporarily disappear from the list while it is recreated.

### unRAID

For unRAID users, update a container image with these steps:

  1. Select the *Docker* tab.
  2. Click the *Check for Updates* button at the bottom of the page.
  3. Click the *apply update* link of the container to be updated.

## User/Group IDs

When mapping data volumes (using the `-v` flag of the `docker run` command),
permission issues may arise between the host and the container. Files and
folders in a data volume are owned by a user, which may differ from the user
running the application. Depending on permissions, this could prevent the
container from accessing the shared volume.

To avoid this, specify the user the application should run as using the
`USER_ID` and `GROUP_ID` environment variables.

To find the appropriate IDs, run the following command on the host for the user
owning the data volume:

```shell
id <username>
```

This produces output like:

```
uid=1000(myuser) gid=1000(myuser) groups=1000(myuser),4(adm),24(cdrom),27(sudo),46(plugdev),113(lpadmin)
```

Use the `uid` (user ID) and `gid` (group ID) values to configure the container.

## Shell Access

To access the shell of a running container, execute the following command:

```shell
docker exec -ti CONTAINER sh
```

Where `CONTAINER` is the ID or the name of the container used during its
creation.

## Accessing the GUI

Assuming that container's ports are mapped to the same host's ports, the
interface of the application can be accessed with a web browser at:

```text
http://<HOST IP ADDR>:9090
```

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

> [!TIP]
> A default `SHARRY_` environment variable (as defined under the
> [Environment Variables](#environment-variables) section) can be ignored by
> setting its value to `UNSET`. This forces the use of the config option value
> from the configuration file,

## Exposing Sharry to the Internet

Sharry cannot be exposed directly to the Internet. Features
required to allow this is out of scope for Sharry. Instead, it
should run behind a reverse proxy. A reverse proxy can offer a secure access via
HTTPs to the web interface, while also providing a valid certificate that can be
verified by browsers.

See https://eikek.github.io/sharry/doc/reverseproxy for more details.

## Support or Contact

Having troubles with the container or have questions? Please
[create a new issue](https://github.com/jlesage/docker-sharry/issues).

For other Dockerized applications, visit https://jlesage.github.io/docker-apps.
