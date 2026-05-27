FROM pytorch/pytorch:2.3.1-cuda12.1-cudnn8-runtime

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg && \
    rm -rf /var/lib/apt/lists/*

COPY requirements-deploy.txt .
RUN pip install --no-cache-dir -r requirements-deploy.txt

# Source code (no training data, no runs/)
COPY sangeet/        ./sangeet/
COPY backend/        ./backend/
COPY generate_music.py .

# Vocab JSONs — small, ship in image so no runtime fetch needed
COPY vocabs/ ./vocabs/

# Startup script downloads checkpoint from HF Hub on first boot
COPY scripts/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENV MODEL_CHECKPOINT=/app/checkpoint.pt
ENV VOCABS_DIR=/app/vocabs
ENV OUTPUTS_DIR=/app/outputs

EXPOSE 7860

ENTRYPOINT ["/entrypoint.sh"]
