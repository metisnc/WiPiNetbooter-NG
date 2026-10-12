# WiPi Launcher — interface tactile pour l'écran 3,5"

Interface de **sélection et de lancement des jeux** pour WiPi Netbooter 6.1-92, pensée pour l'écran tactile MHS 3,5" (480×320) branché sur le Raspberry Pi. Elle fonctionne aussi sur téléphone et PC.

Le launcher vit entièrement dans `/var/www/html/launcher/` et **ne modifie aucun fichier de l'interface WiPi existante**. Les réglages WiPi (options, netdimms, OpenJVS, cartes, réseau…) restent dans l'interface d'origine, accessible depuis **⚙ Réglages → Interface WiPi**.

## Fonctionnalités

- Grille de logos paginée, au choix **3×3, 2×3, 2×2 ou 1×2** sur le 3,5" (plus de tuiles sur un grand écran).
- **Veille de l'écran** (3,5" uniquement) : écran noir après 2 min sans toucher l'écran ou après un lancement (réglable : jamais, 1, 2, 5 min). Le rétroéclairage du MHS 3,5" (ILI9486) n'est pas pilotable : on affiche du noir. Le premier tap réveille sans rien déclencher.
- Écran **⚙ Réglages** : affichage de la grille, vidéo dans la fiche, état des netdimms (en ligne ou non), nombre de jeux et mode simulation/réel, bouton **Interface WiPi** vers l'interface d'origine.
- Onglets **★ Favoris**, **TOUS**, un onglet par système présent (Naomi, Naomi 2, Atomiswave, Chihiro, Triforce) et **↺ Récents**.
- Saut **A–Z** plein écran, filtres **Genre / Orientation / Contrôles** à choix multiple (OU dans un groupe, ET entre les groupes).
- Fiche jeu : vidéo (optionnelle), infos, favori ☆/★, gros bouton **LANCER**. Toujours 2 taps pour lancer : tuile puis LANCER.
- Écran de lancement : recherche du netdimm, choix de la borne s'il y en a plusieurs, progression en %, succès, erreur avec la fin du log, **Réessayer** et **Annuler**.
- Pages tournées avec les flèches ◀ ▶ ou en glissant le doigt sur la grille, y compris sur les logos (la grille suit le doigt, revient en place si le geste est trop court). Les listes Filtres et Réglages défilent aussi au glissement.
- Les choix d'affichage (onglet, filtres, page, densité, vidéo) sont mémorisés dans le navigateur.

Ce qui est repris de WiPi : la liste des jeux (`csv/romsinfo.csv`, jeux activés dont la ROM est dans `/boot/roms`), l'option **System Filter**, les favoris (via `updatecsvfave.php`), « Last Game Played », l'option **Video Sound**, les images et vidéos (`/images`, `/videos`) et la commande de lancement de `load.php`.

## URLs

| URL | Usage |
|---|---|
| `http://<pi>/launcher/` | téléphone / PC |
| `http://<pi>/launcher/?kiosk=1` | écran 3,5" (compense le `--force-device-scale-factor=0.651` du kiosque) |
| `http://<pi>/launcher/?frame=480x320` | aperçu du 3,5" sur un PC |
| `…&sim=error` / `slow` / `multi` / `nodimm` | scénarios de test, en mode simulation uniquement |

## Mode simulation

`config.php` contient `'simulate' => true` : **aucun jeu n'est envoyé**, la progression est simulée et un bandeau SIMULATION est affiché. Pour les vrais lancements, passer la valeur à `false` puis redéployer.

## Installation sur le Pi

Depuis le Mac (clé SSH installée pour `root`) :

```bash
tools/deploy.sh                     # copie launcher/ sur le Pi (WIPI_HOST=root@<ip> pour changer de cible)
```

Puis sur le Pi, en root :

```bash
bash /var/www/html/launcher/install.sh --restart     # le kiosque 3,5" ouvre le launcher
bash /var/www/html/launcher/screen-rotate.sh 90 --reboot   # optionnel : écran en paysage
```

