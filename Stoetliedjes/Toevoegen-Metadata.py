import os
import subprocess
from mutagen.easyid3 import EasyID3
from mutagen.flac import FLAC
from mutagen.wave import WAVE
from mutagen.mp4 import MP4
from mutagen.id3 import ID3NoHeaderError

# Een lijst van ondersteunde bestandsextensies
SUPPORTED_EXTENSIONS = ['.mp3', '.flac', '.m4a', '.wav']

def get_metadata_reader(file_path):
    """Bepaalt en laadt de juiste metadata lezer voor het bestandstype."""
    _, ext = os.path.splitext(file_path)
    if ext == '.mp3':
        try:
            return EasyID3(file_path)
        except ID3NoHeaderError:
            audio = EasyID3()
            audio.save(file_path)
            return EasyID3(file_path)
    elif ext == '.flac':
        return FLAC(file_path)
    elif ext == '.m4a':
        return MP4(file_path)
    elif ext == '.wav':
        # WAV ondersteunt standaard geen uitgebreide tags, dit is een placeholder
        print(f"Info: WAV-bestanden ({os.path.basename(file_path)}) hebben beperkte metadata-ondersteuning.")
        return None
    return None

def update_metadata(file_path):
    """Verwerkt een enkel muziekbestand: toont en update metadata."""
    filename = os.path.basename(file_path)
    print("="*50)
    print(f"Bestand wordt verwerkt: {filename}")
    print("="*50)

    audio = get_metadata_reader(file_path)
    if audio is None:
        print(f"Kan geen metadata lezen voor {filename}. Bestand wordt overgeslagen.\n")
        return

    # Huidige metadata tonen
    print("\nHuidige metadata:")
    title = audio.get('title', ['N/A'])[0]
    artist = audio.get('artist', ['N/A'])[0]
    album = audio.get('album', ['N/A'])[0] # Hoewel niet gevraagd, is dit vaak nuttig
    date = audio.get('date', ['N/A'])[0]
    tracknumber = audio.get('tracknumber', ['N/A'])[0]
    
    print(f"  - Titel: {title}")
    print(f"  - Artiest: {artist}")
    print(f"  - Album: {album}")
    print(f"  - Jaar: {date}")
    print(f"  - Tracknummer: {tracknumber}")
    print(f"  - Bestandsnaam: {filename}")

    # Vragen om nieuwe metadata
    print("\nGeef nieuwe metadata op (laat leeg en druk op Enter om de huidige waarde te behouden):")

    new_title = input(f"Nieuwe titel [{title}]: ") or title
    new_artist = input(f"Nieuwe artiest [{artist}]: ") or artist
    new_date = input(f"Nieuw jaar [{date}]: ") or date
    new_track = input(f"Nieuw tracknummer [{tracknumber}]: ") or tracknumber

    # Metadata bijwerken
    audio['title'] = new_title
    audio['artist'] = new_artist
    audio['date'] = new_date
    audio['tracknumber'] = new_track
    audio.save()
    
    print("\nMetadata succesvol bijgewerkt.")

    # Vragen om de bestandsnaam aan te passen
    rename_choice = input("\nWil je de bestandsnaam aanpassen op basis van de nieuwe metadata? (ja/nee): ").lower()
    if rename_choice == 'ja':
        # Creëer een nieuwe, 'schone' bestandsnaam. Je kan het formaat hier aanpassen.
        # Bijvoorbeeld: "Tracknummer - Artiest - Titel.ext"
        new_filename_str = f"{new_track} - {new_artist} - {new_title}{os.path.splitext(file_path)[1]}"
        # Verwijder ongeldige karakters voor bestandsnamen
        new_filename_str = "".join(c for c in new_filename_str if c not in r'<>:"/\|?*')
        
        new_filepath = os.path.join(os.path.dirname(file_path), new_filename_str)
        
        try:
            os.rename(file_path, new_filepath)
            print(f"Bestand hernoemd naar: {new_filename_str}")
            file_path = new_filepath # Update het pad voor het trim-script
        except OSError as e:
            print(f"Fout bij het hernoemen van het bestand: {e}")


    # Vragen om te trimmen
    trim_choice = input("\nWil je dit nummer trimmen? (ja/nee): ").lower()
    if trim_choice == 'ja':
        print(f"Het script 'trim.sh' wordt uitgevoerd voor {os.path.basename(file_path)}...")
        try:
            # Voer het trim script uit en geef het pad van het bestand als argument mee
            subprocess.run(['./trim.sh', file_path], check=True)
            print("'trim.sh' succesvol uitgevoerd.")
        except FileNotFoundError:
            print("FOUT: 'trim.sh' niet gevonden. Zorg ervoor dat het script in dezelfde map staat en uitvoerbaar is.")
        except subprocess.CalledProcessError as e:
            print(f"FOUT: Er is een fout opgetreden tijdens het uitvoeren van 'trim.sh': {e}")
            
    print("\nVerwerking van dit bestand is voltooid.\n")


def main():
    """Hoofdfunctie om het script te starten."""
    folder_path = input("Geef het volledige pad naar de map met muziekbestanden: ")

    if not os.path.isdir(folder_path):
        print(f"Fout: De map '{folder_path}' bestaat niet.")
        return

    print(f"\nStarten met het doorlopen van bestanden in: {folder_path}\n")
    
    # Sorteer de bestanden alfabetisch voor een voorspelbare volgorde
    files_in_folder = sorted(os.listdir(folder_path))

    for filename in files_in_folder:
        # Controleer of de extensie ondersteund wordt
        if any(filename.lower().endswith(ext) for ext in SUPPORTED_EXTENSIONS):
            file_path = os.path.join(folder_path, filename)
            update_metadata(file_path)
        else:
            print(f"Bestand '{filename}' wordt overgeslagen (geen ondersteunde muziek-extensie).")


if __name__ == "__main__":
    main()