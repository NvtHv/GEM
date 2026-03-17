# 🖐️ GEM — Gesture Control

Contrôle du lecteur audio par reconnaissance de gestes via webcam.

---

## Mapping des gestes

| Geste | Doigts | Classe | Action |
|-------|--------|--------|--------|
| ☝️ Index seul | Index levé, autres baissés | `IndexPointUp` | Volume + |
| ✌️ Deux doigts | Index + majeur levés, autres baissés | `TwoFingersUp` | Volume - |
| 🖐️ Main ouverte | Les 5 doigts levés | `OpenHand` | Play / Pause |
| 🤙 Auriculaire seul | Auriculaire levé, index + majeur + annulaire baissés | `PinkyUp` | Piste suivante |
| 🖕🖕 Majeur + annulaire | Majeur + annulaire levés, index + auriculaire baissés | `MiddleRingUp` | Piste précédente |

---

## Détection

La détection repose sur la comparaison verticale (axe Y) des landmarks MediaPipe :

- **Doigt levé** : `pip[2] > tip[2]` — l'articulation est plus basse que le bout du doigt
- **Doigt baissé** : `tip[2] > pip[2]` — le bout du doigt est plus bas que l'articulation

> Le pouce n'est pas utilisé dans la détection car il se déplace sur l'axe horizontal (X),
> ce qui le rend peu fiable et dépendant de la main (gauche/droite).

---

## Configuration (`run_detection`)

```python
run_detection(
    stop_fn=None,          # fonction renvoyant True pour stopper la boucle
    gesture_callback=None, # appelé avec le nom du geste détecté (ou None)
    mirror=True            # activer/désactiver le mode miroir (cv2.flip)
)
```

### Mode miroir

```python
if mirror:
    img = cv2.flip(img, 1)  # appliqué avant find_hands() et find_position()
```

> Important : le flip doit être appliqué **avant** la détection des landmarks
> pour que la cohérence gauche/droite soit respectée à l'écran.

---

## Cooldown

Pour éviter les faux positifs lors des transitions entre gestes :

```python
COOLDOWN = 1.0      # secondes min entre deux déclenchements du même geste
RESET_DELAY = 0.8   # secondes sans geste avant de réinitialiser le dernier geste détecté
```

Le `last_gesture` est réinitialisé uniquement après `RESET_DELAY` secondes
de silence continu — pas à chaque frame neutre.

---

## Structure des fichiers

```
gestures/
├── __init__.py
├── open_hand.py         # 🖐️ Play / Pause
├── index_point_up.py    # ☝️  Volume +
├── two_fingers_up.py    # ✌️  Volume -
├── pinky_up.py          # 🤙 Next
└── middle_ring_up.py    # 🖕🖕 Previous
```

---

## Dépendances

```bash
pip install opencv-python mediapipe
```
