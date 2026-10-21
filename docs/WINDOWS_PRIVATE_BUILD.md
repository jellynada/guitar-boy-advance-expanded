# Mission014 note

The existing launcher is preserved and now names the private output **Guitar-Boy-Advance-M014-Cream-Private.gba**. The cloud exercises its underlying clean build chain; Windows11 double-click execution is untested here. A user who only wants to play should receive the already-built ROM privately, without needing these developer installation steps. That private transfer is currently unavailable; the owner requested local retention. Public synthetic review ZIPs do not contain Cream.

# Build your Cream ROM on Windows 11

Keep the song ZIP on your computer. The launcher never downloads music or uploads
its result. Both profiles use the same engine revision.

## One-time installation

1. Install [mGBA](https://mgba.io/downloads.html) for Windows.
2. Open Windows Terminal **as administrator**, enter `wsl --install -d Ubuntu`,
   restart if requested, then open Ubuntu and finish creating its user account.
3. Install [Docker Desktop](https://www.docker.com/products/docker-desktop/).
   Use Linux containers. Under Settings → Resources → WSL Integration, enable
   **Ubuntu**, Apply, and keep Docker Desktop running.
4. In Ubuntu, enter `sudo apt update`, then
   `sudo apt install -y python3 ffmpeg git`. This is one-time setup.
5. Extract the **complete** Mission013 review ZIP with Windows **Extract All**.
   Keep the `guitar-boy-advance-expanded` source folder together. A short local
   path such as `C:\gba\mission013` is recommended; spaces are supported.

## Every time you want a current private ROM

1. Obtain the current reviewed source ZIP, or update a Git checkout. Do not mix
   source files from different ZIPs. Keep your existing song ZIP separately.
2. Inside the source folder, create a folder named `private`. Put your existing
   song ZIP inside and name it **Cream.zip**. In Explorer enable View → Show →
   File name extensions; it must not be named Cream.zip.zip. Do not unpack it.
3. Double-click **Build-Cream-ROM.bat**. The first build downloads the pinned GBA
   compiler image. Wait for **BUILD SUCCESS: M013 / CREAM / LOCAL**.
4. The window prints the exact ROM location, complete source commit and SHA-256
   checksum. Find it under `builds\private\<source-version-and-time>\` with name
   **Guitar-Boy-Advance-M013-Cream-Private.gba**. The adjacent manifest identifies
   the source, song hashes, toolchain and ROM. `LATEST.txt` selects only a
   successful current attempt.
5. In mGBA: File → Load ROM → select that newly printed file. Confirm the selector
   says **M013 / CREAM / LOCAL**, then choose Imported Easy Test. Alternatively,
   copy that `.gba` file to your compatible flash cartridge using its normal
   instructions. Never copy the ELF, source or ZIP to the cartridge as the game.

Easy now uses GBA **Left / B / A** from left to right. Original Demo keeps
Left / Right / A / B. A/Start replays results; B/Select returns; Start+Select exits play.

## If it stops

A red **BUILD STOPPED** means no new successful ROM was delivered. Do not open an
old file and assume it contains the latest engine. Previous dated builds remain,
but the latest-success pointer is removed when a new attempt starts.

- Missing ZIP: check `private\Cream.zip` and visible filename extensions.
- WSL cannot start: launch Ubuntu once and complete its account setup.
- Missing Python/FFmpeg/Git: repeat the Ubuntu install command above.
- Docker unavailable: start Docker Desktop; enable Ubuntu WSL integration and
  Linux containers. Restart Ubuntu after changing integration settings.
- Wrong ZIP entries/stems/chart: use your complete original owner package. The
  build requires exactly one guitar, rhythm and song role,395 Easy heads and78
  genuine sustains. It stops instead of substituting synthetic music.
- Source incomplete/changed: extract a fresh complete review ZIP. A Git checkout
  with edited tracked files must be reviewed and committed first.
- Compilation error: the window shows the end of the log. Full details are in
  `builds\private\LAST_ATTEMPT.json` and the `.failed-*\build.log` it names.
- Clock/freshness error: correct Windows date/time and try again.

The Linux preparation and pinned Docker build are tested in this cloud workspace.
Actual Windows double-click execution cannot be tested on this Linux machine;
report the exact visible error if Windows behaves differently. Different FFmpeg
versions may change audio bytes; manifests record the version and hashes rather
than promising identical bytes across every installation.
