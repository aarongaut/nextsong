set -e
rm -rf artifacts
mkdir artifacts

export NEXTSONG_MEDIA_ROOT="$RL_ROOT/tests/common/sample_media"
export NEXTSONG_PLAYLIST_PATH="./artifacts/nextsong.xml"
export NEXTSONG_STATE_PATH="./artifacts/state.pickle"
export NEXTSONG_ON_CHANGE=seek

cp "$RL_ROOT/tests/common/sample_playlists/1.xml" "$NEXTSONG_PLAYLIST_PATH"

printf "$(realpath --relative-to=$NEXTSONG_MEDIA_ROOT $(nextsong))\n" | tee -a artifacts/out.txt
printf "$(realpath --relative-to=$NEXTSONG_MEDIA_ROOT $(nextsong))\n" | tee -a artifacts/out.txt

printf "Copying over overlapping playlist; should continue\n" | tee -a artifacts/out.txt
cp "$RL_ROOT/tests/common/sample_playlists/2.xml" "$NEXTSONG_PLAYLIST_PATH"

printf "$(realpath --relative-to=$NEXTSONG_MEDIA_ROOT $(nextsong))\n" | tee -a artifacts/out.txt

printf "Touching playlist; should continue\n" | tee -a artifacts/out.txt
touch "$NEXTSONG_PLAYLIST_PATH"

printf "$(realpath --relative-to=$NEXTSONG_MEDIA_ROOT $(nextsong))\n" | tee -a artifacts/out.txt

printf "Diffing output - <got >exp\n"
diff artifacts/out.txt expected/out.txt
