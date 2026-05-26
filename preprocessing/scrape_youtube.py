"""
preprocessing/scrape_youtube.py

Download Hindustani classical recordings from YouTube, convert to 16kHz mono WAV,
segment into 10-second chunks, and produce a manifest compatible with the
existing tokenization pipeline.

Sources used (all public domain / government archive / CC):
  - All India Radio (AIR) Archives — government recordings, public domain in India
  - Doordarshan Archives
  - Any playlist/channel URLs passed via --urls or urls.txt

Requirements:
    pip install yt-dlp soundfile librosa tqdm

Run:
    # Download from built-in sources
    python preprocessing/scrape_youtube.py

    # Download from custom URL list (one URL per line)
    python preprocessing/scrape_youtube.py --url-file my_urls.txt

    # Limit to N videos for a test run
    python preprocessing/scrape_youtube.py --max-videos 5

Output:
    data/processed/youtube_wav16k/<video_id>/seg_NNNNN.wav
    data/processed/segments_manifest_youtube.jsonl

After this, tokenize:
    python preprocessing/tokenize_carnatic_encodec.py \
        --config configs/tokenize_encodec_24khz_youtube.yaml
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import librosa
import numpy as np
import soundfile as sf
from tqdm import tqdm

_REPO = Path(__file__).resolve().parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

# ---------------------------------------------------------------------------
# Default YouTube sources — public domain / government archives
# ---------------------------------------------------------------------------
DEFAULT_URLS = [
    # All India Radio Archives (government recordings, public domain in India)
    "https://www.youtube.com/@AIRArchives/videos",
    # Doordarshan National Archive
    "https://www.youtube.com/@DDNational/videos",
    # ITC Sangeet Research Academy — institutional uploads
    "https://www.youtube.com/@ITCSRAKolkata/videos",
]

SEG_SEC    = 10.0
TARGET_SR  = 16000
MIN_DUR    = 30.0   # skip videos shorter than this (likely clips, not full performances)
MAX_DUR    = 7200.0  # skip videos longer than 2h (likely compilations)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--url-file",    default=None,
                   help="Text file with one YouTube URL per line (channel, playlist, or video)")
    p.add_argument("--urls",        nargs="*", default=None,
                   help="YouTube URLs to download (overrides defaults)")
    p.add_argument("--out-dir",     default=str(_REPO / "data/processed/youtube_wav16k"))
    p.add_argument("--manifest",    default=str(_REPO / "data/processed/segments_manifest_youtube.jsonl"))
    p.add_argument("--max-videos",  type=int, default=None,
                   help="Stop after downloading this many videos (for testing)")
    p.add_argument("--seg-sec",     type=float, default=SEG_SEC)
    p.add_argument("--raga",        default="unknown",
                   help="Default raga label (override per-video if known)")
    p.add_argument("--tala",        default="unknown")
    return p.parse_args()


def get_video_urls(source_urls: list[str], max_videos: int | None) -> list[dict]:
    """Use yt-dlp --flat-playlist to enumerate video URLs without downloading."""
    import json as _json
    videos: list[dict] = []

    for src in source_urls:
        cmd = [
            "yt-dlp", "--flat-playlist", "--dump-single-json",
            "--match-filter", f"duration > {MIN_DUR} & duration < {MAX_DUR}",
            src,
        ]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            if result.returncode != 0:
                print(f"  [WARN] yt-dlp listing failed for {src}: {result.stderr[:200]}")
                continue
            data = _json.loads(result.stdout)
            entries = data.get("entries") or [data]
            for e in entries:
                vid_url = e.get("url") or e.get("webpage_url")
                if vid_url and not vid_url.startswith("http"):
                    vid_url = f"https://www.youtube.com/watch?v={vid_url}"
                if vid_url:
                    videos.append({
                        "url":      vid_url,
                        "video_id": e.get("id", ""),
                        "title":    e.get("title", ""),
                    })
                if max_videos and len(videos) >= max_videos:
                    break
        except Exception as ex:
            print(f"  [WARN] listing {src}: {ex}")

        if max_videos and len(videos) >= max_videos:
            break

    return videos[:max_videos] if max_videos else videos


def download_audio(video_url: str, tmp_dir: Path) -> Path | None:
    """Download best audio, convert to wav via yt-dlp + ffmpeg."""
    out_tmpl = str(tmp_dir / "%(id)s.%(ext)s")
    cmd = [
        "yt-dlp",
        "-x", "--audio-format", "wav",
        "--audio-quality", "0",
        "--no-playlist",
        "-o", out_tmpl,
        video_url,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    if result.returncode != 0:
        print(f"    [DL FAIL] {video_url}: {result.stderr[:300]}")
        return None
    wavs = list(tmp_dir.glob("*.wav"))
    return wavs[0] if wavs else None


def segment_wav(wav_path: Path, seg_sec: float, target_sr: int) -> list[np.ndarray]:
    """Load, resample, and split into fixed-length segments."""
    audio, sr = librosa.load(str(wav_path), sr=target_sr, mono=True)
    seg_len = int(seg_sec * target_sr)
    segments = []
    for start in range(0, len(audio) - seg_len + 1, seg_len):
        segments.append(audio[start : start + seg_len])
    return segments


def main() -> None:
    args = parse_args()
    out_dir  = Path(args.out_dir)
    manifest = Path(args.manifest)
    manifest.parent.mkdir(parents=True, exist_ok=True)

    # Determine source URLs
    if args.url_file:
        urls = [l.strip() for l in Path(args.url_file).read_text().splitlines() if l.strip()]
    elif args.urls:
        urls = args.urls
    else:
        urls = DEFAULT_URLS

    print(f"[scrape_youtube] Enumerating videos from {len(urls)} source(s)…")
    videos = get_video_urls(urls, args.max_videos)
    print(f"  → {len(videos)} videos to download")

    rows: list[dict] = []
    # Append to existing manifest if present
    if manifest.exists():
        with open(manifest, encoding="utf-8") as f:
            rows = [json.loads(l) for l in f if l.strip()]
        print(f"  → {len(rows)} existing rows in manifest (will append)")

    downloaded = 0
    for vid in tqdm(videos, desc="Downloading"):
        video_id = vid["video_id"] or "unknown"
        vid_dir  = out_dir / video_id
        vid_dir.mkdir(parents=True, exist_ok=True)

        # Skip if already processed
        existing_segs = list(vid_dir.glob("seg_*.wav"))
        if existing_segs:
            print(f"  [SKIP] {video_id} — already has {len(existing_segs)} segments")
            continue

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            wav_path = download_audio(vid["url"], tmp_path)
            if wav_path is None:
                continue

            try:
                segments = segment_wav(wav_path, args.seg_sec, TARGET_SR)
            except Exception as e:
                print(f"  [SKIP] {video_id} segment error: {e}")
                continue

            for i, seg in enumerate(segments):
                seg_path = vid_dir / f"seg_{i:05d}.wav"
                sf.write(str(seg_path), seg, TARGET_SR)
                rows.append({
                    "mbid":            video_id,
                    "segment_index":   i,
                    "start_sec":       i * args.seg_sec,
                    "duration_sec":    args.seg_sec,
                    "wav_path":        str(seg_path.relative_to(_REPO)),
                    "raga":            args.raga,
                    "tala":            args.tala,
                    "artist":          vid.get("title", "unknown"),
                    "source":          "youtube",
                    "youtube_url":     vid["url"],
                })

        downloaded += 1

    # Write manifest
    with open(manifest, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    print(f"\n[DONE] {downloaded} videos downloaded, {len(rows)} total segments")
    print(f"       manifest → {manifest}")
    print(f"\nNext: tokenize with")
    print(f"  python preprocessing/tokenize_carnatic_encodec.py --config configs/tokenize_encodec_24khz_youtube.yaml")


if __name__ == "__main__":
    main()
