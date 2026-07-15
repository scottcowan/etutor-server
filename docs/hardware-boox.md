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

### Primary: Boox Palma 2 (6")
- **Dual microphones** — best audio capture for child voice
- **Dual speakers** — good for TTS playback
- **Pocket-sized** — holdable by a 6-year-old single-handed
- Android 13, ~3950mAh battery
- ~£180-200 UK

### Alternative: Boox Go 10.3 (10.3")
- **Built-in microphone + dual speakers**
- Larger screen — better for reading/illustrations
- Heavier — may be harder for younger children to hold portably
- Good as a desk device
- ~£220-250 UK

### To avoid
- **Boox Leaf / Poke / basic Go 6** — most lack microphones entirely
- **Kobo / Kindle** — no Android custom app support (or severely restricted)
- **reMarkable** — Linux, no Android APK, no mic/speaker

### Color E-Ink: Boox Go Color 7 / Leaf 3C
- Kaleido 3 color e-ink — acceptable for illustrations, ~4096 colours
- Refresh is slower on color panels and color contrast is muted
- Worth considering for the illustration library feature but not essential for v1

---

## Onyx Boox Android SDK

### Maven Coordinates
```gradle
repositories {
    maven { url "http://repo.boox.com/repository/maven-public/" }
    maven { url "https://jitpack.io" }  // for transitive deps
}

dependencies {
    implementation 'com.onyx.android.sdk:onyxsdk-device:1.1.11'
    implementation 'com.onyx.android.sdk:onyxsdk-pen:1.2.1'
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

## Wake Word Detection

### Recommendation: Picovoice Porcupine (free personal tier)
- **Official Android SDK** — well-maintained, first-class support
- Requires AccessKey from Picovoice Console (free for personal/non-commercial)
- 0.6% CPU on RPi5 (vendor claim); negligible battery impact with hardware DSP
- Custom wake words via Picovoice Console
- "Hey Tutor" will need to be trained

### Alternative: sherpa-onnx KWS (fully Apache-2.0)
- https://github.com/k2-fsa/sherpa-onnx
- Pre-built Android APKs for keyword spotting
- ONNX Runtime, Kotlin/Java API
- No licensing concerns
- Less mature Android tooling than Porcupine

### Do not use
- **Snowboy** — abandoned since 2018, vendor sunset 2020
- **openWakeWord** — no official Android port; pre-trained models are **CC-BY-NC-SA** (non-commercial only)
- **microWakeWord** — microcontroller-only (ESPHome)

### Battery Impact (wake word always-on)
On non-Snapdragon SoCs (which Boox uses — typically Rockchip/i.MX without Hexagon DSP):
- Estimated **0.5–2%/day** battery drain running wake word on Cortex-A CPU
- Acceptable for the 3000-4000mAh batteries in Palma 2 / Go 10.3

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
No WebSocket needed. The 3-hop HTTP flow (STT → chat SSE → TTS) meets <2s target on home LAN. SSE streaming already implemented in `api/chat.py`.

---

## Audio Latency Budget

Target: **<2s end-to-end** (VAD end → first TTS word from speaker)

| Stage | Estimate | Notes |
|-------|----------|-------|
| VAD detection + crop | ~50ms | Silero VAD on device |
| WiFi upload (WAV) | ~50ms | Home LAN, ~300KB audio |
| Whisper STT (base.en) | ~300-500ms | On home server GPU/CPU |
| LLM TTFT (Haiku) | ~300-500ms | Claude API, first token |
| TTS synthesis (Piper) | ~500ms | Server-side, full response |
| WiFi download (WAV) | ~50ms | |
| `MediaPlayer` buffer + play | ~100ms | |
| **Total** | **~1.35–1.75s** | Within 2s target |

Screen refresh (300ms partial) runs **in parallel** with audio — not in the critical path.

---

## Open Questions

- [ ] Which specific Boox model to buy first (Palma 2 vs Go 10.3)
- [ ] Wake word phrase — "Hey Tutor"? needs Porcupine Console training
- [ ] Kiosk mode / single-app lock for child safety (Android app pinning via `startLockTask()`)
- [ ] Boox parental controls — app blocking, usage time limits
- [ ] Pricing verification — confirm current UK pricing before ordering

---

## Reference Repos

| Repo | Purpose |
|------|---------|
| https://github.com/onyx-intl/OnyxAndroidDemo | Official Onyx SDK demos + EPD docs |
| https://github.com/hbmartin/onyx-android-sdk | Full SDK source mirror |
| https://github.com/timschneeb/OnyxTweaks | Boox internals (MMKV config, feature flags) |
| https://github.com/mbulling83/boox-eink-skills | Claude Code skills for Boox Android dev |
| https://github.com/aitorpazos/piper-tts-android | Piper as Android system TTS provider |
| https://github.com/k2-fsa/sherpa-onnx | ONNX KWS + TTS for Android |
| https://github.com/Picovoice/porcupine | Porcupine wake word (Android SDK) |
| https://github.com/lad6mntzezhbll4d-dev/boox-ai-reader | EpdController reflection pattern |
| https://github.com/buggins/coolreader | Real reader app with Onyx integration |

---

*Research: parallel web agents, 2026-07-15. Models/pricing agent pending — verify Boox UK pricing before ordering.*
