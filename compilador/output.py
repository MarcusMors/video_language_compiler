from moviepy.editor import *
from moviepy.video.fx.all import *
from moviepy.audio.fx.all import *

ancho = 1920
alto = "1080"
escala = 1.5
titulo = "Mi video personal"
intro = VideoFileClip("intro.mp4")
cancion = AudioFileClip("musica.mp3")
ancho = ((ancho + (80 / 2)) - 10)
escala = ((escala * 2.0) / 3.0)
intro = .resize()
intro = .fx(vfx.mirror_y)
intro = .speedx(1.0)
intro = .fadein(1.0)
intro = .fadeout(1.0)
intro = .without_audio()
intro = .without_audio()
intro = .set_audio(None)
intro = .concatenate_videoclips([])
intro = .subclip(0)
es_horizontal = 1
if es_horizontal:
    intro = .fx(vfx.mirror_y)
else:
    intro = .fx(vfx.mirror_y)
i = 0
if (es_horizontal == 0):
    i = 0
    while (i < 3):
        intro = .fx(vfx.mirror_y)
        i = (i + 1)
else:
    intro = .fx(vfx.mirror_y)
i = 0
while (i < 3):
    intro = .speedx(1.0)
    j = 0
    while (j < 3):
        intro = .speedx(1.0)
        j = (j + 1)
    i = (i + 1)
i = 0
while (i < 3):
    intro = .speedx(1.0)
    j = 0
    if (i == 5):
        while (j < 30):
            j = (j + 1)
    else:
        j = 15
        while (j > 0):
            j = (j - 1)
    i = (i + 1)
intro.write_videofile("salida.mp4")
cancion.write_audiofile("salida.mp3")