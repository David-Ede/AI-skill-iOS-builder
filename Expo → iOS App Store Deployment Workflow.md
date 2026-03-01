🚀 Expo → iOS App Store Deployment Workflow
PHASE 1 — One-Time Project Configuration
1️⃣ Confirm your iOS config

Open app.json (or app.config.js) and verify:

{
  "expo": {
    "name": "Your App Name",
    "slug": "your-app-slug",
    "version": "1.0.0",
    "ios": {
      "bundleIdentifier": "com.yourcompany.yourapp",
      "buildNumber": "1",
      "config": {
        "usesNonExemptEncryption": false
      }
    }
  }
}
Rules

bundleIdentifier must match exactly what you create in App Store Connect.

version = user-facing version.

buildNumber must increase every upload.

Set `ios.config.usesNonExemptEncryption` explicitly (`false` unless your app uses non-exempt encryption).

2️⃣ Configure EAS (if not already)

From repo root:

eas build:configure

Ensure eas.json contains:

{
  "build": {
    "production": {
      "ios": {
        "distribution": "store"
      }
    }
  },
  "submit": {
    "production": {}
  }
}
PHASE 2 — Create App in App Store Connect

Go to:

App Store Connect → Apps → + → New App

You must enter:

App Name

Primary language

Bundle ID (must match ios.bundleIdentifier)

SKU (any unique internal string)

You do NOT need screenshots yet for TestFlight.

PHASE 3 — Build the Store IPA with EAS

From your project:

eas build -p ios --profile production
During first build:

Choose “Let Expo handle credentials”

Log into Apple if prompted

Allow EAS to generate certificates & provisioning profiles

When finished:

You get a signed .ipa

You get a build URL

You now have a production App Store–signed binary.

PHASE 4 — Submit to TestFlight
1️⃣ Create App Store Connect API Key (recommended)

App Store Connect → Users and Access → Keys → App Store Connect API

Create key

Download .p8

Copy:

Key ID

Issuer ID

2️⃣ Submit via EAS
eas submit -p ios --profile production

First time:

Enter API key info

It stores securely in Expo

You can also combine build + submit:

eas build -p ios --profile production --auto-submit
PHASE 5 — TestFlight

Go to:

App Store Connect → Your App → TestFlight

Wait for “Processing” to finish.

Add Internal Testers.

Install via TestFlight.

Fully test on real devices.

If you want public testers:

Add External Testers

Complete Beta App Review

PHASE 6 — Prepare App Store Listing

Go to:

App Store Connect → Your App → App Store → Prepare for Submission

You must complete:

Required

Screenshots (all required device sizes)

Description

Keywords

Support URL

Privacy Policy URL

Age rating questionnaire

App Privacy “Nutrition Label”

Optional but recommended

App preview video

Promotional text

PHASE 7 — Submit for Review

Select your uploaded build.

Answer export compliance questions.

Add Review Notes (very important):

Demo account if login required

Any special setup steps

Choose release option:

Manual release (recommended first time)

Automatic release

Click Submit for Review.

PHASE 8 — After Approval

Release manually (if selected)

Monitor:

Crashes (App Store Connect → Crashes)

Analytics

Prepare 1.0.1 quickly if needed
