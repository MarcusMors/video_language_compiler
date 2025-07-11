from moviepy.editor import *
from moviepy.video.fx.all import *
from moviepy.audio.fx.all import *

intro = VideoFileClip("intro.mp4")
cancion = AudioFileClip("musica.mp3")
intro = intro.resize(width=1280, height=720)
intro = intro.fx(vfx.mirror_x)
intro = intro.speedx(factor=1)
intro.write_videofile("salida.mp4")
cancion.write_audiofile("salida.mp3")