$ErrorActionPreference = 'Stop'
$runtimePath = Join-Path -Path $PSScriptRoot -ChildPath 'runtime.py'

if (Get-Command py.exe -ErrorAction SilentlyContinue) {
    & py.exe -3 $runtimePath
    exit $LASTEXITCODE
}
if (Get-Command python.exe -ErrorAction SilentlyContinue) {
    & python.exe $runtimePath
    exit $LASTEXITCODE
}
if (Get-Command python3.exe -ErrorAction SilentlyContinue) {
    & python3.exe $runtimePath
    exit $LASTEXITCODE
}

exit 0
