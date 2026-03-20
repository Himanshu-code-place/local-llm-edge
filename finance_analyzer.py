import ollama

def analyze_finance(text, analysis_type):
    
    if analysis_type == "1":
        system_prompt = "You are a financial analyst. Analyze the given earnings report and summarise in 3 sections: 1. Revenue Performance 2. Key Highlights 3. Future Outlook. Be concise and professional."
        user_message = "Analyze this earnings report:\n" + text
    
    elif analysis_type == "2":
        system_prompt = "You are a financial news analyst. Summarise the given news in 3 sections: 1. Main Event 2. Market Impact 3. Investor Takeaway. Be concise and professional."
        user_message = "Summarise this financial news:\n" + text
    
    elif analysis_type == "3":
        system_prompt = "You are a stock market expert. Analyze the given information and provide: 1. Bull Case 2. Bear Case 3. Recommendation. Be concise and professional."
        user_message = "Analyze this stock information:\n" + text
    
    response = ollama.chat(
        model='llama3.2',
        messages=[
            {
                'role': 'system',
                'content': system_prompt
            },
            {
                'role': 'user',
                'content': user_message
            }
        ]
    )
    return response['message']['content']

print("=" * 50)
print("  FINANCE AI ANALYZER")
print("  Powered by Local LLM — No Cloud")
print("=" * 50)
print()

while True:
    print("What do you want to analyze?")
    print("1. Earnings Report")
    print("2. Financial News")
    print("3. Stock Information")
    print("4. Quit")
    print("-" * 50)
    
    choice = input("Enter choice (1/2/3/4): ")
    
    if choice == "4":
        print("Goodbye!")
        break
    
    if choice not in ["1", "2", "3"]:
        print("Invalid choice! Enter 1, 2, 3 or 4")
        continue
    
    print()
    print("Enter your financial text below:")
    print("-" * 50)
    text = input(">> ")
    
    if len(text.strip()) == 0:
        print("Please enter some text!")
        continue
    
    print()
    print("Analyzing...")
    print("-" * 50)
    print(analyze_finance(text, choice))
    print("=" * 50)
    print()