#!/bin/bash
set -e

if [ ! -f "$MODEL_CHECKPOINT" ]; then
    echo "[startup] Checkpoint not found at $MODEL_CHECKPOINT"
    if [ -z "$HF_MODEL_REPO" ]; then
        echo "[startup] ERROR: set HF_MODEL_REPO env var (e.g. nitya2405/sangeet-hindustani-lm)"
        exit 1
    fi
    echo "[startup] Downloading checkpoint from $HF_MODEL_REPO ..."
    python - <<'PYEOF'
import os, shutil
from huggingface_hub import hf_hub_download
dst = os.environ["MODEL_CHECKPOINT"]
path = hf_hub_download(
    repo_id=os.environ["HF_MODEL_REPO"],
    filename=os.environ.get("HF_CKPT_FILE", "checkpoint.pt"),
    token=os.environ.get("HF_TOKEN"),
    local_dir="/tmp/hf_dl",
    local_dir_use_symlinks=False,
)
shutil.copy(path, dst)
print(f"[startup] Checkpoint saved to {dst}")
PYEOF
fi

exec uvicorn backend.main:app --host 0.0.0.0 --port 7860
