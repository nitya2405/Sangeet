"""
scripts/generate_resume_picks.py
Run from repo root with venv active:
    python scripts/generate_resume_picks.py
"""
import subprocess, sys
from pathlib import Path

CKPT_FLAT  = "runs/hindustani_cfg/checkpoints/latest.pt"
CKPT_DELAY = "runs/hindustani_delay_v2/checkpoints/latest.pt"
OUT        = Path("outputs/resume_picks")
OUT.mkdir(parents=True, exist_ok=True)

TEEN  = "Tīntāl"
RUPAK = "Rūpak"

JOBS = [
    # (ckpt,       raga,               tala,   dur, cb, cfg,  tag)
    # Flat model — your confirmed best checkpoint
    (CKPT_FLAT, "Kalyāṇ",          TEEN,   6,  4, 7.0, "flat_kalyan_teen_6s_cb4"),
    (CKPT_FLAT, "Kalyāṇ",          TEEN,  12,  4, 7.0, "flat_kalyan_teen_12s_cb4"),
    (CKPT_FLAT, "Kalyāṇ",          TEEN,   6,  4, 5.0, "flat_kalyan_teen_6s_cfg5"),
    (CKPT_FLAT, "Kalyāṇ",          TEEN,   6,  8, 7.0, "flat_kalyan_teen_6s_cb8"),
    (CKPT_FLAT, "Bhairav",         TEEN,   6,  4, 7.0, "flat_bhairav_teen_6s"),
    (CKPT_FLAT, "Bhairav",         RUPAK,  6,  4, 7.0, "flat_bhairav_rupak_6s"),
    (CKPT_FLAT, "Bhairavi",        TEEN,   6,  4, 7.0, "flat_bhairavi_teen_6s"),
    (CKPT_FLAT, "Bhairavi",        TEEN,  12,  4, 7.0, "flat_bhairavi_teen_12s"),
    (CKPT_FLAT, "Tōḍī",            TEEN,   6,  4, 7.0, "flat_todi_teen_6s"),
    (CKPT_FLAT, "Mārvā",           TEEN,   6,  4, 7.0, "flat_marva_teen_6s"),
    (CKPT_FLAT, "Yaman kalyāṇ",    TEEN,   6,  4, 7.0, "flat_yaman_teen_6s"),
    (CKPT_FLAT, "Yaman kalyāṇ",    TEEN,  12,  4, 7.0, "flat_yaman_teen_12s"),
    (CKPT_FLAT, "Mālkauns",        TEEN,   6,  4, 7.0, "flat_malkauns_teen_6s"),
    (CKPT_FLAT, "Bāgēśrī",         TEEN,   6,  4, 7.0, "flat_bageshri_teen_6s"),
    # Delay v2 for comparison
    (CKPT_DELAY, "Kalyāṇ",         TEEN,   6,  4, 7.0, "delay_v2_kalyan_teen_6s"),
    (CKPT_DELAY, "Bhairav",        TEEN,   6,  4, 7.0, "delay_v2_bhairav_teen_6s"),
]

for ckpt, raga, tala, dur, cb, cfg, tag in JOBS:
    out_path = OUT / f"{tag}.wav"
    if out_path.exists():
        print(f"    [SKIP] {tag} — already exists", flush=True)
        continue
    print(f"\n>>> {tag}", flush=True)
    subprocess.run(
        [sys.executable, "generate_music.py",
         "--ckpt", ckpt,
         "--raga", raga,
         "--tala", tala,
         "--duration", str(dur),
         "--n-cb", str(cb),
         "--cfg-scale", str(cfg),
         "--out", str(out_path)],
        check=False,
    )

print(f"\n[DONE] All outputs in {OUT}")
