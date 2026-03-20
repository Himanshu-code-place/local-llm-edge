import ollama

def summarise_patient_note(note):
    response = ollama.chat(
        model='llama3.2',
        messages=[
            {
                'role': 'system',
                'content': 'You are a clinical documentation assistant. Summarise patient notes in exactly 3 sections: 1. Chief Complaint 2. Assessment 3. Plan. Be concise and use simple language.'
            },
            {
                'role': 'user',
                'content': 'Summarise this patient note:\n' + note
            }
        ]
    )
    return response['message']['content']

note1 = "Patient is a 45 year old male with chest pain since 3 days. Pain is crushing and radiates to left arm. Patient has history of high blood pressure. No fever. No vomiting."

note2 = "Patient is a 60 year old female with diabetes. Came in with blurred vision since 1 week. Blood sugar levels are very high at 400. Patient is on insulin but missed doses for 3 days."

print("==================================================")
print("PATIENT 1 SUMMARY:")
print("==================================================")
print(summarise_patient_note(note1))

print()
print("==================================================")
print("PATIENT 2 SUMMARY:")
print("==================================================")
print(summarise_patient_note(note2))


