param(
    [string]$StartPath = ".",
    [ValidateSet("VAULT_DOCUMENTATION", "SOURCE_REPOSITORY")]
    [string]$TaskClassification = "VAULT_DOCUMENTATION",
    [string[]]$AllowedDirtyPaths = @()
)

# Project Read-First Preflight — Vault Edition
# Read-only: this script never modifies files or Git state, and never
# pulls, commits, or pushes.

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# Owner artifacts allowed to remain untracked in this Vault.
$ownerArtifacts = @(".obsidian/", "IDEA.md")

# The only valid terminal decisions.
$validDecisions = @(
    "READY",
    "BLOCKED_DIRTY_WORKTREE",
    "BLOCKED_PROJECT_MISMATCH",
    "BLOCKED_SERENA",
    "BLOCKED_CODEGRAPH",
    "BLOCKED_MISSING_AUTHORITY",
    "BLOCKED_SCOPE_CONFLICT",
    "BLOCKED_OWNER_DECISION"
)

$decision = "READY"
$blockReason = ""

function Set-Block {
    param([string]$NewDecision, [string]$Reason)
    # First block wins; later blocks do not overwrite the reason.
    if ($script:decision -eq "READY") {
        $script:decision = $NewDecision
        $script:blockReason = $Reason
    }
}

$currentDir = (Get-Location).Path

# Resolve canonical Git root (read-only).
$root = git -C $StartPath rev-parse --show-toplevel 2>$null
if ($LASTEXITCODE -ne 0 -or -not $root) {
    $root = "NONE"
    Set-Block "BLOCKED_MISSING_AUTHORITY" "Not a Git repository or git not on PATH"
}

$branch = ""
$head = ""
$upstream = ""
$origin = ""
$gitStatusLines = @()

if ($root -ne "NONE") {
    $branch = git -C $root branch --show-current 2>$null
    $head = git -C $root rev-parse HEAD 2>$null
    $upstream = git -C $root rev-parse --abbrev-ref "HEAD@{upstream}" 2>$null
    if ($LASTEXITCODE -ne 0) { $upstream = "NONE" }
    $origin = git -C $root remote get-url origin 2>$null
    $gitStatusRaw = git -C $root status --short 2>$null
    if ($gitStatusRaw) {
        $gitStatusLines = @($gitStatusRaw -split "`r?`n" | Where-Object { $_.Trim() })
    }
}

# Separate expected dirty files from unexpected dirty files.
$expectedDirty = @()
$unexpectedDirty = @()
foreach ($line in $gitStatusLines) {
    $path = $line.Substring(3).Trim().Trim('"')
    $isExpected = $false
    foreach ($artifact in $ownerArtifacts) {
        if ($path -eq $artifact -or $path -eq $artifact.TrimEnd('/') -or $path.StartsWith($artifact)) {
            $isExpected = $true
        }
    }
    foreach ($allowed in $AllowedDirtyPaths) {
        if ($path -eq $allowed -or $path.StartsWith($allowed.TrimEnd('/') + "/")) {
            $isExpected = $true
        }
    }
    if ($isExpected) { $expectedDirty += $path } else { $unexpectedDirty += $path }
}

if ($unexpectedDirty.Count -gt 0) {
    Set-Block "BLOCKED_DIRTY_WORKTREE" ("Unexpected dirty files: " + ($unexpectedDirty -join ", "))
}

# Mandatory Vault authority documents.
$activeWorkOrder = "NONE"
$workOrderStatus = "NONE"
if ($root -ne "NONE") {
    $mandatoryFiles = @(
        "AGENTS.md",
        "README.md",
        "00 Dashboard/Project Dashboard.md",
        "04 Work Orders/CURRENT_WORK_ORDER.md"
    )
    $missingFiles = @()
    foreach ($f in $mandatoryFiles) {
        if (-not (Test-Path -LiteralPath (Join-Path $root $f) -PathType Leaf)) {
            $missingFiles += $f
        }
    }
    if ($missingFiles.Count -gt 0) {
        Set-Block "BLOCKED_MISSING_AUTHORITY" ("Missing mandatory files: " + ($missingFiles -join ", "))
    }

    # Resolve active Work Order pointer (read-only).
    $currentWoPath = Join-Path $root "04 Work Orders/CURRENT_WORK_ORDER.md"
    if (Test-Path -LiteralPath $currentWoPath -PathType Leaf) {
        $woContent = Get-Content -LiteralPath $currentWoPath -Raw
        if ($woContent -match 'WORK_ORDER:\s*`?([^`\r\n]+)`?') {
            $activeWorkOrder = $Matches[1].Trim()
        }
        if ($woContent -match 'STATUS:\s*([A-Z_]+)') {
            $workOrderStatus = $Matches[1]
        }
        if ($activeWorkOrder -ne "NONE") {
            $woTarget = Join-Path $root $activeWorkOrder
            if (-not (Test-Path -LiteralPath $woTarget -PathType Leaf)) {
                Set-Block "BLOCKED_MISSING_AUTHORITY" "CURRENT_WORK_ORDER points to a missing file: $activeWorkOrder"
            }
        }
    }
}

