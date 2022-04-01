set -e
rm -rf artifacts
mkdir artifacts

printf "Default config:\n"
python print_config.py | tee artifacts/default.txt

printf "With environment config:\n"
NEXTSONG_MEDIA_ROOT="media" NEXTSONG_MEDIA_EXTS="flac ogg" python print_config.py | tee artifacts/environ.txt

printf "Custom config:\n"
python print_custom_config.py | tee artifacts/custom.txt

printf "Diffing output - <got >exp\n"
diff -r artifacts expected
