"""Sequências visuais independentes das regras de combate."""

import json
from pathlib import Path
from .catalog import SPELLS

ANIMATIONS = json.loads((Path(__file__).resolve().parent.parent / "data" / "animations.json").read_text(encoding="utf-8"))


def frame_index(age, fps, count):
    if count < 1:
        raise ValueError("A animação precisa de pelo menos um quadro.")
    return int(max(0, age)*max(0, fps)+1e-8) % count


def projectile_frame(key, age, progress):
    sequence = ANIMATIONS[key]
    if sequence.get('stages'):
        return sequence['stages'][min(2, int(max(0, age)/.5))]
    if key == 'yami_matoi':
        return 0 if progress < .12 else 1 if progress < .72 else 2 if progress < .86 else 3
    return frame_index(age, SPELLS[key]['animation_fps'], len(sequence['frames']))
