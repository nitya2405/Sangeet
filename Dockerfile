FROM pytorch/pytorch:2.3.1-cuda12.1-cudnn8-runtime

WORKDIR /app

# ffmpeg for audio format conversion
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg && \
    rm -rf /var/lib/apt/lists/*

# Python deps
COPY requirements-deploy.txt .
RUN pip install --no-cache-dir -r requirements-deploy.txt

# Source code (no training data, no runs/)
COPY sangeet/        ./sangeet/
COPY backend/        ./backend/
COPY generate_music.py .

# Model checkpoint — downloaded at build time from HF Hub
# Set HF_MODEL_REPO and HF_CKPT_FILE as build args or env vars
ARG HF_MODEL_REPO=""
ARG HF_CKPT_FILE="latest.pt"
ENV MODEL_CHECKPOINT=/app/checkpoint.pt

RUN if [ -n "$HF_MODEL_REPO" ]; then \
        pip install --no-cache-dir huggingface_hub && \
        python -c "from huggingface_hub import hf_hub_download; \
                   hf_hub_download('${HF_MODEL_REPO}', '${HF_CKPT_FILE}', local_dir='/app', local_dir_use_symlinks=False)" && \
        mv /app/${HF_CKPT_FILE} /app/checkpoint.pt; \
    fi

EXPOSE 7860

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "7860"]
