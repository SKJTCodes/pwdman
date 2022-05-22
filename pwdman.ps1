if (Test-Path -Path $env:CONDA)
{
    $pythonFile = $PSCommandPath.replace(".ps1", ".py")
    $pythonExist = Test-Path -Path $pythonFile -PathType Leaf
    if ($pythonExist) {
        & $env:CONDA\python.exe $pythonFile $args
    }
} else {
    throw "Unable to find Conda Env. $env:CONDA"
}