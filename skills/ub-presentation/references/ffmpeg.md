# ffmpeg Notes

This skill expects both `ffmpeg` and `ffprobe` to be available on `PATH`.

Render behavior:

- One video clip is created per slide.
- Each clip loops the slide image for the exact duration of that slide's MP3.
- Clips are concatenated into `final.mp4`.
- The output is encoded with H.264 video and AAC audio for broad compatibility.

If validation reports missing tools, install ffmpeg with the local system package manager before rendering.
