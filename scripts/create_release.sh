#!/usr/bin/env bash
GIT_OWNER=ToucanToco
REPO=ansible-collection
BUILD_PATH=build

create_release(){
  echo "Create Github Release :: Retrieve current version..."
  NEW_VERSION_NUMBER=`make -s get-version | sed -e "s/^v//g"`
  export RELEASE_NAME="v${NEW_VERSION_NUMBER}"

  echo "Create Github Release :: Create release '${RELEASE_NAME}'..."
  res=$(curl -XPOST \
    -H "Authorization: token ${GITHUB_TOKEN}" \
    --silent --show-error --fail \
    --data "{\"tag_name\": \"v${NEW_VERSION_NUMBER}\", \"name\": \"${RELEASE_NAME}\"}" \
    https://api.github.com/repos/${GIT_OWNER}/${REPO}/releases)

  if [[ $? -ne 0 ]]; then \
      echo -e "\n\n ERROR :: Create Github Release :: Could not create github release\n"
      exit 1;
  fi

  RELEASE_ID=$(echo $res | jq .id)

  ARCHIVE_NAME="toucantoco-toucantoco-${NEW_VERSION_NUMBER}.tar.gz"
  FILE=${BUILD_PATH}/${ARCHIVE_NAME}

  curl \
      -H "Authorization: token $GITHUB_TOKEN" \
      -H "Content-Type: $(file -b --mime-type $FILE)" \
      --silent --output /dev/null --show-error --fail \
      --data-binary @$FILE \
      "https://uploads.github.com/repos/${GIT_OWNER}/${REPO}/releases/${RELEASE_ID}/assets?name=$(basename $FILE)"

  if [[ $? -ne 0 ]]; then \
      echo -e "\n\n ERROR :: Create Github Release :: Could not push archive\n"
      exit 1;
  fi
}

if [[ -z ${GITHUB_TOKEN} ]]
then
  echo -e "\n\n ERROR :: Release :: Missing Github token\n"
  exit 2
fi

create_release
