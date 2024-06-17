import os
import json
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
from mutagen.flac import FLAC
from mutagen.oggvorbis import OggVorbis
from unidecode import unidecode

actions_log = []

def load_actions_log(log_file):
    if os.path.exists(log_file):
        with open(log_file, 'r') as f:
            return json.load(f)
    return []

def save_actions_log(log_file, actions):
    with open(log_file, 'w') as f:
        json.dump(actions, f, indent=4)

def remove_accents_from_metadata(file_path):
    try:
        if file_path.lower().endswith('.mp3'):
            audio = MP3(file_path, ID3=EasyID3)
        elif file_path.lower().endswith('.flac'):
            audio = FLAC(file_path)
        elif file_path.lower().endswith('.ogg'):
            audio = OggVorbis(file_path)
        else:
            print(f"Unsupported file format: {file_path}")
            return
        
        modified = False
        changes = {}
        
        for tag in audio.keys():
            original_value = audio[tag][0]
            new_value = unidecode(original_value)
            if original_value != new_value:
                audio[tag] = [new_value]
                modified = True
                changes[tag] = original_value
                print(f"Updated {tag}: '{original_value}' -> '{new_value}'")

        if modified:
            audio.save()
            actions_log.append({'action': 'update_metadata', 'file': file_path, 'changes': changes})
            print(f"Metadata updated for file: {file_path}")
        else:
            print(f"No accents found in metadata for file: {file_path}")

        # Renaming the file based on a combination of artist and title tags
        artist = audio.get('artist', ['Unknown Artist'])[0]
        title = audio.get('title', ['Unknown Title'])[0]

        extension = os.path.splitext(file_path)[1]
        new_file_name = f"{unidecode(artist)} - {unidecode(title)}{extension}"
        new_file_path = os.path.join(os.path.dirname(file_path), new_file_name)
        
        if new_file_path != file_path:
            os.rename(file_path, new_file_path)
            actions_log.append({'action': 'rename_file', 'old_path': file_path, 'new_path': new_file_path})
            print(f"Renamed file to: {new_file_path}")
        else:
            print(f"File already has the correct name: {file_path}")

    except Exception as e:
        print(f"Error processing file {file_path}: {e}")

def process_music_directory(directory_path):
    album_directories = set()
    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.lower().endswith(('.mp3', '.flac', '.ogg')):
                file_path = os.path.join(root, file)
                remove_accents_from_metadata(file_path)
                album_directories.add(root)
    
    for album_dir in album_directories:
        rename_album_directory(album_dir)

def rename_album_directory(album_dir):
    try:
        album_name = None
        for file in os.listdir(album_dir):
            file_path = os.path.join(album_dir, file)
            if file.lower().endswith('.mp3'):
                audio = MP3(file_path, ID3=EasyID3)
            elif file.lower().endswith('.flac'):
                audio = FLAC(file_path)
            elif file.lower().endswith('.ogg'):
                audio = OggVorbis(file_path)
            else:
                continue

            album_name = audio.get('album', [None])[0]
            if album_name:
                album_name = unidecode(album_name)
                break
        
        if album_name:
            new_album_dir = os.path.join(os.path.dirname(album_dir), album_name)
            if new_album_dir != album_dir:
                os.rename(album_dir, new_album_dir)
                actions_log.append({'action': 'rename_directory', 'old_path': album_dir, 'new_path': new_album_dir})
                print(f"Renamed folder to: {new_album_dir}")
            else:
                print(f"Folder already has the correct name: {album_dir}")
        else:
            print(f"No album name found for folder: {album_dir}")
    
    except Exception as e:
        print(f"Error renaming folder {album_dir}: {e}")

def undo_changes(log_file):
    actions = load_actions_log(log_file)
    for action in reversed(actions):
        try:
            if action['action'] == 'update_metadata':
                file_path = action['file']
                if file_path.lower().endswith('.mp3'):
                    audio = MP3(file_path, ID3=EasyID3)
                elif file_path.lower().endswith('.flac'):
                    audio = FLAC(file_path)
                elif file_path.lower().endswith('.ogg'):
                    audio = OggVorbis(file_path)
                else:
                    print(f"Unsupported file format: {file_path}")
                    continue

                for tag, original_value in action['changes'].items():
                    audio[tag] = [original_value]
                audio.save()
                print(f"Reverted metadata changes for file: {file_path}")
            
            elif action['action'] == 'rename_file':
                os.rename(action['new_path'], action['old_path'])
                print(f"Reverted file rename: {action['new_path']} -> {action['old_path']}")

            elif action['action'] == 'rename_directory':
                os.rename(action['new_path'], action['old_path'])
                print(f"Reverted directory rename: {action['new_path']} -> {action['old_path']}")

        except Exception as e:
            print(f"Error undoing action {action}: {e}")

if __name__ == "__main__":
    log_file = 'actions_log.json'
    actions_log = load_actions_log(log_file)

    while True:
        choice = input("Enter 'process' to process directory, 'undo' to undo changes, or 'exit' to quit: ").strip().lower()
        if choice == 'process':
            directory = input("Enter the directory path containing your music files: ")
            process_music_directory(directory)
            save_actions_log(log_file, actions_log)
        elif choice == 'undo':
            undo_changes(log_file)
            actions_log = []
            save_actions_log(log_file, actions_log)
        elif choice == 'exit':
            break
        else:
            print("Invalid choice. Please enter 'process', 'undo', or 'exit'.")
