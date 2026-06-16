param(
    [string]$Root = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path,
    [string]$CodexSkillsRoot = (Join-Path $env:USERPROFILE '.codex\skills')
)

$ErrorActionPreference = 'Stop'
$sourceRoot = Join-Path $Root 'skills'
$targetRoot = [System.IO.Path]::GetFullPath($CodexSkillsRoot)

if (-not (Test-Path -LiteralPath $sourceRoot -PathType Container)) {
    throw "Missing source skills directory: $sourceRoot"
}

if (-not (Test-Path -LiteralPath $targetRoot -PathType Container)) {
    New-Item -ItemType Directory -Path $targetRoot | Out-Null
}

$skills = Get-ChildItem -LiteralPath $sourceRoot -Directory -Filter 'neo-*' | Sort-Object Name
foreach ($skill in $skills) {
    $destination = [System.IO.Path]::GetFullPath((Join-Path $targetRoot $skill.Name))
    if (-not $destination.StartsWith($targetRoot, [StringComparison]::OrdinalIgnoreCase)) {
        throw "Refusing to sync outside Codex skills root: $destination"
    }

    if (Test-Path -LiteralPath $destination) {
        Remove-Item -LiteralPath $destination -Recurse -Force
    }

    Copy-Item -LiteralPath $skill.FullName -Destination $destination -Recurse
    Write-Host "Synced $($skill.Name) -> $destination"
}

Write-Host "Synced $($skills.Count) neo skills."
