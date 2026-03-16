# Gestures du projet GEM

Seuls les gestes suivants sont reconnus (la détection est lancée par le bouton `Activer GEM` dans l'interface UI) :

| Geste | Action déclenchée |
|---|---|
| Index levé + mouvement | Déplacer curseur / scroll PDF |
| Poing fermé | Play / Pause (MP3 & MP4) |
| 2 doigts écartés | Zoom avant (PDF / Vidéo) |
| 2 doigts serrés | Zoom arrière (PDF / Vidéo) |
| Swipe droite | Page / chanson suivante |
| Swipe gauche | Page / chanson précédente |
| Main ouverte (5 doigts) | Retour menu principal |
| Index pointé vers le haut (statique) | Volume + |

## Notes d'implémentation

- `main.py` appelle désormais `gem_detector.run_detection()`.
- `ui/main_window.py` active/désactive le thread de détection via le switch GEM.
- les gestes sont dans `gestures/` :
  - `index_move.py` (Index finger raised + movement)
  - `index_point_up.py` (Index finger pointing up static)
  - `fist.py`
  - `open_hand.py`
  - `pinch.py` (Zoom out)
  - `doublepinch.py` (Zoom in)
  - `swipe_left.py`
  - `swipe_right.py`

## Exécution

- Démarrer le programme GUI : `python mainui.py`
- Activer le jeu de gestes avec `Activer GEM` (interrupteur)

*Quelques fonctions d’action sont pour l’instant des `print(...)` et peuvent ensuite appeler le code réel MP3/MP4/PDF.*
