set -e
rm -rf artifacts
mkdir artifacts

export NEXTSONG_MEDIA_ROOT="$RL_ROOT/tests/common/sample_media"
export NEXTSONG_PLAYLIST_PATH="./artifacts/nextsong.xml"
export NEXTSONG_STATE_PATH="./artifacts/state.pickle"
export NEXTSONG_ON_CHANGE=seek
export NEXTSONG_MAX_SEEK_SKIPS=100

python test.py |& tee artifacts/out.txt

printf "Diffing output - <got >exp\n"
diff artifacts/out.txt expected/out.txt
