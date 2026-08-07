# ACPIA Audio Intelligence Agent

## Purpose
The **Audio Intelligence Agent** processes vocal and ambient audio tracks (phone calls, voicemail recordings, ambient recordings, video audio tracks) into time-aligned speech transcriptions and speaker shifts.

## Architecture
- **Dispatcher:** Registers and selects enabled acoustic processors.
- **Processors:** All classes inherit from `BaseProcessor` and implement unified `.process(audio_data, context)` routines.
- **Pipeline:** Runs checksum validations, extracts RMS decibels (quality, noise level), detects voice activity (VAD), diarizes speaker clusters, runs Whisper transcription, and spots keywords.

## Supported Formats
- WAV, MP3, AAC, FLAC, M4A, OGG.

## Running Tests
Run all audio tests from root directory:
```bash
python -m pytest backend/agents/audio_intelligence/tests/
```
