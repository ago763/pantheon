"""Converte o PNG do Pantheon para ICO nos tamanhos usados pelo Windows."""
from pathlib import Path
from io import BytesIO
import struct
import pygame

root = Path(__file__).resolve().parent.parent
source = pygame.image.load(str(root / 'assets/images/ui/pantheon-icon.png'))
sizes = (16, 24, 32, 48, 64, 128, 256)
images = []
for size in sizes:
    output = BytesIO()
    pygame.image.save(pygame.transform.smoothscale(source, (size, size)), output, 'icon.png')
    images.append(output.getvalue())
offset = 6 + 16 * len(sizes)
directory = bytearray(struct.pack('<HHH', 0, 1, len(sizes)))
for size, image in zip(sizes, images):
    directory.extend(struct.pack('<BBBBHHII', size % 256, size % 256, 0, 0, 1, 32, len(image), offset))
    offset += len(image)
(root / 'assets/images/ui/pantheon.ico').write_bytes(directory + b''.join(images))
