import base64
import os
import pyperclip
from pathlib import Path
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

print("file scanned started")

class AudioTranscriber:
    def __init__(self, api_key=None):
        """
        Initialize the AudioTranscriber with Gemini API
        
        Args:
            api_key (str): Your Gemini API key. If None, will look for GEMINI_API_KEY environment variable
        """
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        print(f"API Key: {self.api_key}")
        if not self.api_key:
            raise ValueError("API key is required. Set GEMINI_API_KEY environment variable or pass api_key parameter")
        
        self.client = genai.Client(api_key=self.api_key)
        # self.model = "gemini-2.5-pro"
        self.model = "gemini-2.5-flash"
        self.transcribed_texts = []  # Array to store transcribed texts
    
    def encode_audio_to_base64(self, audio_path):
        """
        Encode audio file to base64
        
        Args:
            audio_path (str): Path to the audio file
            
        Returns:
            str: Base64 encoded audio data
        """
        try:
            with open(audio_path, 'rb') as audio_file:
                audio_data = audio_file.read()
                return base64.b64encode(audio_data).decode('utf-8')
        except FileNotFoundError:
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        except Exception as e:
            raise Exception(f"Error reading audio file: {str(e)}")
    
    def get_audio_mime_type(self, audio_path):
        """
        Determine MIME type based on file extension
        
        Args:
            audio_path (str): Path to the audio file
            
        Returns:
            str: MIME type of the audio file
        """
        extension = Path(audio_path).suffix.lower()
        mime_types = {
            '.mp3': 'audio/mpeg',
            '.wav': 'audio/wav',
            '.m4a': 'audio/mp4',
            '.aac': 'audio/aac',
            '.ogg': 'audio/ogg',
            '.flac': 'audio/flac'
        }
        return mime_types.get(extension, 'audio/mpeg')
    
    def transcribe_audio(self, audio_path, language="auto"):
        """
        Transcribe audio file using Gemini API
        
        Args:
            audio_path (str): Path to the audio file
            language (str): Target language for transcription (default: "auto")
            
        Returns:
            str: Transcribed text
        """
        try:
            # Encode audio to base64
            audio_base64 = self.encode_audio_to_base64(audio_path)
            
            # Get MIME type
            mime_type = self.get_audio_mime_type(audio_path)
            
            # Create content for API request
            contents = [
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_bytes(
                            mime_type=mime_type,
                            data=base64.b64decode(audio_base64)
                        )
                    ]
                )
            ]

            generate_content_config = types.GenerateContentConfig(
                thinking_config = types.ThinkingConfig(
                    thinking_budget=-1,
                ),
                response_mime_type="text/plain",
                system_instruction=[
                    types.Part.from_text(text="""give me transcript of this audio in Telugu language.
Give JUST the transcript now."""),
                ],
            )
            
            # Generate response
            response = self.client.models.generate_content(
                model=self.model,
                contents=contents,
                config=generate_content_config,
            )
            
            transcribed_text = response.text.strip()
            
            # Add to array
            self.transcribed_texts.append(transcribed_text)
            
            return transcribed_text
            
        except Exception as e:
            error_msg = f"Error transcribing audio: {str(e)}"
            print(error_msg)
            raise error_msg
        
    def delete_file(self, file_path):
        """
        Delete a file from the filesystem
        
        Args:
            file_path (str): Path to the file to delete
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"✓ File deleted successfully: {file_path}")
            else:
                print(f"File not found: {file_path}")
        except Exception as e:
            print(f"Error deleting file: {str(e)}")
    
    def process_audio_directory(self, directory_path, audio_index=0):
        """
        Process audio files from a directory and transcribe the specified index
        
        Args:
            directory_path (str): Path to directory containing audio files
            audio_index (int): Index of audio file to process (default: 0 for first file)
            
        Returns:
            str: Transcribed text
        """
        try:
            
            directory = Path(directory_path)
            if not directory.exists():
                raise FileNotFoundError(f"Directory not found: {directory_path}")
            
            
            # Get all audio files from directory
            audio_files = [i for i in directory.glob("*.mp3")]
            
            if not audio_files:
                raise FileNotFoundError(f"No audio files found in directory: {directory_path}")

            
            if audio_index >= len(audio_files):
                raise IndexError(f"Audio index {audio_index} out of range. Found {len(audio_files)} audio files.")
            
            # sort audio files by name
            audio_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            # Get the specified audio file
            target_audio = audio_files[audio_index]
            print(f"Processing audio file: {target_audio.name}")
            
            # Transcribe the audio
            transcribed_text = self.transcribe_audio(str(target_audio))

            # Delete file after successful processing
            if target_audio.exists():
                self.delete_file(target_audio)
            
            return transcribed_text
            
        except Exception as e:
            error_msg = f"Error processing directory v1: {str(e)}"
            print(error_msg)
            raise error_msg
    
    def copy_to_clipboard(self, text):
        """
        Copy text to system clipboard
        
        Args:
            text (str): Text to copy to clipboard
        """
        try:
            pyperclip.copy(text)
            print("✓ Text copied to clipboard successfully!")
        except Exception as e:
            print(f"Error copying to clipboard: {str(e)}")
    
    def get_transcribed_texts(self):
        """
        Get all transcribed texts
        
        Returns:
            list: Array of all transcribed texts
        """
        return self.transcribed_texts
    
    def clear_transcribed_texts(self):
        """Clear the transcribed texts array"""
        self.transcribed_texts.clear()

# Main function to use the transcriber
def analyse_audio_transcript_copy():
    """
    Example usage of the AudioTranscriber
    """
    # Initialize transcriber (make sure to set your API key)
    transcriber = AudioTranscriber()
    
    # Example usage 1: Process specific audio file
    # audio_path = "/path/to/your/audio/file.mp3"
    # result = transcriber.transcribe_audio(audio_path)
    
    # Example usage 2: Process audio[0] from directory
    # directory_path = input("Enter the path to your audio directory:").strip()
    directory_path = r"C:\Users\M sai\Downloads"
    
    try:
        # Process the first audio file (index 0) from the directory
        result = transcriber.process_audio_directory(directory_path, audio_index=0)
        
        print("\n" + "="*50)
        print("TRANSCRIPTION RESULT:")
        print("="*50)
        print(result)
        print("="*50)
        
        # Copy to clipboard
        transcriber.copy_to_clipboard(result)
        
        # Show all transcribed texts
        print(f"\nTotal transcribed texts in array: {len(transcriber.get_transcribed_texts())}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        raise e


# Main function to use the transcriber
def main():
    """
    Example usage of the AudioTranscriber
    """
    # Initialize transcriber (make sure to set your API key)
    transcriber = AudioTranscriber()
    
    # Example usage 1: Process specific audio file
    # audio_path = "/path/to/your/audio/file.mp3"
    # result = transcriber.transcribe_audio(audio_path)
    
    # Example usage 2: Process audio[0] from directory
    # directory_path = input("Enter the path to your audio directory:").strip()
    directory_path = r"C:\Users\M sai\Downloads"
    
    try:
        # Process the first audio file (index 0) from the directory
        result = transcriber.process_audio_directory(directory_path, audio_index=0)
        
        print("\n" + "="*50)
        print("TRANSCRIPTION RESULT:")
        print("="*50)
        print(result)
        print("="*50)
        
        # Copy to clipboard
        transcriber.copy_to_clipboard(result)
        
        # Show all transcribed texts
        print(f"\nTotal transcribed texts in array: {len(transcriber.get_transcribed_texts())}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        raise e

# main()
if __name__ == "__main__":
    print("inside if")
    main()

print("outside if", __name__)

print("file scanned successfully")