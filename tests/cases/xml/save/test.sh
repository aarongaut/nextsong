set -e
rm -rf artifacts
mkdir artifacts

export NEXTSONG_MEDIA_ROOT="$RL_ROOT/tests/common/sample_media"
export NEXTSONG_PLAYLIST_PATH="./artifacts/nextsong.xml"

python test.py

printf "Diffing output - <got >exp\n"
diff -r artifacts expected
