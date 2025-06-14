poetry sync
echo "{\"python.defaultInterpreterPath\": \"$(poetry env info -p)\"}" > .vscode/settings.json