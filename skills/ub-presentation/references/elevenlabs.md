# ElevenLabs Notes

The scripts use the ElevenLabs Text to Speech REST API:

```text
POST https://api.elevenlabs.io/v1/text-to-speech/:voice_id?output_format=mp3_44100_128
```

Required environment values:

```dotenv
ELEVENLABS_API_KEY=replace_me
ELEVENLABS_VOICE_ID=replace_me
ELEVENLABS_MODEL_ID=eleven_v3
ELEVENLABS_OUTPUT_FORMAT=mp3_44100_128
```

Defaults:

- `eleven_v3` for more natural presentation narration with inline audio tags.
- `mp3_44100_128` for broad MP3 compatibility.

Narration is generated per segment. Segment text may start with ElevenLabs v3 audio tags such as `[calm]`, `[warmly]`, `[thoughtful]`, `[slight emphasis]`, or `[confident]`. Tags are not validated locally; they are passed to the model as written.

Generated segment files are stored under `voiceover/audio/slide-001/` and
concatenated with `pause_after_ms` silence into slide-level MP3 files such as
`voiceover/audio/slide-001.mp3`. Silence files and concat lists are disposable
build artifacts under `build/voiceover/`.

Do not print or commit the real API key. Keep it in `.env` or the process
environment. Scripts read the nearest `.env` found from the presentation
directory upward and do not override existing environment values.
