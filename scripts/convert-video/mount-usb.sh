#!/usr/bin/env bash
set -euo pipefail

MOUNT_POINT="${MOUNT_POINT:-/mnt/usb}"
DEVICE="${1:-}"

die() {
  printf 'mount-usb: %s\n' "$*" >&2
  exit 1
}

find_usb_device() {
  local line first_usb_disk
  declare -A usb_disks=()

  while IFS= read -r line; do
    local NAME= TYPE= TRAN= PKNAME=
    eval "$line"

    if [[ "$TYPE" == "disk" && "$TRAN" == "usb" ]]; then
      usb_disks["$NAME"]=1
      first_usb_disk="${first_usb_disk:-$NAME}"
    elif [[ "$TYPE" == "part" && ( "$TRAN" == "usb" || ( -n "$PKNAME" && -n "${usb_disks[$PKNAME]:-}" ) ) ]]; then
      printf '%s\n' "$NAME"
      return 0
    fi
  done < <(lsblk -rpno NAME,TYPE,TRAN,PKNAME -P)

  [[ -n "${first_usb_disk:-}" ]] && printf '%s\n' "$first_usb_disk"
}

[[ -n "$DEVICE" ]] || DEVICE="$(find_usb_device)"
[[ -n "$DEVICE" ]] || die "no USB disk or partition found"
[[ -b "$DEVICE" ]] || die "$DEVICE is not a block device"

FS_TYPE="$(sudo blkid -o value -s TYPE "$DEVICE" 2>/dev/null || true)"
[[ -n "$FS_TYPE" ]] || die "could not detect filesystem type for $DEVICE"

uid="$(id -u)"
gid="$(id -g)"
opts=""
mount_type="$FS_TYPE"

case "${FS_TYPE,,}" in
  vfat|fat|msdos)
    mount_type="vfat"
    opts="iocharset=utf8,codepage=936,uid=$uid,gid=$gid"
    ;;
  exfat)
    opts="iocharset=utf8,uid=$uid,gid=$gid"
    ;;
  ntfs)
    if grep -qw ntfs3 /proc/filesystems 2>/dev/null; then
      mount_type="ntfs3"
      opts="iocharset=utf8,uid=$uid,gid=$gid"
    else
      mount_type="ntfs-3g"
      opts="locale=${LC_ALL:-${LANG:-C.UTF-8}},uid=$uid,gid=$gid"
    fi
    ;;
esac

sudo mkdir -p "$MOUNT_POINT"

if [[ -n "$opts" ]]; then
  sudo mount -t "$mount_type" -o "$opts" "$DEVICE" "$MOUNT_POINT"
else
  sudo mount -t "$mount_type" "$DEVICE" "$MOUNT_POINT"
fi

printf 'Mounted %s (%s) at %s\n' "$DEVICE" "$FS_TYPE" "$MOUNT_POINT"
