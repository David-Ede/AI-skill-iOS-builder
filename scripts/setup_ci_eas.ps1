[CmdletBinding()]
param(
  [Parameter(Mandatory = $true)]
  [ValidateNotNullOrEmpty()]
  [string]$ProjectDir,

  [ValidateSet("github")]
  [string]$RepoProvider = "github",

  [ValidateNotNullOrEmpty()]
  [string]$ReleaseBranch = "main"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Write-Step {
  param([string]$Message)
  Write-Host "[expo-ios-app-builder] $Message"
}

function Has-ObjectProperty {
  param(
    [Parameter(Mandatory = $true)]
    [object]$Object,
    [Parameter(Mandatory = $true)]
    [string]$Name
  )
  foreach ($property in $Object.PSObject.Properties) {
    if ($property.Name -eq $Name) {
      return $true
    }
  }
  return $false
}

function Ensure-ObjectProperty {
  param(
    [Parameter(Mandatory = $true)]
    [object]$Object,
    [Parameter(Mandatory = $true)]
    [string]$Name,
    [Parameter(Mandatory = $true)]
    [object]$DefaultValue
  )
  if (-not (Has-ObjectProperty -Object $Object -Name $Name)) {
    $Object | Add-Member -MemberType NoteProperty -Name $Name -Value $DefaultValue
  }
  return $Object.$Name
}

function Set-ObjectProperty {
  param(
    [Parameter(Mandatory = $true)]
    [object]$Object,
    [Parameter(Mandatory = $true)]
    [string]$Name,
    [Parameter(Mandatory = $true)]
    [object]$Value
  )
  if (Has-ObjectProperty -Object $Object -Name $Name) {
    $Object.$Name = $Value
  }
  else {
    $Object | Add-Member -MemberType NoteProperty -Name $Name -Value $Value
  }
}

function Write-Utf8NoBom {
  param(
    [Parameter(Mandatory = $true)]
    [string]$Path,
    [Parameter(Mandatory = $true)]
    [string]$Content
  )
  $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
  [System.IO.File]::WriteAllText($Path, $Content, $utf8NoBom)
}

function Assert-CommandAvailable {
  param(
    [Parameter(Mandatory = $true)]
    [string]$CommandName
  )
  if (-not (Get-Command $CommandName -ErrorAction SilentlyContinue)) {
    throw "Required command not found in PATH: $CommandName"
  }
}

function Assert-NodeVersionPolicy {
  $nodeVersion = (& node -v).Trim()
  if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($nodeVersion)) {
    throw "Unable to determine Node version from 'node -v'."
  }

  if ($nodeVersion -notmatch '^v(\d+)\.(\d+)\.(\d+)$') {
    throw "Unexpected Node version format: $nodeVersion"
  }

  $major = [int]$Matches[1]
  $minor = [int]$Matches[2]
  $patch = [int]$Matches[3]

  if ($major -lt 20) {
    throw "Node version $nodeVersion is unsupported. Minimum supported version is v20.19.4."
  }

  if ($major -eq 20) {
    if ($minor -lt 19 -or ($minor -eq 19 -and $patch -lt 4)) {
      throw "Node version $nodeVersion is unsupported. Minimum supported version is v20.19.4."
    }
  }
}

function Ensure-GitIgnoreEntries {
  param(
    [Parameter(Mandatory = $true)]
    [string]$ProjectDir
  )

  $gitignorePath = Join-Path $ProjectDir ".gitignore"
  $content = ""
  if (Test-Path -LiteralPath $gitignorePath) {
    $content = [System.IO.File]::ReadAllText($gitignorePath)
  }

  $entries = @(".expo/", ".expo-shared/")
  $updated = $false
  foreach ($entry in $entries) {
    $escapedEntry = [regex]::Escape($entry)
    if ($content -notmatch "(?m)^$escapedEntry\s*$") {
      if ($content.Length -gt 0 -and -not $content.EndsWith("`n")) {
        $content += "`n"
      }
      $content += "$entry`n"
      $updated = $true
    }
  }

  if ($updated -or -not (Test-Path -LiteralPath $gitignorePath)) {
    Write-Utf8NoBom -Path $gitignorePath -Content $content
  }
}

