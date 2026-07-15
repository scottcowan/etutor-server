# Hardware: Onyx Boox Android E-Ink Device

> Replaces the custom CM4 build. Commodity Android e-ink hardware runs a native
> Android app that connects to etutor-server over home WiFi.
> Research compiled 2026-07-15 from parallel web agents.

---

## Decision: Commodity Boox over Custom CM4

| Factor | CM4 custom build | Onyx Boox |
|--------|-----------------|-----------|
| Time to first device | 6-12 months (PCB, firmware) | Days (buy + sideload APK) |
| Per-device cost | ~£220 | £150-250 depending on model |
| Android app dev | Custom Linux stack | Standard Android SDK |
| Risk | High (untested hardware) | Low (mature commercial device) |
| Repairability | Owner-maintained | Warranty + replacement |
| E-ink refresh control | Full (custom firmware) | Full (Onyx SDK) |

---

## Recommended Models

GBP prices confirmed from PriceRunner/UK retailers July 2026. EUR from ereader.store.

### ⚠ Screen fragility warning
Boox devices use regular glass (not Gorilla Glass). Community reports of cracked screens from light pressure, bag compression, and spontaneous battery swell are widespread. Repair costs ~£250 — near the device price — and Boox's warranty covers nothing screen-related. **A ruggedised airbag-corner TPU case is mandatory before handing to a child.** Budget ~£8–15 on AliExpress; official Boox magnetic case ~£35.

