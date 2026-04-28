#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUILD_DIR="$REPO_ROOT/build"

mkdir -p "$BUILD_DIR"

for parent in "$REPO_ROOT"/0x*/; do
    parent_name="$(basename "$parent")"
    for child in "$parent"0x*/; do
        [ -d "$child" ] || continue
        child_name="$(basename "$child")"
        zip_name="firmware_${parent_name}_${child_name}.zip"
        if [ -z "$(ls -A "$child")" ]; then
            echo "Skipping $parent_name/$child_name (empty)"
            continue
        fi
        echo "Packing $parent_name/$child_name -> build/$zip_name"
        (cd "$child" && zip -r "$BUILD_DIR/$zip_name" . --exclude eeprom.yaml)
        if [ -f "$child/eeprom.yaml" ]; then
            cp "$child/eeprom.yaml" "$BUILD_DIR/firmware_${parent_name}_${child_name}.yaml"
        fi
    done
done
