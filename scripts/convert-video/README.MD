# Convert Videos

Run these scripts from the `scripts/convert-video` directory.

The video converter now runs as a Python script. The old Bash converter is kept
under `legacy/` for reference, while the active workflow uses these directories:

- `input/`: source video folders to convert
- `output/`: converted MP4 files, grouped by source folder
- `archived/`: source folders moved here after every video in the folder
  converts or is already present in `output/`

## Prepare videos

Create `input/` if needed, then copy each source video folder into it. The
converter scans immediate subdirectories of `input/`, preserves nested paths
inside `output/<source-folder>/`, and moves fully successful source folders to
`archived/<source-folder>/`.

```bash
mkdir -p input output archived
```

## Convert videos

```bash
tmux
python3 convert-video.py
```

Converted files are written to `output/<source-folder>/` as MP4 files. Progress,
failures, and skipped files are logged to `convert-video-YYYYMMDD-HHMMSS.log`,
and a completion email is sent when the run finishes. The converter exits with a
non-zero status if any video fails or times out.

Optional environment variables:

```bash
MAX_JOBS=8 CONVERT_TIMEOUT=30m SUBTITLE_FONT="Noto Sans CJK SC" python3 convert-video.py
```

`CONVERT_VIDEO_BASE_DIR` can point the converter at another directory with the
same `input/`, `output/`, and `archived/` structure.

## Mount the USB drive

```bash
./mount-usb.sh
```

The script auto-detects a USB disk or partition and mounts it at `/mnt/usb`.
Pass a device path if auto-detection is not the one you want:

```bash
./mount-usb.sh /dev/sdb1
```

## Move videos to USB

Clean up old videos on the USB first if needed, then run the transfer from a
tmux session:

```bash
tmux
./move-video-to-usb.sh
```

The transfer copies everything from `output/` to `/mnt/usb/`, removes copied
source files from `output/`, prunes empty output directories, and sends a
completion email.

## Unmount the USB drive

Unmount the USB drive before unplugging it:

```bash
sudo umount /mnt/usb
```

if busy

```
sudo umount -l /mnt/usb
```