Assert-CommandAvailable -CommandName "node"
Assert-CommandAvailable -CommandName "npm"
Assert-CommandAvailable -CommandName "npx"
Assert-NodeVersionPolicy

if (-not (Test-Path -LiteralPath $ProjectDir)) {
  throw "ProjectDir does not exist: $ProjectDir"
}

$resolvedProjectDir = (Resolve-Path -LiteralPath $ProjectDir).Path
$packageJsonPath = Join-Path $resolvedProjectDir "package.json"
if (-not (Test-Path -LiteralPath $packageJsonPath)) {
  throw "package.json not found in project directory: $resolvedProjectDir"
}

$skillRoot = Split-Path -Parent $PSScriptRoot
$workflowTemplatePath = Join-Path $skillRoot "assets/templates/github-actions-eas.yml"
$easTemplatePath = Join-Path $skillRoot "assets/templates/eas.json.template"

if ($RepoProvider -ne "github") {
  throw "Only RepoProvider=github is currently supported."
}

if (-not (Test-Path -LiteralPath $workflowTemplatePath)) {
  throw "Workflow template is missing: $workflowTemplatePath"
}

$workflowDir = Join-Path $resolvedProjectDir ".github/workflows"
New-Item -ItemType Directory -Path $workflowDir -Force | Out-Null
$workflowPath = Join-Path $workflowDir "eas-ios.yml"
$template = [System.IO.File]::ReadAllText($workflowTemplatePath)
$workflow = $template.Replace("__RELEASE_BRANCH__", $ReleaseBranch)
Write-Utf8NoBom -Path $workflowPath -Content $workflow
Write-Step "Installed workflow: $workflowPath"

$easPath = Join-Path $resolvedProjectDir "eas.json"
if (-not (Test-Path -LiteralPath $easPath)) {
  if (Test-Path -LiteralPath $easTemplatePath) {
    Copy-Item -Path $easTemplatePath -Destination $easPath -Force
    Write-Step "Installed eas.json from template."
  }
  else {
    throw "eas.json is missing and eas template was not found."
  }
}

$pkg = Get-Content -Raw -Path $packageJsonPath | ConvertFrom-Json
$pkgScripts = Ensure-ObjectProperty -Object $pkg -Name "scripts" -DefaultValue ([pscustomobject]@{})
Set-ObjectProperty -Object $pkgScripts -Name "lint" -Value "eslint . --ext .js,.jsx,.ts,.tsx"
Set-ObjectProperty -Object $pkgScripts -Name "typecheck" -Value "tsc --noEmit"
Set-ObjectProperty -Object $pkgScripts -Name "test" -Value "jest --runInBand"

$pkgJson = $pkg | ConvertTo-Json -Depth 20
Write-Utf8NoBom -Path $packageJsonPath -Content ($pkgJson + "`n")

$metadataPath = Join-Path $resolvedProjectDir "skill.modules.json"
if (Test-Path -LiteralPath $metadataPath) {
  try {
    $metadata = Get-Content -Raw -Path $metadataPath | ConvertFrom-Json
    Set-ObjectProperty -Object $metadata -Name "releaseBranch" -Value $ReleaseBranch
    $json = $metadata | ConvertTo-Json -Depth 20
    Write-Utf8NoBom -Path $metadataPath -Content ($json + "`n")
  }
  catch {
    Write-Step "Warning: could not update releaseBranch in skill.modules.json ($($_.Exception.Message))."
  }
}

Ensure-GitIgnoreEntries -ProjectDir $resolvedProjectDir

Write-Step "CI and EAS setup complete."
Write-Step "Ensure EXPO_TOKEN and Apple credentials are configured in repository secrets."
