set -e
rm -rf artifacts
mkdir artifacts

export NEXTSONG_MEDIA_ROOT="$RL_ROOT/tests/common/sample_media"
export NEXTSONG_PLAYLIST_PATH="$RL_ROOT/tests/common/sample_playlists/1.xml"
export NEXTSONG_STATE_PATH="./artifacts/state.pickle"

printf "$(realpath --relative-to=$NEXTSONG_MEDIA_ROOT $(nextsong))\n" | tee artifacts/output.txt
printf "$(realpath --relative-to=$NEXTSONG_MEDIA_ROOT $(nextsong))\n" | tee -a artifacts/output.txt
printf "$(realpath --relative-to=$NEXTSONG_MEDIA_ROOT $(nextsong))\n" | tee -a artifacts/output.txt

printf "Diffing output - <got >exp\n"
diff -r artifacts/output.txt expected/output.txt
