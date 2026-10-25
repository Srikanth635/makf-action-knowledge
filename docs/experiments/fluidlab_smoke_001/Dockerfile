# syntax=docker/dockerfile:1
FROM python:3.7-slim-bullseye@sha256:603879aeff06df23f0d392a19f7ce02aa85e14e6b4d25fd9647b116e0cb93467
RUN --mount=type=secret,id=ca,required=true \
    PIP_CERT=/run/secrets/ca pip install --no-cache-dir pip==23.0 setuptools==65.5.0 wheel==0.38.4
RUN --mount=type=secret,id=ca,required=true \
    PIP_CERT=/run/secrets/ca pip install --no-cache-dir numpy==1.21.5 taichi==1.1.0 gym==0.21.0 scipy==1.7.3 trimesh==3.12.9 transforms3d==0.4.1 yacs==0.1.8 pyyaml==6.0 tqdm==4.64.1 scikit-learn==1.0.2
RUN --mount=type=secret,id=ca,required=true \
    PIP_CERT=/run/secrets/ca pip install --no-cache-dir torch==1.12.1+cpu --extra-index-url https://download.pytorch.org/whl/cpu
WORKDIR /work
ENV PYTHONPATH=/work PYTHONUNBUFFERED=1
RUN --mount=type=secret,id=ca,required=true \
    PIP_CERT=/run/secrets/ca pip install --no-cache-dir matplotlib==3.5.3
RUN --mount=type=secret,id=ca,required=true,mode=0444 sed -i 's|http://deb.debian.org|https://deb.debian.org|g; s|http://security.debian.org|https://security.debian.org|g' /etc/apt/sources.list && apt-get -o Acquire::https::CaInfo=/run/secrets/ca update && apt-get -o Acquire::https::CaInfo=/run/secrets/ca install -y --no-install-recommends libx11-6 libxrandr2 libxinerama1 libxcursor1 libxi6 && rm -rf /var/lib/apt/lists/*
RUN --mount=type=secret,id=ca,required=true \
    PIP_CERT=/run/secrets/ca pip install --no-cache-dir importlib-metadata==4.12.0
RUN --mount=type=secret,id=ca,required=true \
    PIP_CERT=/run/secrets/ca pip install --no-cache-dir opencv-python-headless==4.6.0.66
