param(
    [string]$Root = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
)

$ErrorActionPreference = 'Stop'
$skillsRoot = Join-Path $Root 'skills'
$errors = New-Object System.Collections.Generic.List[string]

if (-not (Test-Path -LiteralPath $skillsRoot -PathType Container)) {
    throw "Missing skills directory: $skillsRoot"
}

$skillDirs = Get-ChildItem -LiteralPath $skillsRoot -Directory | Sort-Object Name
if ($skillDirs.Count -eq 0) {
    $errors.Add('No skill directories found.')
}

foreach ($dir in $skillDirs) {
    if ($dir.Name -notlike 'neo-*') {
        $errors.Add("Skill directory must use neo-* prefix: $($dir.Name)")
    }

    $skillPath = Join-Path $dir.FullName 'SKILL.md'
    if (-not (Test-Path -LiteralPath $skillPath -PathType Leaf)) {
        $errors.Add("Missing SKILL.md: $($dir.Name)")
        continue
    }

    $content = Get-Content -LiteralPath $skillPath -Raw
    if ($content -notmatch '(?s)^---\r?\n(.*?)\r?\n---') {
        $errors.Add("Missing YAML frontmatter: $($dir.Name)")
        continue
    }

    $frontmatter = $Matches[1]
    $keys = @()
    foreach ($line in ($frontmatter -split "\r?\n")) {
        if ($line -match '^([A-Za-z0-9_-]+):') {
            $keys += $Matches[1]
        }
    }

    foreach ($required in @('name', 'description')) {
        if ($keys -notcontains $required) {
            $errors.Add("Missing frontmatter key '$required': $($dir.Name)")
        }
    }

    foreach ($key in $keys) {
        if ($key -notin @('name', 'description')) {
            $errors.Add("Unsupported frontmatter key '$key' in $($dir.Name).")
        }
    }

    if ($frontmatter -match '(?m)^name:\s*["'']?([^"''\r\n]+)') {
        $skillName = $Matches[1].Trim()
        if ($skillName -ne $dir.Name) {
            $errors.Add("Frontmatter name '$skillName' does not match folder '$($dir.Name)'.")
        }
    }

    $agentPath = Join-Path $dir.FullName 'agents\openai.yaml'
    if (-not (Test-Path -LiteralPath $agentPath -PathType Leaf)) {
        $errors.Add("Missing agents/openai.yaml: $($dir.Name)")
    } else {
        $agentText = Get-Content -LiteralPath $agentPath -Raw
        if ($agentText -notmatch [regex]::Escape('$' + $dir.Name)) {
            $errors.Add("agents/openai.yaml default prompt does not mention '$$($dir.Name)': $($dir.Name)")
        }
    }
}

if ($errors.Count -gt 0) {
    Write-Host 'Skill validation failed:' -ForegroundColor Red
    foreach ($errorItem in $errors) {
        Write-Host " - $errorItem" -ForegroundColor Red
    }
    exit 1
}

Write-Host "Skill validation passed for $($skillDirs.Count) skills." -ForegroundColor Green
