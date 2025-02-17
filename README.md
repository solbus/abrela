# Abrela
An unofficial & fan-made choose-your-own-adventure MP3 editor & mixer designed to work with the King Gizzard & The Lizard Wizard bootlegger albums.

Current version: **`1.0`** (initial release)

## Project Dependencies
- [**PyQt6**](https://www.riverbankcomputing.com/static/Docs/PyQt6/) (6.8.0) - *UI*
- [**Pydub**](https://github.com/jiaaro/pydub) (0.25.1) and [**FFmpeg**](https://ffmpeg.org/download.html) (`ffmpeg.exe` and `ffprobe.exe` from [gyan.dev](https://www.gyan.dev) `ffmpeg-2025-02-13-git-19a2d26177-essentials_build.7z`) - *MP3 processing*
- [**PyInstaller**](https://pyinstaller.org/en/stable/) (6.12.0) - *Packaging release builds*

## Disclaimer
This project was created with the extensive use of OpenAI's GPT and Reasoning models available on ChatGPT. Now that the bulk of the initial code is complete, I plan to begin estimating the negative environmental impact of the use of AI to create this project, and to work/make contributions to offset it.

 Though I have tested the code rigorously and acted as a kind of project manager putting it all together, currently it has not been reviewed by a human expert in Python programming, as I myself am not a programming expert. Abrela makes no connections to the internet and no user information is stored, except for optional settings related to remembering local filepaths to make reusing it easier, and these settings are stored locally.

## How it Works
Abrela works with transition logic: **default transitions** are just the transitions to the next track on any given album, and **custom transitions** are manually-defined parameters that allow transitions from any track to any other track (so long as a custom transition is defined). Currently, custom transitions only include slicing, linear fades, and overlays. Abrela is configured to chain transitions automatically, so each transition is handled "in a vacuum" and the final product is built as a series of these transitions. As more custom transitions are added, this will enable an exponentially large number of potential combinations of transitions selectable by users.

## Current List of Custom Transitions
[See list here](link)

## Setup & Usage Guide
1. Download KGLW bootlegger albums from the [bootleg gizzard Bandcamp page](https://bootleggizzard.bandcamp.com/) - MP3 format (MP3 320 recommended, though V0 should work in theory - untested)
2. Extract each album's ZIP - this will give you one folder for each album
3. Move all of the album folders to one shared folder (optional, but recommended)
4. In the Abrela setup process, indicate whether you have all of the bootlegger albums downloaded, or just some of them (more downloaded = more custom transitions available), and whether you have all of the album folders stored in one shared folder, or in separate folders
5. If you only have some of them downloaded, tell Abrela which ones you have in the setup process (skip if you have all of them downloaded)
6. If you have the album folders stored in one shared folder, indicate that folder's location in Abrela (otherwise, indiciate an individual folder location per album)
7. Select the album that has the track you want to start with
8. Select the track you want to start with
9. Select a series of transitions
10. Click the "Done" button
11. Select a save location

## A friendly reminder
The spirit of the KGLW bootleggers is in **physical media**, so Abrela is intended for personal use only, or for those experimenting with intentions to create physical media.

Relevant info from [https://kinggizzardandthelizardwizard.com/bootlegger](https://kinggizzardandthelizardwizard.com/bootlegger):<br>**Q:** "Can I upload to Spotify or other DSPs like Apple Music?"<br>**A:** "No thanks! Let's keep this [stuff] underground baby."<br>**Also:** "The licence only extends to physical copies of the music."

## Want to contribute?
- **Transition Makers:** Only basic audio editing experience needed to contribute! Video of the basic flow I've been doing in Audacity coming soon.
- **Programmers:** Because I have no idea what I'm doing!
- **Graphic Artists:** Some visual assets for this could be nice!

I am not currently able to hire help, but anyone volunteering to contribute will be credited. I can be reached on Discord (King Gizzcord server, **@Solbus**), Reddit (**u/automation_kglw**), and via email (**kglwautomation@gmail.com**)

## GPL v3 Notice
    This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.