# generate_resume_picks.ps1
# Run from repo root with venv active:
#   .\scripts\generate_resume_picks.ps1

$env:PYTHONUTF8 = "1"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$CKPT_FLAT  = "runs/hindustani_cfg/checkpoints/latest.pt"
$CKPT_DELAY = "runs/hindustani_delay_v2/checkpoints/latest.pt"
$OUT        = "outputs/resume_picks"

New-Item -ItemType Directory -Force $OUT | Out-Null

function Gen($ckpt, $raga, $tala, $dur, $cb, $cfg, $tag) {
    $outPath = "$OUT/$tag.wav"
    Write-Host "`n>>> $tag" -ForegroundColor Cyan
    python generate_music.py --ckpt $ckpt --raga $raga --tala $tala --duration $dur --n-cb $cb --cfg-scale $cfg --out $outPath
}

$teen  = "T`u012bnt`u0101l"
$rupak = "R`u016bpak"

# Flat model (hindustani_cfg 155k)
Gen $CKPT_FLAT "Kalya`u0101`u1e47"           $teen   6  4  7.0  "flat_kalyan_teen_6s_cb4"
Gen $CKPT_FLAT "Kalya`u0101`u1e47"           $teen  12  4  7.0  "flat_kalyan_teen_12s_cb4"
Gen $CKPT_FLAT "Kalya`u0101`u1e47"           $teen   6  4  5.0  "flat_kalyan_teen_6s_cfg5"
Gen $CKPT_FLAT "Kalya`u0101`u1e47"           $teen   6  8  7.0  "flat_kalyan_teen_6s_cb8"
Gen $CKPT_FLAT "Bhairav"                     $teen   6  4  7.0  "flat_bhairav_teen_6s"
Gen $CKPT_FLAT "Bhairav"                     $rupak  6  4  7.0  "flat_bhairav_rupak_6s"
Gen $CKPT_FLAT "Bhairavi"                    $teen   6  4  7.0  "flat_bhairavi_teen_6s"
Gen $CKPT_FLAT "Bhairavi"                    $teen  12  4  7.0  "flat_bhairavi_teen_12s"
Gen $CKPT_FLAT "T`u014d`u1e0d`u012b"         $teen   6  4  7.0  "flat_todi_teen_6s"
Gen $CKPT_FLAT "M`u0101rv`u0101"             $teen   6  4  7.0  "flat_marva_teen_6s"
Gen $CKPT_FLAT "Yaman kalya`u0101`u1e47"     $teen   6  4  7.0  "flat_yaman_teen_6s"
Gen $CKPT_FLAT "Yaman kalya`u0101`u1e47"     $teen  12  4  7.0  "flat_yaman_teen_12s"
Gen $CKPT_FLAT "M`u0101lkauns"               $teen   6  4  7.0  "flat_malkauns_teen_6s"
Gen $CKPT_FLAT "B`u0101g`u0113`u015br`u012b" $teen   6  4  7.0  "flat_bageshri_teen_6s"

# Delay v2
Gen $CKPT_DELAY "Kalya`u0101`u1e47"          $teen   6  4  7.0  "delay_v2_kalyan_teen_6s"
Gen $CKPT_DELAY "Bhairav"                    $teen   6  4  7.0  "delay_v2_bhairav_teen_6s"

Write-Host "`n[DONE] All outputs in $OUT" -ForegroundColor Green
