## Entire duplicates of explorer_stack/Dockerfile because I couldn't reuse steps as I wanted
## May be reunited properly later

# Overridable ROS distro argument (generic)
ARG ROS_DISTRO=jazzy
## Only used for production-ready image
ARG ROS_USER=orthopus
ARG ROS_WS=/home/${ROS_USER}/src/

## Multi stage build

##  ---------------- Base / cache part ---------------- 
FROM osrf/ros:${ROS_DISTRO}-desktop AS explorer_ws_cacher
ARG ROS_WS

# Overwrite apt-get defaults to prevent rosdep from installing optional packages
RUN rosdep update --rosdistro $ROS_DISTRO && \
    cat <<EOF > /etc/apt/apt.conf.d/docker-clean && apt-get update
APT::Install-Recommends "false";
APT::Install-Suggests "false";
EOF

WORKDIR ${ROS_WS}
COPY --exclude=build --exclude=install . ${ROS_WS}

# Derive build/exec dependencies into a /tmp/[build|exec]_dependencies.txt
# Taken from an official ROS image
RUN bash -e <<'EOF'
declare -A types=(
  [exec]="--dependency-types=build --dependency-types=exec --dependency-types=test --dependency-types=doc"
  [build]="--dependency-types=build --dependency-types=test")
for type in "${!types[@]}"; do
  rosdep install -y \
    --from-paths . \
    --ignore-src \
    --reinstall \
    --simulate \
    ${types[$type]} \
    | grep 'apt-get install' \
    | awk '{gsub(/'\''/,"",$4); print $4}' \
    | sort -u > /tmp/${type}_dependencies.txt
done
EOF


##  ---------------- Builder part (CI)---------------- 
# Lighter image for CI/CD
FROM amd64/ros:${ROS_DISTRO}-ros-base AS explorer_ws_builder
LABEL org.opencontainers.image.source="https://github.com/ORTHOPUS-EXPLORER/explorer_ws"
LABEL org.opencontainers.image.description="CI/CD image for Orthopus Explorer Workspace"
# LABEL org.opencontainers.image.licenses=

COPY --from=explorer_ws_cacher /tmp/exec_dependencies.txt /tmp/exec_dependencies.txt
RUN --mount=type=cache,target=/etc/apt/apt.conf.d,from=explorer_ws_cacher,source=/etc/apt/apt.conf.d \
    --mount=type=cache,target=/var/lib/apt/lists,from=explorer_ws_cacher,source=/var/lib/apt/lists \
    --mount=type=cache,target=/var/cache/apt,sharing=locked \
    # Install exec dependencies from rosdep (includes build, exec, test, doc)
    < /tmp/exec_dependencies.txt xargs apt-get install -y --no-install-recommends \
    # CI build caching + modprobe (kmod) + killall command (psmisc)
    && apt install -y ccache kmod psmisc

## Install manual extra dependencies
COPY qontrol_controller/Makefile /tmp
RUN make install -C /tmp && rm /tmp/Makefile

RUN echo 'source /opt/ros/${ROS_DISTRO}/setup.bash && source install/setup.bash || true' >> ~/.bashrc

##  ---------------- Runner part (dev)---------------- 
FROM ghcr.io/orthopus-explorer/ros-${ROS_DISTRO}-explorer/dev AS explorer_ws_dev
LABEL org.opencontainers.image.source="https://github.com/ORTHOPUS-EXPLORER/explorer_ws"
LABEL org.opencontainers.image.description="Development image for Orthopus Explorer workspace"
# LABEL org.opencontainers.image.licenses=

# Needed for build script
ARG ROS_WS
ENV ROS_WS=${ROS_WS}

COPY --from=explorer_ws_cacher /tmp/exec_dependencies.txt /tmp/
# Install build/exec dependencies from rosdep
RUN --mount=type=cache,target=/etc/apt/apt.conf.d,from=explorer_ws_cacher,source=/etc/apt/apt.conf.d \
    --mount=type=cache,target=/var/lib/apt/lists,from=explorer_ws_cacher,source=/var/lib/apt/lists \
    --mount=type=cache,target=/var/cache/apt,sharing=locked \
    ## Delete any clang related packages (latest version will be installed at next step)
    sed -i '/.*clang.*/d' /tmp/exec_dependencies.txt \
    && < /tmp/exec_dependencies.txt xargs apt-get install -y --no-install-recommends \
    && apt install -y --no-install-recommends psmisc

## Install manual extra dependencies
COPY qontrol_controller/Makefile /tmp
RUN make install -C /tmp && rm /tmp/Makefile

RUN echo 'source /opt/ros/${ROS_DISTRO}/setup.bash && source install/setup.bash || true' >> ~/.bashrc

# Make the workspace build script available globally as `ros_build`
COPY .devcontainer/ros/build.sh /usr/local/bin/ros_build
RUN chmod +x /usr/local/bin/ros_build

## ---------------- Runner part (prod) ----------------
FROM explorer_ws_dev AS explorer_ws_prod
LABEL org.opencontainers.image.description="Ready to uses image for Orthopus Explorer project"

ARG ROS_WS
ARG ROS_USER
ENV ROS_USER=${ROS_USER}
ENV ROS_WS=${ROS_WS}

RUN useradd -m --no-log-init -r ${ROS_USER}

# Copy colcon config (no need to reinstall mixins)
RUN cp -r /root/.colcon /home/${ROS_USER}
WORKDIR ${ROS_WS}

# Setup passwordless sudoers for apt related commands
RUN echo "${ROS_USER} ALL=(ALL) NOPASSWD: /usr/bin/apt, /usr/bin/apt-get, /usr/bin/aptitude, /usr/bin/apt-fast, /usr/bin/add-apt-repository, /usr/local/bin/set_device_permissions.sh" >> /etc/sudoers

COPY --chown=orthopus --exclude=build --exclude=install --exclude=log . ${ROS_WS}
RUN chmod -R a+rwX ${ROS_WS}

RUN . /opt/ros/$ROS_DISTRO/setup.sh && . /home/${ROS_USER}/.bashrc && cd ${ROS_WS} && \
    colcon build --symlink-install --continue-on-error --mixin release

USER ${ROS_USER}