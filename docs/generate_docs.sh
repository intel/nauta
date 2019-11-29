#!/bin/bash -ex
sphinx-build -b html . _build

mkdir -p gh-pages
if [[ ! $(git worktree list | grep 'gh-pages') ]]; then
    git worktree add --detach gh-pages
fi
rm -rf gh-pages/*
mv _build/* gh-pages/
cd gh-pages

git config --local user.name nauta-docs
git config --local user.email nauta-docs@nauta.invalid

if [[ $(git branch --list "gh-pages") ]]; then
	git checkout gh-pages
else
	git checkout --orphan gh-pages
fi

touch .nojekyll

if [[ $(git status --short) ]]; then
    git add .
    git commit  -m "Documentation update: $(date '+%d %b %y')"
fi

git push --set-upstream origin gh-pages
