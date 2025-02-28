In the packaged version of Abrela, `ffmpeg.exe` and `ffprobe.exe` from [gyan.dev](https://www.gyan.dev/ffmpeg/) are included from within this `vendor/` subdirectory. They are not included in the repo on GitHub to reduce repo bloat.

If you clone this repo and want to add `ffmpeg.exe` and `ffprobe.exe` locally, you can download them from gyan.dev (the current pacakged versions are from `ffmpeg-2025-02-13-git-19a2d26177-essentials_build.7z`, but any version of `ffmpeg.exe` and `ffprobe.exe` from gyan.dev's git master branch builds should work just fine), and simply place the two EXEs in the `vendor/` subdirectory.

You'll just download the `.7z` file and extract those two EXEs from it, and place them in `vendor/`.