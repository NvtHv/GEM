# GEM - Gesture Recognition and Control

## 1) Vue d'ensemble des gestes supportés

| Geste | Action déclenchée | Onglets ciblés |
|---|---|---|
| Index levé + mouvement | Déplacer curseur / scroll PDF | PDF |
| Poing fermé | Play / Pause | MP3, MP4 |
| 2 doigts écartés | Zoom avant | PDF, Photos |
| 2 doigts serrés | Zoom arrière | PDF, Photos |
| Swipe droite | Page / chanson suivante | PDF, MP3, MP4 |
| Swipe gauche | Page / chanson précédente | PDF, MP3, MP4 |
| Index pointé vers le haut (statique) | Volume + | MP3, MP4 |

## 2) Architecture et fichiers importants

- `mainui.py` : lance l'interface graphique (CustomTkinter)
- `ui/main_window.py` : bouton `Activer GEM` (ON/OFF), lancement arrêt du thread de détection
- `gem_detector.py` : boucle vidéo + détection de gestes + callback `gesture_callback`
- `main.py` : lance la détection seule (sans UI)
- `gestures/` : implémentations des gestes
- `ui/pdf_viewer.py`, `ui/photo_viewer.py`, `ui/mp3_player.py`, `ui/mp4_player.py` : actions connectées

## 3) Fonctionnement dans chaque onglet

### PDF
- Scroll vertical : Index levé + mouvement
- Zoom avant/arrière : 2 doigts écartés/serrés
- Page suivante/précédente : Swipe droite/gauche

### MP3
- Play/pause : Poing fermé
- Next song : Swipe droite
- Previous song : Swipe gauche
- Volume + : Index pointé haut

### MP4
- Play/pause : Poing fermé
- Next song : Swipe droite
- Previous song : Swipe gauche
- Volume + : Index pointé haut

### Photos
- Zoom avant/arrière : 2 doigts écartés/serrés

## 4) Activation et test

1. Lancer : `python mainui.py`
2. Dans la fenêtre GEM : basculer `Activer GEM` sur ON.
3. Appliquer les gestes devant la caméra.
4. Les actions sont déclenchées automatiquement dans l'onglet actif.

## 5) Notes techniques

- `gestures` : chaque geste dérive de `BaseGesture` avec `detect()` + `action()`.
- `gem_detector.run_detection` appelle `gesture_callback` qui appelle `ui/main_window.py`.
- La version minimale de OpenCV doit fournir `cv2.VideoCapture`.
