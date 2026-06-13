# Convert Videos

Run these scripts from the `scripts/convert-video` directory.

## Prepare videos

Copy each source video folder into this directory. The converter scans immediate
subdirectories, writes converted files under `output/`, and renames fully
successful source folders to `<folder>-done`.

## Convert videos

```bash
./convert-video.sh
```

Converted files are written to `output/<source-folder>/` as MP4 files. Progress
and failures are logged to `convert-video-errors.log`, and a completion email is
sent when the run finishes.

Optional environment variables:

```bash
MAX_JOBS=8 SUBTITLE_FONT="Noto Sans CJK SC" ./convert-video.sh
```

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
