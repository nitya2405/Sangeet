"""
preprocessing/pitch_augment.py

Pitch-shift every existing WAV segment by -2, -1, +1, +2 semitones.
Writes new WAV files and a combined manifest (original + augmented).

Input  : data/processed/segments_manifest.jsonl
         data/processed/hindustani_wav16k/**/*.wav

Output : data/processed/hindustani_wav16k_aug/<mbid>_ps<shift>/seg_NNNNN.wav
         data/processed/segments_manifest_aug.jsonl   (original rows + new rows)

Run:
    python preprocessing/pitch_augment.py
    # or limit to N songs for a quick test:
    python preprocessing/pitch_augment.py --max-songs 5

After this, run the tokenizer:
    python preprocessing/tokenize_carnatic_encodec.py \
        --config configs/tokenize_encodec_24khz_aug.yaml
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import librosa
import numpy as np
import soundfile as sf
from tqdm import tqdm

_REPO = Path(__file__).resolve().parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from sangeet.utils.jsonl import read_jsonl

SRC_MANIFEST = _REPO / "data/processed/segments_manifest.jsonl"
DST_WAV_ROOT = _REPO / "data/processed/hindustani_wav16k_aug"
DST_MANIFEST = _REPO / "data/processed/segments_manifest_aug.jsonl"

SHIFTS = [-2, -1, 1, 2]   # semitones


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--src-manifest", default=str(SRC_MANIFEST))
    p.add_argument("--dst-wav-root", default=str(DST_WAV_ROOT))
    p.add_argument("--dst-manifest", default=str(DST_MANIFEST))
    p.add_argument("--max-songs", type=int, default=None,
                   help="Process at most N unique recordings (for testing)")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    src_manifest = Path(args.src_manifest)
    dst_wav_root = Path(args.dst_wav_root)
    dst_manifest = Path(args.dst_manifest)

    rows = list(read_jsonl(src_manifest))
    print(f"[pitch_augment] {len(rows)} segments in source manifest")

    # Limit to N unique recordings if requested
    if args.max_songs is not None:
        seen_mbids: set[str] = set()
        filtered = []
        for r in rows:
            mbid = r.get("mbid", "")
            seen_mbids.add(mbid)
            if len(seen_mbids) <= args.max_songs:
                filtered.append(r)
        rows = filtered
        print(f"  → limited to {args.max_songs} songs = {len(rows)} segments")

    out_rows: list[dict] = []
    errors = 0

    for row in tqdm(rows, desc="Pitch augmenting"):
        src_wav = Path(row["wav_path"])
        if not src_wav.is_absolute():
            src_wav = (_REPO / src_wav).resolve()

        if not src_wav.exists():
            errors += 1
            continue

        # Read once, reuse for all shifts
        try:
            audio, sr = librosa.load(str(src_wav), sr=None, mono=True)
        except Exception as e:
            print(f"  [SKIP] {src_wav}: {e}")
            errors += 1
            continue

        mbid = str(row.get("mbid", "unknown"))
        seg_idx = int(row.get("segment_index", 0))

        for shift in SHIFTS:
            shifted = librosa.effects.pitch_shift(audio, sr=sr, n_steps=shift)

            tag = f"ps{shift:+d}"
            aug_mbid = f"{mbid}_{tag}"
            dst_dir = dst_wav_root / aug_mbid
            dst_dir.mkdir(parents=True, exist_ok=True)
            dst_path = dst_dir / f"seg_{seg_idx:05d}.wav"

            sf.write(str(dst_path), shifted, sr)

            new_row = dict(row)
            new_row["mbid"] = aug_mbid
            new_row["wav_path"] = str(dst_path.relative_to(_REPO))
            new_row["pitch_shift_semitones"] = shift
            out_rows.append(new_row)

    # Write manifest: original rows first, then augmented
    all_rows = list(read_jsonl(src_manifest)) + out_rows
    with open(dst_manifest, "w", encoding="utf-8") as f:
        for r in all_rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    print(f"\n[DONE] {len(out_rows)} augmented segments written")
    print(f"       {len(all_rows)} total rows in {dst_manifest}")
    if errors:
        print(f"       {errors} segments skipped")


if __name__ == "__main__":
    main()
