set -e
rm -rf artifacts
mkdir artifacts

export NEXTSONG_MEDIA_ROOT="$RL_ROOT/tests/common/sample_media"
export NEXTSONG_PLAYLIST_PATH="./artifacts/nextsong.xml"
export NEXTSONG_STATE_PATH="./artifacts/state.pickle"
export NEXTSONG_ON_CHANGE=restart

cp "$RL_ROOT/tests/common/sample_playlists/1.xml" "$NEXTSONG_PLAYLIST_PATH"

nextsong | tee -a artifacts/out.txt
nextsong | tee -a artifacts/out.txt

printf "Touching playlist; should restart\n" | tee -a artifacts/out.txt
touch "$NEXTSONG_PLAYLIST_PATH"

nextsong | tee -a artifacts/out.txt

printf "Touching playlist; should restart again\n" | tee -a artifacts/out.txt
touch "$NEXTSONG_PLAYLIST_PATH"

nextsong | tee -a artifacts/out.txt

printf "Diffing output - <got >exp\n"
diff artifacts/out.txt expected/out.txt
