TARGET_DIR=/tmp/japanese-helper
rm -rf ${TARGET_DIR}
mkdir ${TARGET_DIR}
cp -r __init__.py jp_helper ${TARGET_DIR}
pushd ${TARGET_DIR} || exit
zip -r ../japanese-helper.ankiaddon *
rm -rf ${TARGET_DIR:?}/*
mv ../japanese-helper.ankiaddon ${TARGET_DIR}

echo "The addon has been packaged to ${TARGET_DIR}/japanese-helper.ankiaddon"
popd || exit