- `install.sh` modifie la ligne Chromium de `/etc/xdg/openbox/autostart` : il remplace l'URL et charge l'extension `kiosk/home-button`, qui ajoute un bouton **⌂** sur les pages WiPi existantes pour revenir au launcher. L'original est gardé en `autostart.wipi-orig`. Le script est idempotent.
- `screen-rotate.sh 0|90|180|270` règle `dtoverlay=tft35a:rotate=` dans `/boot/config.txt` **et** `/boot/config.txt.lcd35` (l'option WiPi « LCD Mode » recopie le second sur le premier), ainsi que la calibration tactile `/etc/X11/xorg.conf.d/99-calibration.conf`. Les originaux sont gardés en `*.wipi-orig`. Si l'image est à l'envers, utiliser l'autre angle (90 ↔ 270).

## Après une mise à jour WiPi

Le paquet `wipi` ne supprime pas `launcher/` et ne touche ni à `autostart` ni à `/boot/config.txt`. Par précaution, relancer :

```bash
bash /var/www/html/launcher/install.sh --restart
```

Il affiche un **avertissement si `load.php` a changé** : dans ce cas, vérifier que `api/launch_lib.php` lance toujours la même commande avant de faire de vrais lancements. Si `launcher/` a disparu, relancer `tools/deploy.sh` depuis le Mac, puis `install.sh`.

## Revenir en arrière

```bash
bash /var/www/html/launcher/uninstall.sh --restart     # le kiosque rouvre l'interface WiPi d'origine
bash /var/www/html/launcher/screen-rotate.sh 0 --reboot   # écran en portrait (réglage WiPi d'origine)
```

Le launcher reste accessible par son URL tant que le dossier existe.

## Architecture

```
launcher/
  index.php             page unique
  config.php            simulate, taille de l'historique
  assets/launcher.css   thème sombre, mise en page 480x320 d'abord
  assets/launcher.js    navigation : onglets, grille, A–Z, filtres, fiche, favoris, vidéo
  assets/launch.js      écran de lancement
  api/lib.php           lecture romsinfo.csv / dimms.csv / fichiers de mode
  api/games.php         GET  liste des jeux, historique, simulate, sound
  api/dimms.php         GET  netdimms de dimms.csv + ping (écran Réglages)
  api/launch.php        POST {rom, dimm?, sim?} -> started | choose | nodimm | busy | error
  api/status.php        GET  idle | connecting | running | done | error | cancelled
  api/cancel.php        POST arrête wipiloader.py / netdimm_send
  api/launch_lib.php    état du lancement, commande wipiloader, simulation
  data/                 history.json, launch.json (écrits par www-data, hors git)
  kiosk/home-button/    extension Chromium (bouton ⌂)
  install.sh, uninstall.sh, screen-rotate.sh
tools/deploy.sh         (à la racine du dépôt) déploiement tar via ssh — le Pi n'a pas rsync
```

**Lancement** (identique à l'interface d'origine) :
1. `launch.php` vérifie que la ROM est dans la liste des jeux, puis ping (`fping`) les netdimms de `dimms.csv` compatibles avec le système (mêmes règles que `loadcheck.php`).
2. Avec un seul netdimm en ligne, il exécute `sudo python3 /sbin/piforce/wipiloader.py <rom> <ip> <relaymode> <zeromode> <mapping> <ffb>`, comme `load.php`. Chaque argument est validé puis passé par `escapeshellarg`.
3. `status.php` lit `/var/log/progress_<ip>`, écrit par `dm_netboot` (lignes `0`…`100` puis `COMPLETE`). Un fichier antérieur au lancement est ignoré. Si le processus s'est arrêté sans `COMPLETE`, c'est une erreur, et la fin de `/var/log/netdimm_send.log` est affichée.
4. **Annuler** tue `wipiloader.py` et `netdimm_send`. Le netdimm reste alors sur « Now Loading » jusqu'au prochain envoi.
5. DietPi garde `/var/log` en RAM et le **vide toutes les heures à hh:17**. L'état final d'un lancement (jeu lancé, ou erreur avec son log) est donc mémorisé dans `data/launch.json` dès qu'il est connu.

Contraintes respectées : PHP 7.3 (pas de fonctions fléchées), Chromium 88, aucun framework ni CDN, aucune accélération matérielle sur le Pi 3 (effets légers, pas de flou, fonds opaques).
