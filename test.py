import os
from dotenv import load_dotenv
load_dotenv()
from utils.audio_processor import process_input
from core.transciber import transcribe_all
from core.summarize import summarize,generate_title
from core.extractor import extract_action_items,extract_key_decisions,extract_questions


source = 'https://youtu.be/_Q-e_nczWqM?si=rH8qzVbnHY0_VMnQ'
language = 'english' # change the 'hinglish' = Sarvam , 'english' = Whisper


chunks = process_input(source)
transcript = transcribe_all(chunks,language=language)
print('\n' + '=' * 60)
print('Transcript')
print('='*60)
print(transcript[:500] + '...' if len(transcript)>500 else transcript)

title = generate_title(transcript)
summary = summarize(transcript)

print('\n' + '=' * 60)
print('Title',{title})
print('='*60)

print('\nSummary')
print('='*60)
print(summary)

action_items = extract_action_items(transcript)
decisions = extract_key_decisions(transcript)
questions = extract_questions(transcript)

print('\n' + '=' * 60)
print('Action Items')
print('='*60)
print(action_items)

print('\n' + '=' * 60)
print('Key Decision')
print('='*60)
print(decisions)

print('\n' + '=' * 60)
print('Open Questions')
print('='*60)
print(questions)
