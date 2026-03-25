"""Claude Code TTS Hook - reads assistant responses aloud using Edge TTS (Elvira neural voice)"""

import sys
import json
import re
import os
import tempfile
import subprocess

# Force UTF-8 on Windows
if sys.stdin.encoding != 'utf-8':
    sys.stdin.reconfigure(encoding='utf-8', errors='replace')

TOGGLE_FILE = os.path.expanduser("~/.claude/hooks/tts-enabled")

def main():
    if not os.path.exists(TOGGLE_FILE):
        return

    raw = sys.stdin.buffer.read().decode('utf-8', errors='replace')
    if not raw:
        return

    data = json.loads(raw)
    message = data.get("last_assistant_message", "")
    if not message:
        return

    text = filter_message(message)
    if len(text) < 5:
        return

    if len(text) > 1000:
        text = text[:1000] + "... y más."

    speak(text)


def filter_message(message):
    lines = message.split("\n")
    filtered = []
    in_code_block = False

    for line in lines:
        if line.strip().startswith("```"):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue

        # Skip code/technical lines
        stripped = line.strip()
        if not stripped:
            continue
        if re.match(r'^\s*[\$#>]', line):
            continue
        if re.match(r'^\s*import ', line):
            continue
        if re.match(r'^\s*\|.*\|.*\|', line):
            continue
        if re.match(r'^[a-zA-Z]:\\', line):
            continue
        if re.match(r'^/[a-z]', line):
            continue
        if re.match(r'^\s*\{', line):
            continue
        if re.match(r'^\s*\[.*\]\(.*\)', line):
            continue
        if re.match(r'^\s*[-*] `', line):
            continue
        if re.match(r'^\s*\d+\.\s*`', line):
            continue
        if re.match(r'^\s*Co-Authored', line):
            continue
        if re.match(r'^\s*---', line):
            continue
        if re.match(r'^\s*===', line):
            continue

        clean = line

        # Remove inline code
        clean = re.sub(r'`[^`]*`', '', clean)

        # Remove markdown formatting
        clean = re.sub(r'\*\*([^*]*)\*\*', r'\1', clean)
        clean = re.sub(r'\*([^*]*)\*', r'\1', clean)
        clean = re.sub(r'#{1,6}\s*', '', clean)
        clean = re.sub(r'\[([^\]]*)\]\([^\)]*\)', r'\1', clean)
        clean = re.sub(r'\*+', '', clean)
        clean = re.sub(r'<[^>]*>', '', clean)

        # Remove special symbols that get narrated
        clean = clean.replace('®', '')
        clean = clean.replace('™', '')
        clean = clean.replace('©', '')
        clean = clean.replace('→', ', ')
        clean = clean.replace('←', ', ')
        clean = clean.replace('•', ', ')
        clean = clean.replace('●', ', ')
        clean = clean.replace('«', '')
        clean = clean.replace('»', '')
        clean = clean.replace('\u2014', ', ')  # em dash
        clean = clean.replace('\u2013', ', ')  # en dash
        clean = clean.replace('\u2026', '...')  # ellipsis
        clean = clean.replace('\u201c', '')  # left double quote
        clean = clean.replace('\u201d', '')  # right double quote
        clean = clean.replace('\u2018', '')  # left single quote
        clean = clean.replace('\u2019', '')  # right single quote

        clean = clean.strip()
        if len(clean) < 3:
            continue

        filtered.append(clean)

    text = ". ".join(filtered)
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\.\s*\.', '.', text)
    return text.strip()


def speak(text):
    txt_file = tempfile.NamedTemporaryFile(suffix='.txt', delete=False, mode='w', encoding='utf-8')
    txt_file.write(text)
    txt_file.close()

    mp3_file = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False)
    mp3_file.close()

    try:
        subprocess.run(
            ['python', '-m', 'edge_tts', '--voice', 'es-ES-ElviraNeural',
             '--rate', '+15%',
             '--file', txt_file.name, '--write-media', mp3_file.name],
            check=True, capture_output=True
        )

        # Play with PowerShell MediaPlayer
        ps_script = f'''
Add-Type -AssemblyName PresentationCore
$player = New-Object System.Windows.Media.MediaPlayer
$player.Open([Uri]::new("{mp3_file.name}"))
$player.Play()
Start-Sleep -Milliseconds 500
while ($player.NaturalDuration.HasTimeSpan -eq $false) {{ Start-Sleep -Milliseconds 100 }}
$duration = $player.NaturalDuration.TimeSpan.TotalSeconds
Start-Sleep -Seconds ($duration + 0.5)
$player.Stop()
$player.Close()
'''
        subprocess.run(['powershell', '-ExecutionPolicy', 'Bypass', '-Command', ps_script],
                       capture_output=True)
    finally:
        try:
            os.unlink(txt_file.name)
        except:
            pass
        try:
            os.unlink(mp3_file.name)
        except:
            pass


if __name__ == '__main__':
    main()
