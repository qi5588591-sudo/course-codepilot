"""Assemble narrated engineering slides, explicitly not a live model recording.

Authoring dependency: pip install imageio-ffmpeg. Speech comes from build-narration.ps1.
"""
from pathlib import Path
import subprocess

import imageio_ffmpeg

root=Path(__file__).resolve().parents[1]
ffmpeg=imageio_ffmpeg.get_ffmpeg_exe()
clips=[]
for number in range(1,11):
    image=root/f'build/slides/slide-{number:02}.png'
    audio=root/f'build/audio/speech-{number:02}.wav'
    clip=root/f'build/clip-{number:02}.mp4'
    subprocess.run([ffmpeg,'-y','-loglevel','error','-loop','1','-i',str(image),'-i',str(audio),
        '-c:v','libx264','-preset','fast','-tune','stillimage','-r','10','-c:a','aac','-ar','44100',
        '-pix_fmt','yuv420p','-shortest',str(clip)],check=True)
    clips.append(clip)
    print('Encoded slide',number,flush=True)
concat=root/'build/video-concat.txt'
concat.write_text('\n'.join("file '"+p.as_posix()+"'" for p in clips),encoding='utf-8')
output=root/'deliverables/工程讲解_非实机模型演示.mp4'
subprocess.run([ffmpeg,'-y','-loglevel','error','-f','concat','-safe','0','-i',str(concat),
    '-c','copy','-movflags','+faststart',str(output)],check=True)
print(output)
