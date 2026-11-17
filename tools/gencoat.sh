#!/bin/bash
# gencoat.sh <coat> "<описание шерсти по-английски>" — перекрашивает рыжие листы через Codex CLI (ChatGPT),
# кладёт src/<coat>_{walk,pose}.png. Потом: python3 mksheet.py <coat>
cd "$(dirname "$0")"; coat=$1; desc=$2
[ -n "$coat" ] && [ -n "$desc" ] || { echo "usage: $0 <coat> \"<fur description>\""; exit 1; }
for kind in walk pose; do
  log=$(mktemp)
  timeout 520 codex exec -s read-only --skip-git-repo-check --ephemeral -C "$PWD" -i src/ginger_$kind.png -o "$log" "Use your image_generation tool to EDIT the attached sprite sheet image. Keep absolutely everything identical: the same number of kittens, the same poses, positions, sizes, silhouettes, fluffy fur edges, faces, pink inner ears, pink blush, the flat pure green #00FF00 background, the same image size. Change ONLY the fur colour and pattern of the kitten in every cell, identically in all cells: $desc. No outline, no text. After generating, print the full absolute path of the PNG file." < /dev/null > /dev/null 2>&1
  p=$(grep -o '/[^ ]*generated_images/[^ ]*\.png' "$log" | tail -1); rm -f "$log"
  [ -f "$p" ] && cp "$p" src/${coat}_$kind.png && echo "ok $coat $kind" || echo "FAIL $coat $kind"
done
