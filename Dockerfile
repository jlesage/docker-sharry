#
# sharry Dockerfile
#
# https://github.com/jlesage/docker-sharry
#

# Docker image version is provided via build arg.
ARG DOCKER_IMAGE_VERSION=

# Define software versions.
ARG SHARRY_VERSION=1.14.0

# Define software download URLs.
ARG SHARRY_URL=https://github.com/eikek/sharry/releases/download/v${SHARRY_VERSION}/sharry-restserver-${SHARRY_VERSION}.zip

# Download JDownloader2
FROM --platform=$BUILDPLATFORM alpine:3.20 AS sharry
ARG SHARRY_URL
RUN \
    apk --no-cache add curl && \
    curl -# -L -o /tmp/sharry.zip ${SHARRY_URL} && \
    unzip -d /opt/ /tmp/sharry.zip && \
    mv /opt/sharry-restserver-* /opt/sharry

# Pull base image.
FROM jlesage/baseimage:alpine-3.20-v3.6.2

ARG DOCKER_IMAGE_VERSION

# Define working directory.
WORKDIR /tmp

# Install dependencies.
RUN \
    add-pkg \
        bash \
        ncurses \
        java-common \
        openjdk17-jre

# Add files.
COPY rootfs/ /
COPY --from=sharry /opt/sharry /opt/sharry

# Set internal environment variables.
RUN \
    set-cont-env APP_NAME "Sharry" && \
    set-cont-env DOCKER_IMAGE_VERSION "$DOCKER_IMAGE_VERSION" && \
    true

# Set public environment variables.
ENV \
    SHARRY_BASE_URL=http://localhost:9090 \
    SHARRY_BACKEND_AUTH_FIXED_USER=admin \
    SHARRY_BACKEND_AUTH_FIXED_PASSWORD=changeme

# Expose ports.
#   - 9191: Sharry web interface.
EXPOSE 9191

# Metadata.
LABEL \
      org.label-schema.name="sharry" \
      org.label-schema.description="Docker container for Sharry" \
      org.label-schema.version="${DOCKER_IMAGE_VERSION:-unknown}" \
      org.label-schema.vcs-url="https://github.com/jlesage/docker-sharry" \
      org.label-schema.schema-version="1.0"