# Serena and CodeGraph fields.
# This script cannot verify MCP project activation or index-root
# equality by itself; verification requires the agent to confirm via
# the MCP tools per SERENA_CODEGRAPH_PROTOCOL.md. Presence of an
# executable or an index directory is never sufficient, so this
# script reports not_verified for SOURCE_REPOSITORY and defers the
# block decision to the agent-side protocol.
if ($TaskClassification -eq "VAULT_DOCUMENTATION") {
    $serenaProject = "not_required"
    $serenaStatus = "not_required"
    $codegraphProject = "not_required"
    $codegraphStatus = "not_required"
    $codegraphSync = "not_required"
} else {
    $serenaProject = "not_verified"
    $serenaStatus = "not_verified"
    $codegraphProject = "not_verified"
    $codegraphStatus = "not_verified"
    $codegraphSync = "no"
    Set-Block "BLOCKED_SERENA" "SOURCE_REPOSITORY task: Serena and CodeGraph must be verified via MCP protocol before implementation"
}

# Guard: decision must be one of the eight valid values.
if ($validDecisions -notcontains $decision) {
    $decision = "BLOCKED_SCOPE_CONFLICT"
    $blockReason = "Internal error: invalid terminal decision computed"
}

$gitStatusJoined = if ($gitStatusLines.Count -gt 0) { $gitStatusLines -join " | " } else { "clean" }
$expectedJoined = if ($expectedDirty.Count -gt 0) { $expectedDirty -join ", " } else { "none" }
$unexpectedJoined = if ($unexpectedDirty.Count -gt 0) { $unexpectedDirty -join ", " } else { "none" }

# Emit output contract exactly once.
Write-Output "READ_FIRST_PREFLIGHT"
Write-Output ""
Write-Output "REPOSITORY_ROOT: $root"
Write-Output "CURRENT_DIRECTORY: $currentDir"
Write-Output "BRANCH: $branch"
Write-Output "HEAD: $head"
Write-Output "UPSTREAM: $upstream"
Write-Output "ORIGIN: $origin"
Write-Output "GIT_STATUS: $gitStatusJoined"
Write-Output "EXPECTED_DIRTY_FILES: $expectedJoined"
Write-Output "UNEXPECTED_DIRTY_FILES: $unexpectedJoined"
Write-Output ""
Write-Output "TASK_CLASSIFICATION: $TaskClassification"
Write-Output "ACTIVE_WORK_ORDER: $activeWorkOrder"
Write-Output "WORK_ORDER_STATUS: $workOrderStatus"
Write-Output "ALLOWED_FILES: see active Work Order"
Write-Output "FORBIDDEN_FILES: see active Work Order"
Write-Output ""
Write-Output "SERENA_PROJECT: $serenaProject"
Write-Output "SERENA_STATUS: $serenaStatus"
Write-Output "CODEGRAPH_PROJECT: $codegraphProject"
Write-Output "CODEGRAPH_STATUS: $codegraphStatus"
Write-Output "CODEGRAPH_SYNC: $codegraphSync"
Write-Output ""
Write-Output "FULL_DOCUMENTS_READ: agent-reported per DOCUMENT_READ_POLICY.md"
Write-Output "TARGETED_DOCUMENTS_READ: agent-reported per DOCUMENT_READ_POLICY.md"
Write-Output "SOURCE_SYMBOLS_INSPECTED: agent-reported"
Write-Output ""
Write-Output "EXPECTED_CHANGE: defined by active Work Order"
Write-Output "REQUIRED_VALIDATION: defined by active Work Order"
Write-Output "DOCUMENTATION_IMPACT: defined by active Work Order"
Write-Output "COMMIT_AUTHORIZATION: defined by active Work Order"
Write-Output ""
Write-Output "PREFLIGHT_DECISION: $decision"
Write-Output ""
Write-Output "BLOCK_REASON: $blockReason"

if ($decision -eq "READY") { exit 0 } else { exit 1 }