### Primary: Boox Go Color 7 Gen II — £226.98 (confirmed)
- 7" Kaleido 3 color e-ink, 300ppi text / 150ppi color
- **Physical page-turn buttons on both sides** — important for younger children (7", 195g, 156×137mm)
- Microphone + speaker, **Android 12**, 2,300mAh
- Color quality is muted/washed-out compared to LCD — fine for text-heavy tutoring, limited for picture books
- USD $269.99 / EUR €289.99

### Second: Boox Palma 2 — £335.98 (confirmed, over budget)
- **Dual microphones** — only sub-10" model with dual mics; better for child speech capture
- Phone form factor (159×80mm, 170g) — very holdable, good for portability
- Single speaker — pair with Bluetooth speaker for room-filling TTS
- **Android 13**, 3,950mAh (best battery of any small model)
- Screen is 6.13" — marginal for a beginning reader aged 6–7

### Desk device: Boox Go 10.3 Gen II (~£315)
- **Dual stereo speakers** — noticeably better TTS output
- 10.3", ~350g — too heavy for a child to handheld, good on a desk
- Single microphone, no physical page-turn buttons, **Android 15**

### Mono budget option: Boox Go 7 (~£180–190, unconfirmed GBP)
- Same physical form factor as Go Color 7 Gen II (156×137mm, 195g)
- No colour — but voice-first tutoring is text-heavy, colour matters less
- **Android 13**, same mic/speaker/buttons spec
- Likely cheapest option within or near the £200 budget

### To avoid
- **Boox Go 6 Gen II** — no confirmed built-in speaker
- **Boox Leaf 3C, Nova Air C, Tab Mini C** — discontinued/sold out
- **Kobo / Kindle / PocketBook / reMarkable** — proprietary OS, no APK sideloading, no mic
- **PineNote** — no working Android build as of November 2024

### Three actions before buying
1. Buy a Go Color 7 Gen II + airbag TPU case (~£235 total)
2. Test `AudioRecord` at 16 kHz with a real child speaker — measure WER against etutor-server Whisper
3. Test foreground service survival: start the service, lock screen for 10 minutes, verify it's still running

---

## Onyx Boox Android SDK

### Maven Coordinates
```gradle
repositories {
    maven { url "http://repo.boox.com/repository/maven-public/" }
    maven { url "https://jitpack.io" }  // for transitive deps
}

dependencies {
    implementation 'com.onyx.android.sdk:onyxsdk-device:1.3.5'
    implementation 'com.onyx.android.sdk:onyxsdk-pen:1.5.4'
    implementation 'com.onyx.android.sdk:onyxsdk-base:1.4.3.7'
}
```

### Official Reference
- **Demo repo**: https://github.com/onyx-intl/OnyxAndroidDemo — 249 commits, includes `/doc/EPD-Update-Mode.md` and design guide
- **SDK mirror** (full source): https://github.com/hbmartin/onyx-android-sdk
- **Internals reference**: https://github.com/timschneeb/OnyxTweaks — Xposed module revealing config format and feature gates
- **etutor-specific skills**: https://github.com/mbulling83/boox-eink-skills

### Delivery Model
The SDK JAR ships `compileOnly` — the implementation lives in `/system/framework/onyx.jar` on the device. Use reflection for non-Boox compatibility:
```java
Class<?> c = Class.forName("com.onyx.android.sdk.api.device.epd.EpdController");
// wrap in try/catch — degrades gracefully on non-Boox Android
```

---

## E-Ink Refresh API

### UpdateMode Enum
```
DU              — 1-bit fast partial (most ghosting, ~A2)
DU_QUALITY      — 1-bit cleaner partial
GU / GU_FAST    — 16-grey partial (standard text scroll)
GC / GC4        — full refresh (clears ghosting)
DEEP_GC         — deep full refresh
REGAL / REGAL_D / REGAL_PLUS — anti-ghost partial, optimised for text
ANIMATION / ANIMATION_QUALITY / ANIMATION_MONO / ANIMATION_X — video modes
HAND_WRITING_REPAINT_MODE — stylus overlay
```

### Key Methods (EpdController, all static)
```java
EpdController.invalidate(View v, UpdateMode mode);
EpdController.postInvalidate(View v, UpdateMode mode);
EpdController.setViewDefaultUpdateMode(View v, UpdateMode);   // sticky per-View
EpdController.resetViewUpdateMode(View v);
EpdController.refreshScreenRegion(View v, int l, int t, int w, int h, UpdateMode);
EpdController.applyAppScopeUpdate(String pkg, boolean, boolean, UpdateMode, int repeatLimit);
EpdController.setWebViewContrastOptimize(WebView, boolean);
EpdController.waitForUpdateFinished();
EpdController.supportRegal();
```

### Anti-Ghost Pattern
```java
// Clear ghosting every 20 partial refreshes
EpdController.applyAppScopeUpdate(pkg, true, true, UpdateMode.GC, 20);
```

### WebView Pattern (for web-based UI)
```java
EpdController.setWebViewContrastOptimize(webView, true);           // dithering + contrast
EpdController.setViewDefaultUpdateMode(webView, UpdateMode.REGAL); // text scrolling
// periodically: EpdController.invalidate(webView, UpdateMode.GC); // force full clear
```

### Design Rules (from Onyx Eink-Develop-Guide.md)
- Minimum font size: 14sp
- Minimum touch target: 36dp
- **No animations** — all CSS transitions and Android Animated must be off
- **No transparent layers** — compositing is expensive on e-ink
- **Page-based navigation, not scroll** — partial refresh on scroll causes ghosting
- 16-level grayscale maximum

---

## App Development Approach

### Recommendation: Native Kotlin + WebView shell

| Approach | Verdict |
|----------|---------|
| **Native Kotlin/Java** | Best — direct `EpdController` access, what Onyx expects |
| **WebView + thin native shell** | Good — Onyx builds their own apps this way; JS bridge to EpdController straightforward |
| **React Native** | Workable but no community precedent; needs custom native modules for refresh |
| **Flutter** | **Avoid** — Skia renders to opaque bitmap surface, no per-View refresh mode control, heavy ghosting |

**Practical recommendation**: Kotlin native shell that embeds a WebView for UI (React/Vue SPA). The shell handles:
- `EpdController` refresh mode calls
- `AudioRecord` (STT microphone)
- `MediaPlayer` / ExoPlayer (TTS playback)
- Device registration and token storage
- Wake word detection

The WebView renders the tutor UI. JS calls the native shell via `JavascriptInterface` for refresh mode changes.

### ADB / Sideloading
- Developer mode: Settings → About → tap build number 7× → toggle USB debugging
- **No vendor lockdown** — Onyx is developer-friendly
- Unknown sources / sideload APK allowed from Settings
- Google Play available on most current models (requires activation via Boox settings toggle)
- F-Droid works fine

---

## Audio

### Microphone
- Palma 2: **dual microphones** — best for noisy environments, potential beamforming
- Go 10.3: **single microphone**
- Standard Android `AudioRecord` API — no Boox-specific quirks found
- Runtime permission: `RECORD_AUDIO`
- **Child speech target**: 16kHz mono 16-bit PCM for Whisper STT

### TTS (Text-to-Speech)

**Architecture**: server-side TTS preferred (Piper/Kokoro on etutor-server), but on-device fallback needed for offline use.

#### Server-side (primary)
- `POST /v1/audio/speech` on etutor-server returns WAV/MP3 bytes
- Device plays via `MediaPlayer` / `ExoPlayer`
- Piper amy-low latency: **~524ms** (voiceping.net benchmark)

#### On-device fallback
**Recommended**: `aitorpazos/piper-tts-android` (https://github.com/aitorpazos/piper-tts-android)
- v1.21.0, March 2026 — **actively maintained**
- Registers as Android system TTS provider — any app using `TextToSpeech` API gets Piper voices
- ONNX Runtime mobile, low-quality models ~15MB, medium ~60MB
- Cleanest integration: device-side app just calls standard Android TTS API

**Alternative on-device**: sherpa-onnx Kokoro-82M
- ~80MB int8 quantized
- CPU-only (NPU doesn't work — dynamic shapes, unsupported ops)
- Higher quality than Piper but larger

**Do not use**: Google TTS — Boox runs AOSP without GMS, Google TTS engine not present.
**Do not use**: eSpeak-ng, RHVoice, Flite — all produce robotic voices unsuitable for child UX.

#### Children's voices
**There are no purpose-trained children's TTS voices in any offline Android engine** (as of 2026-07-15). The tutor voice will be an adult voice — this is fine, Miranda's voice in the Primer was an adult woman's voice too.

---

## Wake Word / Activation

### Recommendation: Tap-to-talk (hold physical button)

Porcupine's **free custom wake word tier ended June 30, 2026** — custom "Hey Tutor" now requires an enterprise contract (pricing unpublished, likely $1,000+/year). Always-on software wake word on Boox (no hardware DSP) costs **30–80 mAh/hour** — roughly 8–25% battery drain per hour on standby. For a child's dedicated device with physical page-turn buttons, **hold-to-speak is more reliable and zero battery cost**.

**Start with tap-to-talk. Revisit wake word only if usage patterns demand it.**

### If wake word is needed later
- **sherpa-onnx KWS** (https://github.com/k2-fsa/sherpa-onnx) — Apache-2.0, Android APKs provided, ONNX Runtime — the clean open-source path
- **Porcupine built-in keywords** (Apache-2.0 free): ~10 built-in phrases remain free; custom training is now enterprise-only

### Do not use
- **Snowboy** — abandoned 2018, vendor sunset 2020
- **openWakeWord** — no Android port; pre-trained models are CC-BY-NC-SA (non-commercial)
- **microWakeWord** — microcontroller-only

## VAD (Voice Activity Detection)

Use **Silero VAD** via `android-vad:silero` (https://github.com/gkonovalov/android-vad):
- DNN-based, ROC-AUC 0.97 vs WebRTC GMM 0.73
- Handles children's higher pitch (200–400 Hz) — WebRTC GMM was trained on adult speech (85–180 Hz)
- ~2MB ONNX model

**Critical: set silence threshold to 600–800ms** for ages 6–8 (default 300ms is too aggressive — children pause mid-thought). Build this state machine on top of the library:
```
SILENCE → [speech_prob > 0.5] → SPEAKING → [silence ≥ 700ms] → SEND_TO_SERVER
```

Note: a crash in Silero 2.0.10 is open as of September 2025 (issue #39) — test on target device.

---

## Server Changes Required for Android Client

The server gap analysis identified 9 gaps. Priority order:

### Add (net-new endpoints)
| Endpoint | Priority | Notes |
|----------|----------|-------|
| `POST /v1/devices/{id}/claim` | High | Pair device to child profile via one-time code from parent dashboard |
| `POST /v1/devices/{id}/events` | High | Batch interaction events from device (SYNC-02); must be idempotent |
| `POST /v1/audio/speech` | High | Server-side TTS — returns WAV bytes; OpenAI-compatible signature |
| `POST /v1/sessions` | Medium | Explicit session start — device needs session_id before going offline |
| `PATCH /v1/sessions/{id}/end` | Medium | Session close trigger for BKT batch update (Phase 2) |

### Fix existing endpoints
| Endpoint | Fix |
|----------|-----|
| `POST /v1/audio/transcriptions` | Fix temp file suffix — Android sends M4A not WAV; derive suffix from content-type |
| `GET /v1/devices/{id}/sync` | Add ETag header; add focus KCs + mastery buckets when Phase 2 is done |
| All device routes | Add device token auth (static bearer token, not mTLS) |
| `api/main.py` | Narrow `allow_origins=["*"]` to configured list |

### Schema additions
- `ChildProfileModel`: add `device_token` (nullable), `registered_at`
- New: `DevicePairingCode` table (one-time codes, TTL)
- New: `ContentPackageModel` (KC-level offline bundles, `expires_at`)

### WebSocket vs HTTP
Prefer a **persistent WebSocket** over per-request HTTP for the audio pipeline. It amortizes the TCP handshake across the session (measured difference TCP vs UDP on local WiFi: 0.05ms — negligible). SSE streaming in `api/chat.py` is fine for text; for audio upload + TTS streaming, WebSocket is cleaner.

---

## Audio Latency Budget

Target: **<2s end-to-end** (VAD end → first TTS word from speaker)

| Stage | With server GPU | CPU-only server | Notes |
|-------|----------------|-----------------|-------|
| VAD detection + crop | ~80ms | ~80ms | Silero VAD; 700ms silence threshold already elapsed |
| WiFi upload (5 GHz) | ~15ms | ~15ms | Home LAN |
| Whisper STT (faster-whisper small-int8) | ~500ms | ~900ms | RTF ~0.08 GPU / ~0.13 CPU |
| Claude Haiku TTFT (Vertex AI) | ~600ms | ~600ms | 350ms faster than Anthropic direct |
| Claude Haiku TTFT (Anthropic direct) | ~950ms | ~950ms | Falls back to this if Vertex unavailable |
| Piper TTS first sentence | ~180ms | ~180ms | RTF ~0.06 on i5 |
| WiFi download + ExoPlayer buffer (tuned 200ms) | ~275ms | ~275ms | Default 1,000ms buffer BREAKS this — must reconfigure |
| **Total (GPU + Vertex)** | **~1.65s** | — | ✓ Within target |
| **Total (CPU + Vertex)** | — | **~2.05s** | Borderline — use distil-whisper + stream first sentence |
| **Total (CPU + Anthropic direct)** | — | **~2.40s** | Over budget |

**Critical:** ExoPlayer's default `bufferForPlaybackMs = 1,000ms` alone breaks the 2s target. Reconfigure to 200ms:
```kotlin
DefaultLoadControl.Builder()
    .setBufferDurationsMs(1000, 10000, 200, 500)
    .build()
```

**Without a GPU:** Use Vertex AI for Claude (saves ~350ms TTFT) + distil-whisper-small-int8 (~2x faster than vanilla Whisper) + start streaming Piper before LLM finishes. This recovers enough margin.

Screen refresh (300ms partial) runs **in parallel** with audio — not in the critical path.

---

## Critical Gotchas

### Whisper cannot run on-device
On ARM Android without GPU/NNAPI acceleration, Whisper runs **10–31x slower than real-time**. A 3-second child audio clip takes ~31 seconds. The <2s latency target requires server-side Whisper — always. This is already the architecture; this confirms it is the only viable approach.

### Background service survival (Boox Android 12, OS 3.5+)
Boox battery optimisation kills background services. `Unrestricted` battery mode silently reverts to `Restricted` for some apps. ADB whitelist commands have no effect in this state.

**Required mitigations:**
```xml
<service android:name=".TutorService"
         android:foregroundServiceType="microphone"
         android:exported="false" />
```
Also acquire `PARTIAL_WAKE_LOCK` in the service — foreground service alone is insufficient. On Android 14+ (`Palma 2 Pro`, `Note Air 5C`), the `foregroundServiceType="microphone"` declaration is **mandatory** or the app crashes at install.

Users may need to manually disable "App Freeze" for the app in Boox system settings — document this in the app's setup flow.

### Hardware video codec disabled (Boox firmware 3.x+)
Onyx disabled H.264/HEVC hardware encoders as a side-effect of their screen mirroring feature. **Audio codecs (AAC software encoder) are unaffected**, but verify if using `MediaCodec` anywhere in the audio pipeline.

### Audio recording while screen is off
Untested on Boox specifically. The wake lock + foreground service pattern above should keep the audio subsystem active, but verify on the target device before shipping.

### Bluetooth audio configuration changes
BT headset connect/disconnect triggers an Android `AudioManager` configuration change. Test that the app doesn't crash when a child plugs in headphones mid-session.

### ADB / Developer mode path (non-standard on Boox)
The standard Android "tap Build Number 7 times" path does NOT work on Boox. The actual path:
```
Apps (top-right menu) → App Management → Enable USB Debug Mode
```
On some models (Note Air 3), a third-party "Android Hidden Settings" app is needed to reach the Build Number field.

### AudioRecord: capture at 48kHz, not 16kHz
Requesting 16kHz directly forces the Android kernel resampler, which evicts the track from FastMixer and adds ~20ms latency. **Always capture at 48kHz and downsample in software:**
```kotlin
val recorder = AudioRecord(
    MediaRecorder.AudioSource.VOICE_RECOGNITION,  // NOT MIC — disables OEM AGC/noise suppression
    48000, CHANNEL_IN_MONO, ENCODING_PCM_16BIT,
    AudioRecord.getMinBufferSize(48000, CHANNEL_IN_MONO, ENCODING_PCM_16BIT) * 4
)
// Downsample 48kHz → 16kHz (3:1) before sending to Whisper
```
Use `VOICE_RECOGNITION` not `MIC` — the whisper.cpp Android example uses `MIC` and this is wrong for production.

### No 3.5mm jack on any current Boox model
All current Boox devices are USB-C audio only. Plan for USB-C adapter or Bluetooth speaker/headphones for children who need clearer audio output.

---

## Open Questions

- [ ] Buy Go Color 7 Gen II first — test `AudioRecord` at 16 kHz with real child speech
- [ ] Wake word phrase — "Hey Tutor"? needs Porcupine Console training or sherpa-onnx custom model
- [ ] Kiosk mode — Android app pinning via `startLockTask()` for child safety
- [ ] Boox parental controls — app blocking, screen time limits

---

## Reference Repos

| Repo | Purpose |
|------|---------|
| https://github.com/onyx-intl/OnyxAndroidDemo | Official Onyx SDK demos + EPD docs |
| https://github.com/onyx-intl/public-wiki | Official dev docs and EPD mode reference |
| https://github.com/hbmartin/onyx-android-sdk | Full SDK source mirror |
| https://github.com/timschneeb/OnyxTweaks | Boox internals (MMKV config, feature flags) |
| https://github.com/mbulling83/boox-eink-skills | Claude Code skills for Boox Android dev |
| **https://github.com/BoltAI/Inka** | **Native Kotlin AI app for Boox Note Air — BYOK Anthropic/OpenAI, closest analog to etutor client** |
| https://github.com/alexdremov/notate | Best native Kotlin Boox app, EpdController patterns |
| https://github.com/lEWFkRAD/hermes-agents-guide-to-the-galaxy | Device↔server architecture matching etutor-server |
| https://github.com/aitorpazos/piper-tts-android | Piper as Android system TTS provider (v1.21.0, Mar 2026) |
| https://github.com/k2-fsa/sherpa-onnx | ONNX KWS + TTS for Android (Apache-2.0) |
| https://github.com/Picovoice/porcupine | Porcupine wake word (Android SDK) |
| https://github.com/lad6mntzezhbll4d-dev/boox-ai-reader | EpdController reflection pattern for non-Boox compat |
| https://github.com/buggins/coolreader | Real reader app with Onyx integration |
| https://github.com/koreader/koreader | Dominant open-source e-reader; TTS + spaced repetition; runs on Boox |

---

*Research: parallel web agents, 2026-07-15. Models/pricing agent pending — verify Boox UK pricing before ordering.*
