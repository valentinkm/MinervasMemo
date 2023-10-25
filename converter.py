def vtt_to_md(transcript, output_path, folder):
    """
    Convert a webttv meeting transcript .vtt file to a .md file and remove redundant information

    Parameters:
    - transcript (str): Path to the .vtt file in the docs folder

    Returns:
    - raw_md (str): Path to the raw .md file of the meeting transcript
    """
    

    if not (transcript.startswith("docs_mr/") or transcript.startswith("docs_refine/")):
        transcript = f"{folder}/{transcript}"

    vtt_path = transcript
    
    print(f"Reading from {vtt_path}")  # Debugging line
    
    with open(vtt_path, "r", encoding="utf-8") as file:
        vtt_content = file.readlines()

    # Process and refine the content, omitting the "WEBVTT" redundant speaker information
    docs_md = []
    current_speaker = None
    current_start_timestamp = None
    current_end_timestamp = None
    speaker_dialogues = []

    for line in vtt_content:
        line = line.strip()
        print(f"Processing line: {line}")
        # Skip "WEBVTT" and empty lines
        if not line or line == "WEBVTT":
            continue

        # If line contains a speaker's name
        if '"' in line and '-->' not in line:
            new_speaker = line.split('"')[1] # Get the speaker's name
            
            # If we have a previous speaker's dialogues, append them to the output
            if current_speaker and new_speaker != current_speaker:
                docs_md.append("\n")
                # Add the previous speaker's name and timestamps to the output
                docs_md.append(f'### "{current_speaker}" [{current_start_timestamp}-{current_end_timestamp}]')
                docs_md.extend(speaker_dialogues) # Add the speaker's dialogues to the output
                speaker_dialogues = [] # Reset the speaker's dialogues
            current_speaker = new_speaker # Update the current speaker
            current_start_timestamp = None # Reset the start timestamp

        # If line contains a timestamped dialogue
        elif '-->' in line:
            timestamp_start, timestamp_end = line.split(' --> ') # Get the start and end timestamps
            
            # Setting the start timestamp if it's the first dialogue of the current speaker
            if not current_start_timestamp:
                current_start_timestamp = timestamp_start # Setting the start timestamp
            
            # Updating the end timestamp for every dialogue of the current speaker
            current_end_timestamp = timestamp_end

        # If it's a dialogue
        else:
            speaker_dialogues.append(line) # Add the dialogue to the speaker's dialogues

    # Add the last speaker's dialogues to the output
    if current_speaker:
        docs_md.append("\n")
        docs_md.append(f'### "{current_speaker}" [{current_start_timestamp}-{current_end_timestamp}]')
        docs_md.extend(speaker_dialogues)

    # Write to a .md file
    raw_md = vtt_path.replace(".vtt", ".md")

    print(f"Writing to {raw_md}")  # Debugging line
    with open(output_path, "w", encoding="utf-8") as file:

        file.write("\n".join(docs_md))
    print(f"Successfully converted {vtt_path} to {output_path}")
    return output_path

