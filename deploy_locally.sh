TARGET_DIR=$HOME/Library/Application\ Support/Anki2/addons21/japanese-helper
rm -rf "${TARGET_DIR:?}"/*
mkdir -p "${TARGET_DIR}"
cp -r __init__.py jp_helper "${TARGET_DIR}"