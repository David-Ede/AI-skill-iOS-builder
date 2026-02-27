[CmdletBinding()]
param(
  [Parameter(Mandatory = $true)]
  [ValidateNotNullOrEmpty()]
  [string]$AppName,

  [Parameter(Mandatory = $true)]
  [ValidateNotNullOrEmpty()]
  [string]$BundleId,

  [Parameter(Mandatory = $true)]
  [ValidateNotNullOrEmpty()]
  [string]$OutputDir,

  [switch]$WithTabs,
  [switch]$UseAppConfigTs,
  [ValidateNotNullOrEmpty()]
  [string]$ReleaseBranch = "main",
  [switch]$WithUiFoundation,
  [switch]$WithProfile,
  [switch]$WithAuth,
  [switch]$WithPush,
  [switch]$WithDataLayer,
  [switch]$WithAnalytics,
  [switch]$WithCrashReporting,
  [switch]$WithLocalization,
  [switch]$WithAccessibilityChecks,
  [switch]$WithPrivacyChecklist
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Write-Step {
  param([string]$Message)
  Write-Host "[expo-ios-app-builder] $Message"
}

function Assert-BundleId {
  param([string]$Id)
  if ($Id -notmatch '^[A-Za-z][A-Za-z0-9]*(\.[A-Za-z0-9-]+)+$') {
    throw "BundleId '$Id' is invalid. Use reverse-DNS format like com.example.weatherapp."
  }
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

function Copy-TemplateTree {
  param(
    [Parameter(Mandatory = $true)]
    [string]$TemplateDir,
    [Parameter(Mandatory = $true)]
    [string]$DestinationRoot,
    [hashtable]$Tokens
  )

  if (-not (Test-Path -LiteralPath $TemplateDir)) {
    throw "Template path not found: $TemplateDir"
  }

  $sourceRoot = (Resolve-Path -LiteralPath $TemplateDir).Path
  $files = Get-ChildItem -LiteralPath $sourceRoot -Recurse -File
  foreach ($file in $files) {
    $relativePath = $file.FullName.Substring($sourceRoot.Length).TrimStart('\', '/')
    $destPath = Join-Path $DestinationRoot $relativePath
    $destDir = Split-Path -Parent $destPath
    New-Item -ItemType Directory -Path $destDir -Force | Out-Null

    $content = [System.IO.File]::ReadAllText($file.FullName)
    if ($Tokens) {
      foreach ($token in $Tokens.Keys) {
        $content = $content.Replace($token, [string]$Tokens[$token])
      }
    }
    Write-Utf8NoBom -Path $destPath -Content $content
  }
}

function Install-ExpoPackages {
  param(
    [Parameter(Mandatory = $true)]
    [string]$ProjectDir,
    [Parameter(Mandatory = $true)]
    [string[]]$Packages
  )

  if ($Packages.Count -eq 0) {
    return
  }

  Push-Location $ProjectDir
  try {
    & npx expo install @Packages
    if ($LASTEXITCODE -ne 0) {
      throw "expo install failed with exit code $LASTEXITCODE"
    }
  }
  finally {
    Pop-Location
  }
}

function Install-DevPackages {
  param(
    [Parameter(Mandatory = $true)]
    [string]$ProjectDir,
    [Parameter(Mandatory = $true)]
    [string[]]$Packages
  )

  Push-Location $ProjectDir
  try {
    & npm install --save-dev @Packages
    if ($LASTEXITCODE -ne 0) {
      throw "npm install --save-dev failed with exit code $LASTEXITCODE"
    }
  }
  finally {
    Pop-Location
  }
}

function Write-BaseAppFiles {
  param([string]$ProjectDir)

  $appDir = Join-Path $ProjectDir "app"
  New-Item -ItemType Directory -Path $appDir -Force | Out-Null

  $layoutContent = @'
import { Stack } from "expo-router";

export default function RootLayout() {
  return <Stack screenOptions={{ headerShown: false }} />;
}
'@
  Write-Utf8NoBom -Path (Join-Path $appDir "_layout.tsx") -Content $layoutContent

  $indexContent = @'
import { Text, View } from "react-native";

export default function HomeScreen() {
  return (
    <View style={{ flex: 1, justifyContent: "center", alignItems: "center", padding: 24 }}>
      <Text style={{ fontSize: 28, fontWeight: "700" }}>Welcome</Text>
      <Text style={{ marginTop: 10, textAlign: "center" }}>
        Generated by expo-ios-app-builder baseline scaffold.
      </Text>
    </View>
  );
}
'@
  Write-Utf8NoBom -Path (Join-Path $appDir "index.tsx") -Content $indexContent

  $exploreContent = @'
import { Text, View } from "react-native";

export default function ExploreScreen() {
  return (
    <View style={{ flex: 1, justifyContent: "center", alignItems: "center", padding: 24 }}>
      <Text style={{ fontSize: 24, fontWeight: "700" }}>Explore</Text>
      <Text style={{ marginTop: 10 }}>Second-route baseline for smoke checks.</Text>
    </View>
  );
}
'@
  Write-Utf8NoBom -Path (Join-Path $appDir "explore.tsx") -Content $exploreContent
}

function Write-ConfigFiles {
  param([string]$ProjectDir)

  $babelContent = @'
module.exports = function (api) {
  api.cache(true);
  return {
    presets: ["babel-preset-expo"],
  };
};
'@
  Write-Utf8NoBom -Path (Join-Path $ProjectDir "babel.config.js") -Content $babelContent

  $eslintContent = @'
const { defineConfig } = require("eslint/config");
const expoConfig = require("eslint-config-expo/flat");

module.exports = defineConfig([
  ...expoConfig,
  {
    ignores: ["dist/*", "coverage/*"],
  },
]);
'@
  Write-Utf8NoBom -Path (Join-Path $ProjectDir "eslint.config.js") -Content $eslintContent

  $jestContent = @'
module.exports = {
  preset: "jest-expo",
  setupFilesAfterEnv: ["<rootDir>/jest.setup.ts"],
  testMatch: ["**/__tests__/**/*.test.ts", "**/__tests__/**/*.test.tsx"],
};
'@
  Write-Utf8NoBom -Path (Join-Path $ProjectDir "jest.config.js") -Content $jestContent

  $jestSetupContent = @'
// Keep setup file present for future matcher extensions.
'@
  Write-Utf8NoBom -Path (Join-Path $ProjectDir "jest.setup.ts") -Content $jestSetupContent
}

function Update-TsConfig {
  param([string]$ProjectDir)

  $tsconfigPath = Join-Path $ProjectDir "tsconfig.json"
  if (-not (Test-Path -LiteralPath $tsconfigPath)) {
    return
  }

  $tsconfig = Get-Content -Raw -Path $tsconfigPath | ConvertFrom-Json
  $compiler = Ensure-ObjectProperty -Object $tsconfig -Name "compilerOptions" -DefaultValue ([pscustomobject]@{})
  Set-ObjectProperty -Object $compiler -Name "types" -Value @("jest")
  Set-ObjectProperty -Object $tsconfig -Name "exclude" -Value @("node_modules", "dist")

  $json = $tsconfig | ConvertTo-Json -Depth 20
  Write-Utf8NoBom -Path $tsconfigPath -Content ($json + "`n")
}

function Ensure-ExpoPlugin {
  param(
    [Parameter(Mandatory = $true)]
    [object[]]$Plugins,
    [Parameter(Mandatory = $true)]
    [string]$PluginName
  )

  foreach ($plugin in $Plugins) {
    if ($plugin -is [string] -and $plugin -eq $PluginName) {
      return ,@($Plugins)
    }
    if ($plugin -is [System.Collections.IList] -and $plugin.Count -gt 0 -and $plugin[0] -eq $PluginName) {
      return ,@($Plugins)
    }
  }

  $updated = @($Plugins)
  $updated += $PluginName
  return ,$updated
}

function Configure-AppJson {
  param(
    [string]$ProjectDir,
    [string]$BundleId,
    [hashtable]$ModuleFlags
  )

  $appJsonPath = Join-Path $ProjectDir "app.json"
  if (-not (Test-Path -LiteralPath $appJsonPath)) {
    throw "app.json not found: $appJsonPath"
  }

  $appConfig = Get-Content -Raw -Path $appJsonPath | ConvertFrom-Json
  $expo = Ensure-ObjectProperty -Object $appConfig -Name "expo" -DefaultValue ([pscustomobject]@{})
  $ios = Ensure-ObjectProperty -Object $expo -Name "ios" -DefaultValue ([pscustomobject]@{})
  Set-ObjectProperty -Object $ios -Name "bundleIdentifier" -Value $BundleId
  if (-not (Has-ObjectProperty -Object $expo -Name "scheme") -or [string]::IsNullOrWhiteSpace([string]$expo.scheme)) {
    Set-ObjectProperty -Object $expo -Name "scheme" -Value ($BundleId.Replace('.', '-'))
  }

  if (-not (Has-ObjectProperty -Object $expo -Name "plugins") -or -not $expo.plugins) {
    Set-ObjectProperty -Object $expo -Name "plugins" -Value @()
  }

  $plugins = Ensure-ExpoPlugin -Plugins @($expo.plugins) -PluginName "expo-router"
  if ($ModuleFlags.ContainsKey("withPush") -and [bool]$ModuleFlags["withPush"]) {
    $plugins = Ensure-ExpoPlugin -Plugins $plugins -PluginName "expo-notifications"
  }

  Set-ObjectProperty -Object $expo -Name "plugins" -Value $plugins

  $extra = Ensure-ObjectProperty -Object $expo -Name "extra" -DefaultValue ([pscustomobject]@{})
  Set-ObjectProperty -Object $extra -Name "skillModules" -Value $ModuleFlags

  $json = $appConfig | ConvertTo-Json -Depth 20
  Write-Utf8NoBom -Path $appJsonPath -Content ($json + "`n")
}

function Configure-AppConfigTs {
  param(
    [string]$ProjectDir,
    [string]$SkillRoot,
    [string]$AppName,
    [string]$BundleId,
    [hashtable]$ModuleFlags
  )

  $templatePath = Join-Path $SkillRoot "assets/templates/app.config.ts.template"
  if (-not (Test-Path -LiteralPath $templatePath)) {
    throw "app.config.ts template missing: $templatePath"
  }

  $slug = $AppName.ToLowerInvariant().Replace(' ', '-')
  $scheme = $BundleId.Replace('.', '-')
  $extraPluginsLiteral = ""
  if ($ModuleFlags.ContainsKey("withPush") -and [bool]$ModuleFlags["withPush"]) {
    $extraPluginsLiteral = ', "expo-notifications"'
  }

  $template = [System.IO.File]::ReadAllText($templatePath)
  $rendered = $template.Replace("__APP_NAME__", $AppName).Replace("__APP_SLUG__", $slug).Replace("__APP_SCHEME__", $scheme).Replace("__BUNDLE_ID__", $BundleId).Replace("__EXTRA_PLUGINS__", $extraPluginsLiteral)
  Write-Utf8NoBom -Path (Join-Path $ProjectDir "app.config.ts") -Content $rendered
}

function Write-ModuleMetadata {
  param(
    [string]$ProjectDir,
    [hashtable]$Flags,
    [string]$ReleaseBranch
  )

  $metadata = [ordered]@{
    schemaVersion = 1
    releaseBranch = $ReleaseBranch
    modules = $Flags
  }

  $json = $metadata | ConvertTo-Json -Depth 20
  Write-Utf8NoBom -Path (Join-Path $ProjectDir "skill.modules.json") -Content ($json + "`n")
}

Assert-BundleId -Id $BundleId
Assert-CommandAvailable -CommandName "node"
Assert-CommandAvailable -CommandName "npm"
Assert-CommandAvailable -CommandName "npx"
Assert-NodeVersionPolicy

if ($WithTabs.IsPresent) {
  $WithUiFoundation = $true
}
if ($WithProfile.IsPresent) {
  $WithUiFoundation = $true
}

$resolvedOutput = Resolve-Path -LiteralPath $OutputDir -ErrorAction SilentlyContinue
if (-not $resolvedOutput) {
  New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
  $resolvedOutput = Resolve-Path -LiteralPath $OutputDir
}
$resolvedOutputPath = $resolvedOutput.Path
$projectDir = Join-Path $resolvedOutputPath $AppName

if (Test-Path -LiteralPath $projectDir) {
  throw "Target path already exists: $projectDir"
}

Write-Step "Creating Expo project '$AppName' using template 'blank-typescript'."
Push-Location $resolvedOutputPath
try {
  & npx create-expo-app@latest $AppName --template blank-typescript --yes
  if ($LASTEXITCODE -ne 0) {
    throw "create-expo-app failed with exit code $LASTEXITCODE"
  }
}
finally {
  Pop-Location
}

$skillRoot = Split-Path -Parent $PSScriptRoot
$packageJsonPath = Join-Path $projectDir "package.json"
if (-not (Test-Path -LiteralPath $packageJsonPath)) {
  throw "package.json not found: $packageJsonPath"
}

Write-Step "Installing Expo runtime dependencies."
Install-ExpoPackages -ProjectDir $projectDir -Packages @(
  "expo-router",
  "react-native-safe-area-context",
  "react-native-screens",
  "expo-linking",
  "expo-constants",
  "expo-status-bar",
  "react-dom",
  "react-native-web"
)

if ($WithAuth.IsPresent) {
  Write-Step "Installing auth module dependencies."
  Install-ExpoPackages -ProjectDir $projectDir -Packages @(
    "expo-secure-store",
    "expo-auth-session",
    "expo-apple-authentication",
    "expo-crypto",
    "expo-web-browser"
  )
}
if ($WithPush.IsPresent) {
  Write-Step "Installing push module dependencies."
  Install-ExpoPackages -ProjectDir $projectDir -Packages @(
    "expo-notifications",
    "expo-device"
  )
}
if ($WithLocalization.IsPresent) {
  Write-Step "Installing localization dependencies."
  Install-ExpoPackages -ProjectDir $projectDir -Packages @("expo-localization")
}

Write-Step "Installing lint and test dependencies."
Install-DevPackages -ProjectDir $projectDir -Packages @(
  "eslint@^9.0.0",
  "eslint-config-expo@~10.0.0",
  "babel-preset-expo@^54.0.0",
  "jest@^29.7.0",
  "jest-expo@~54.0.0",
  "@types/jest@^29.5.14",
  "@testing-library/react-native@^13.3.3",
  "react-test-renderer@19.2.0"
)

Write-Step "Patching package scripts and entrypoint."
$pkg = Get-Content -Raw -Path $packageJsonPath | ConvertFrom-Json
Set-ObjectProperty -Object $pkg -Name "main" -Value "expo-router/entry"
$pkgScripts = Ensure-ObjectProperty -Object $pkg -Name "scripts" -DefaultValue ([pscustomobject]@{})
Set-ObjectProperty -Object $pkgScripts -Name "lint" -Value "eslint . --ext .js,.jsx,.ts,.tsx"
Set-ObjectProperty -Object $pkgScripts -Name "typecheck" -Value "tsc --noEmit"
Set-ObjectProperty -Object $pkgScripts -Name "test" -Value "jest --runInBand"

$pkgJson = $pkg | ConvertTo-Json -Depth 20
Write-Utf8NoBom -Path $packageJsonPath -Content ($pkgJson + "`n")

Write-ConfigFiles -ProjectDir $projectDir
Update-TsConfig -ProjectDir $projectDir

$appDir = Join-Path $projectDir "app"
if (Test-Path -LiteralPath $appDir) {
  Remove-Item -LiteralPath $appDir -Recurse -Force
}

$tokenMap = @{
  "__APP_NAME__" = $AppName
}

if ($WithUiFoundation.IsPresent) {
  Write-Step "Applying UI foundation module templates."
  Copy-TemplateTree -TemplateDir (Join-Path $skillRoot "assets/templates/feature-modules/ui-foundation") -DestinationRoot $projectDir -Tokens $tokenMap
}
else {
  Write-Step "Writing base app routes."
  Write-BaseAppFiles -ProjectDir $projectDir
}

if ($WithProfile.IsPresent) {
  Write-Step "Applying profile/settings module templates."
  Copy-TemplateTree -TemplateDir (Join-Path $skillRoot "assets/templates/feature-modules/profile-settings") -DestinationRoot $projectDir -Tokens $tokenMap
}
if ($WithAuth.IsPresent) {
  Write-Step "Applying auth module templates."
  Copy-TemplateTree -TemplateDir (Join-Path $skillRoot "assets/templates/feature-modules/auth") -DestinationRoot $projectDir -Tokens $tokenMap
}
if ($WithPush.IsPresent) {
  Write-Step "Applying notifications module templates."
  Copy-TemplateTree -TemplateDir (Join-Path $skillRoot "assets/templates/feature-modules/notifications") -DestinationRoot $projectDir -Tokens $tokenMap
}
if ($WithDataLayer.IsPresent) {
  Write-Step "Applying data-layer module templates."
  Copy-TemplateTree -TemplateDir (Join-Path $skillRoot "assets/templates/feature-modules/data-layer") -DestinationRoot $projectDir -Tokens $tokenMap
}
if ($WithAnalytics.IsPresent -or $WithCrashReporting.IsPresent) {
  Write-Step "Applying observability module templates."
  Copy-TemplateTree -TemplateDir (Join-Path $skillRoot "assets/templates/feature-modules/analytics-crash") -DestinationRoot $projectDir -Tokens $tokenMap
}
if ($WithLocalization.IsPresent) {
  Write-Step "Applying localization module templates."
  Copy-TemplateTree -TemplateDir (Join-Path $skillRoot "assets/templates/feature-modules/localization") -DestinationRoot $projectDir -Tokens $tokenMap
}

if ($WithAccessibilityChecks.IsPresent -or $WithPrivacyChecklist.IsPresent) {
  Copy-TemplateTree -TemplateDir (Join-Path $skillRoot "assets/templates/feature-modules/compliance") -DestinationRoot $projectDir -Tokens $tokenMap
  if (-not $WithAccessibilityChecks.IsPresent) {
    $accDoc = Join-Path $projectDir "docs/accessibility-checklist.md"
    if (Test-Path -LiteralPath $accDoc) { Remove-Item -LiteralPath $accDoc -Force }
  }
  if (-not $WithPrivacyChecklist.IsPresent) {
    $privDoc = Join-Path $projectDir "docs/privacy-checklist.md"
    if (Test-Path -LiteralPath $privDoc) { Remove-Item -LiteralPath $privDoc -Force }
  }
}

Copy-TemplateTree -TemplateDir (Join-Path $skillRoot "assets/templates/icons-splash") -DestinationRoot (Join-Path $projectDir "assets/placeholders") -Tokens $tokenMap
Copy-TemplateTree -TemplateDir (Join-Path $skillRoot "assets/templates/testing") -DestinationRoot $projectDir -Tokens $tokenMap

if (-not $WithAuth.IsPresent) {
  $authTest = Join-Path $projectDir "__tests__/auth-oauth.test.ts"
  if (Test-Path -LiteralPath $authTest) {
    Remove-Item -LiteralPath $authTest -Force
  }
}

if (-not $WithPush.IsPresent) {
  $pushTest = Join-Path $projectDir "__tests__/notification-deeplink.test.ts"
  if (Test-Path -LiteralPath $pushTest) {
    Remove-Item -LiteralPath $pushTest -Force
  }
}

if (-not $WithDataLayer.IsPresent) {
  $asyncTest = Join-Path $projectDir "__tests__/async-resource.test.ts"
  if (Test-Path -LiteralPath $asyncTest) {
    Remove-Item -LiteralPath $asyncTest -Force
  }
}

$easTemplatePath = Join-Path $skillRoot "assets/templates/eas.json.template"
$easPath = Join-Path $projectDir "eas.json"
if (Test-Path -LiteralPath $easTemplatePath) {
  Copy-Item -Path $easTemplatePath -Destination $easPath -Force
}
else {
  throw "Missing EAS template: $easTemplatePath"
}

$moduleFlags = [ordered]@{
  withTabs = [bool]$WithTabs.IsPresent
  useAppConfigTs = [bool]$UseAppConfigTs.IsPresent
  withUiFoundation = [bool]$WithUiFoundation.IsPresent
  withProfile = [bool]$WithProfile.IsPresent
  withAuth = [bool]$WithAuth.IsPresent
  withPush = [bool]$WithPush.IsPresent
  withDataLayer = [bool]$WithDataLayer.IsPresent
  withAnalytics = [bool]$WithAnalytics.IsPresent
  withCrashReporting = [bool]$WithCrashReporting.IsPresent
  withLocalization = [bool]$WithLocalization.IsPresent
  withAccessibilityChecks = [bool]$WithAccessibilityChecks.IsPresent
  withPrivacyChecklist = [bool]$WithPrivacyChecklist.IsPresent
}

if ($UseAppConfigTs.IsPresent) {
  Write-Step "Configuring app.config.ts mode."
  Configure-AppConfigTs -ProjectDir $projectDir -SkillRoot $skillRoot -AppName $AppName -BundleId $BundleId -ModuleFlags $moduleFlags
  Configure-AppJson -ProjectDir $projectDir -BundleId $BundleId -ModuleFlags $moduleFlags
}
else {
  Write-Step "Configuring app.json mode."
  Configure-AppJson -ProjectDir $projectDir -BundleId $BundleId -ModuleFlags $moduleFlags
}

Write-ModuleMetadata -ProjectDir $projectDir -Flags $moduleFlags -ReleaseBranch $ReleaseBranch
Ensure-GitIgnoreEntries -ProjectDir $projectDir

Write-Step "Scaffold completed at: $projectDir"
Write-Step "Next: run scripts/validate_expo_ios_project.py --project-dir `"$projectDir`""
