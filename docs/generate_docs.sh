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

if [[ ! $(git status --short) ]]; then
    echo 'Nothing to commit'
    exit 0
fi

touch .nojekyll
git add .
git commit  -m "Documentation update: $(date '+%d %b %y')"

if [[ ! $(git branch -a | grep remotes/origin/gh-pages) ]]; then
    git push --set-upstream origin gh-pages
else
    git push origin gh-pages
fi
