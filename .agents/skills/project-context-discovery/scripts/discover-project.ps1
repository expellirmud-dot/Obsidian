param(
    [Parameter(Mandatory = $true)]
    [string]$ProjectPath
)

# Project Context Discovery — Level 1 helper (read-only)
# Reports repository identification facts and candidate authority
# files. Never modifies files or Git state, never installs
# dependencies, never commits or pushes, and never claims Serena or
# CodeGraph verification.

Set-StrictMode -Version Latest
# "Continue" (not "Stop"): native git commands legitimately write to
# stderr for non-repository paths; the script handles failures via
# $LASTEXITCODE and explicit exit codes instead.
$ErrorActionPreference = "Continue"

Write-Output "PROJECT_DISCOVERY_LEVEL1"
Write-Output ""

$currentDir = (Get-Location).Path
Write-Output "CURRENT_DIRECTORY: $currentDir"
Write-Output "PROJECT_PATH_ARG: $ProjectPath"

if (-not (Test-Path -LiteralPath $ProjectPath -PathType Container)) {
    Write-Output "PATH_EXISTS: no"
    Write-Output "REPOSITORY_ROOT: NONE"
    Write-Output "DISCOVERY_LEVEL1_RESULT: NOT_A_DIRECTORY"
    exit 1
}
Write-Output "PATH_EXISTS: yes"

$root = git -C $ProjectPath rev-parse --show-toplevel 2>$null
if ($LASTEXITCODE -ne 0 -or -not $root) {
    Write-Output "REPOSITORY_ROOT: NONE"
    Write-Output "DISCOVERY_LEVEL1_RESULT: NOT_A_GIT_REPOSITORY"
    exit 1
}
Write-Output "REPOSITORY_ROOT: $root"

$branch = git -C $root branch --show-current 2>$null
$head = git -C $root rev-parse HEAD 2>$null
if ($LASTEXITCODE -ne 0) { $head = "NONE (no commits)" }
$upstream = git -C $root rev-parse --abbrev-ref "HEAD@{upstream}" 2>$null
if ($LASTEXITCODE -ne 0) { $upstream = "NONE" }
$origin = git -C $root remote get-url origin 2>$null
if ($LASTEXITCODE -ne 0 -or -not $origin) { $origin = "NONE" }
$statusRaw = git -C $root status --short 2>$null
$statusLines = @()
if ($statusRaw) {
    $statusLines = @($statusRaw -split "`r?`n" | Where-Object { $_.Trim() })
}
$statusJoined = if ($statusLines.Count -gt 0) { $statusLines -join " | " } else { "clean" }

Write-Output "BRANCH: $branch"
Write-Output "HEAD: $head"
Write-Output "UPSTREAM: $upstream"
Write-Output "ORIGIN: $origin"
Write-Output "GIT_STATUS: $statusJoined"
Write-Output "DIRTY_FILE_COUNT: $($statusLines.Count)"
Write-Output ""

# Top-level structure (names only; no file contents are read).
Write-Output "TOP_LEVEL_ENTRIES:"
Get-ChildItem -LiteralPath $root -Force |
    Where-Object { $_.Name -ne ".git" } |
    Sort-Object { -not $_.PSIsContainer }, Name |
    ForEach-Object {
        $kind = if ($_.PSIsContainer) { "dir " } else { "file" }
        Write-Output "  $kind $($_.Name)"
    }
Write-Output ""

# Candidate authority filenames (case-insensitive, root level and
# common locations). Existence is reported; content is NOT read and
# existence is NOT treated as evidence of authority.
$candidates = @(
    "AGENTS.md",
    "PROJECT_RULES.md",
    "CLAUDE.md",
    "CONTRIBUTING.md",
    "GOVERNANCE.md",
    "README.md",
    "CURRENT_WORK_ORDER.md",
    "docs/INDEX.md",
    "docs/README.md",
    "Work-Order/CURRENT_WORK_ORDER.md",
    "work-order/CURRENT_WORK_ORDER.md",
    "work_orders/CURRENT_WORK_ORDER.md"
)
$candidateDirs = @("work-order", "work_orders", "Work-Order", "docs", ".agents")

Write-Output "AUTHORITY_FILE_CANDIDATES:"
$foundAny = $false
foreach ($c in $candidates) {
    $p = Join-Path $root $c
    if (Test-Path -LiteralPath $p -PathType Leaf) {
        $item = Get-Item -LiteralPath $p
        Write-Output "  found: $c (size $($item.Length) bytes)"
        $foundAny = $true
    }
}
foreach ($d in $candidateDirs) {
    $p = Join-Path $root $d
    if (Test-Path -LiteralPath $p -PathType Container) {
        Write-Output "  found-dir: $d/"
        $foundAny = $true
    }
}
if (-not $foundAny) {
    Write-Output "  none-found"
}
Write-Output ""

Write-Output "SERENA_STATUS: not_verified (script cannot verify; use MCP protocol)"
Write-Output "CODEGRAPH_STATUS: not_verified (script cannot verify; use MCP protocol)"
Write-Output ""
Write-Output "DISCOVERY_LEVEL1_RESULT: OK"
exit 0
