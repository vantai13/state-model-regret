#!/bin/bash
# Doan Van Tai — EV-D4b overnight pipeline on the GCP VM [AI (Claude) theo ủy quyền 14/11/2026].
# test seed (resumable; fixed seeds per (case, h); on a crash retry with fewer workers) -> sha256 manifest of raw files
# BEFORE scoring -> score with the locked code -> power the VM off. The author's PC is not needed.
cd ~/smr || exit 1
source experiments/explore_ctmc/env.sh 2>/dev/null
P=.venv/bin/python; L=~/ev_d4b.log
echo "PIPELINE_START $(date -Is)" >> $L
for w in ${WORKERS:-8} 4 2; do
  timeout 9h $P -m experiments.ext_validity.ev_d4b_panel run $w >> $L 2>&1 && break
  echo "RUN_FAILED workers=$w exit=$? $(date -Is)" >> $L
done
echo "TEST_FILES $(ls results/ext_validity/ev_d4b/test/*.json 2>/dev/null | wc -l) $(date -Is)" >> $L
$P -m experiments.ext_validity.ev_d4b_panel manifest >> $L 2>&1
$P -m experiments.ext_validity.ev_d4b_panel score >> $L 2>&1
echo "PIPELINE_DONE $(date -Is)" >> $L
sync; sudo -n poweroff
