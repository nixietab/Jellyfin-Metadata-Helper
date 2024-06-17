# Jellyfin-Metadata-Helper

This script is a Python tool designed to help organize and standardize music file metadata, particularly for formats like MP3, FLAC, and OGG. It allows users to remove accents from metadata tags (such as artist, title, and album), rename files based on cleaned metadata, and even rename directories to match album names found in the music files.

### Features

*    Metadata Cleanup: Automatically removes accents from metadata like artist, title, and album.
*    File Renaming: Updates filenames based on cleaned metadata (artist - title.ext).
*    Directory Renaming: Renames directories to match album names found in music files.
*    Logging and Undo: Logs all actions (metadata updates, renames) to a JSON file (actions_log.json) for potential undo operations.

