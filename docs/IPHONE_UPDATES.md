# iPhone — easiest Shattered Realms updates

The game is built automatically from GitHub `main` after each relevant source push. Only **successful, verified** builds appear in Releases.

## Permanent links

- **Direct current game file:** https://github.com/travisejones28-alt/pokemon-enhanced/releases/latest/download/ShatteredRealms.gba
- **Latest release with version and notes:** https://github.com/travisejones28-alt/pokemon-enhanced/releases/latest
- **Previous versions / rollback:** https://github.com/travisejones28-alt/pokemon-enhanced/releases

The file is always named **ShatteredRealms.gba**. This is a *direct game download*, not the ZIP normally shown under GitHub Actions.

## First-time installation

1. In Safari on iPhone, open the **direct current game file** link above.
2. Tap Download, then open the iPhone **Files** app → Downloads.
3. Open **Delta**, tap **+ → Files**, and import `ShatteredRealms.gba`.
4. Run the game, make a normal in-game save and test saving/loading.

### Put a one-tap link on your Home Screen

In Safari, open the **Latest release with version and notes** link, then tap Share → **Add to Home Screen**. Name it **Shattered Realms**. When an update is ready, tap the icon and download the `.gba` asset.

Optional: In **Apple Shortcuts**, make a shortcut using `URL` (direct current game file link) → `Get Contents of URL` → `Save File` (choose your iCloud Drive / Downloads folder). Add the shortcut to Home Screen. Shortcuts can download the file, but **cannot reliably update Delta's game library or move old saves automatically**; import the new ROM in Delta after downloading.

## Safe updates — important

**A new ROM can have a new SHA-1 hash, which may appear as a separate game inside Delta. Do not assume the previous save will transfer automatically.**

1. Before updating, use the existing game's **in-game Save** option.
2. In Delta, **long-press the old game → Manage Save File → Export Save File**. Save the `.sav` backup to Files / iCloud Drive.
3. Download the newest `ShatteredRealms.gba` and import it via **Delta → + → Files**.
4. If Delta shows another Shattered Realms tile, long-press the **new** tile → **Manage Save File → Import Save File**; select the backup.
5. Start the new game, verify that **Continue** loads correctly, then save, close/relaunch and verify again. Retain the older game and backup until these tests pass.
6. If it doesn't work, continue playing the older build. We need to implement a specific save migration before upgrading that save.

**Do not rely on emulator save states alone.** Battery / in-game saves (`.sav`) are the safer transfer format. Major engine, map or species changes may break compatibility even if the save imports successfully.

## GitHub development workflow

- Source commit to `main` → run unit tests → compile GBA → validate 32 MB ROM → store artifact → publish new GitHub Release.
- The link under **Permanent links** always points to the most recently *published successful* release.
- A failing or canceled build does not replace the working latest release.
- Each successful run receives its own release version tag for rollback.
- Previous GitHub Actions artifacts are only retained temporarily; Releases provide longer-term versioned downloads.

**No automatic iOS app/Delta installation:** iPhone and Delta do not expose a Windows-style folder junction or an official GitHub-to-Delta auto-update path. Saving/importing the game and managing save data still requires interaction.
