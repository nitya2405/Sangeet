# generate_resume_picks.ps1
# Generates a sweep of outputs for resume/demo selection.
# Run from repo root with the venv active:
#   .\scripts\generate_resume_picks.ps1

$CKPT_FLAT  = "runs/hindustani_cfg/checkpoints/latest.pt"
$CKPT_DELAY = "runs/hindustani_delay_v2/checkpoints/latest.pt"
$OUT        = "outputs/resume_picks"

New-Item -ItemType Directory -Force $OUT | Out-Null

function Gen {
    param($ckpt, $raga, $tala, $dur, $cb, $cfg, $tag)
    $out = "$OUT/${tag}.wav"
    Write-Host "`n>>> $tag" -ForegroundColor Cyan
    python generate_music.py `
        --ckpt  $ckpt `
        --raga  $raga `
        --tala  $tala `
        --duration $dur `
        --n-cb  $cb `
        --cfg-scale $cfg `
        --out   $out
}

# ── Flat model (hindustani_cfg 155k) ─────────────────────────────────────────

# Kalyāṇ — your confirmed best raga for this model
Gen $CKPT_FLAT "Kalyāṇ"   "Tīntāl"  6  4  7.0  "flat_kalyan_teen_6s_cb4"
Gen $CKPT_FLAT "Kalyāṇ"   "Tīntāl" 12  4  7.0  "flat_kalyan_teen_12s_cb4"
Gen $CKPT_FLAT "Kalyāṇ"   "Tīntāl"  6  4  5.0  "flat_kalyan_teen_6s_cfg5"
Gen $CKPT_FLAT "Kalyāṇ"   "Tīntāl"  6  8  7.0  "flat_kalyan_teen_6s_cb8"

# Bhairav — morning raga, distinct character
Gen $CKPT_FLAT "Bhairav"  "Tīntāl"  6  4  7.0  "flat_bhairav_teen_6s"
Gen $CKPT_FLAT "Bhairav"  "Rūpak"   6  4  7.0  "flat_bhairav_rupak_6s"

# Bhairavi — late night, emotional
Gen $CKPT_FLAT "Bhairavi" "Tīntāl"  6  4  7.0  "flat_bhairavi_teen_6s"
Gen $CKPT_FLAT "Bhairavi" "Tīntāl" 12  4  7.0  "flat_bhairavi_teen_12s"

# Tōḍī — morning, complex, recognisable
Gen $CKPT_FLAT "Tōḍī"    "Tīntāl"  6  4  7.0  "flat_todi_teen_6s"

# Mārvā — evening, distinctive komal Re + shuddh Ni
Gen $CKPT_FLAT "Mārvā"   "Tīntāl"  6  4  7.0  "flat_marva_teen_6s"

# Yaman kalyāṇ — closest to plain Yaman
Gen $CKPT_FLAT "Yaman kalyāṇ" "Tīntāl" 6 4 7.0 "flat_yaman_teen_6s"
Gen $CKPT_FLAT "Yaman kalyāṇ" "Tīntāl" 12 4 7.0 "flat_yaman_teen_12s"

# Mālkauns — late night, pentatonic, atmospheric
Gen $CKPT_FLAT "Mālkauns" "Tīntāl"  6  4  7.0  "flat_malkauns_teen_6s"

# Bāgēśrī — late night
Gen $CKPT_FLAT "Bāgēśrī" "Tīntāl"  6  4  7.0  "flat_bageshri_teen_6s"

# ── Delay v2 model (for comparison — may or may not be better) ───────────────
Gen $CKPT_DELAY "Kalyāṇ"  "Tīntāl"  6  4  7.0  "delay_v2_kalyan_teen_6s"
Gen $CKPT_DELAY "Bhairav" "Tīntāl"  6  4  7.0  "delay_v2_bhairav_teen_6s"

Write-Host "`n[DONE] All outputs in $OUT" -ForegroundColor Green
