import os
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def basic_llm_call(prompt):
    """Step 1: The simplest possible LLM interaction"""
    
    # Get API key
    api_key = os.getenv("GROQ_API_KEY")
    
    if not api_key:
        print("❌ ERROR: GROQ_API_KEY not found in .env file!")
        print("Make sure your .env file contains: GROQ_API_KEY=your_actual_key")
        return None
    
    # Initialize Groq client
    client = Groq(api_key=api_key)
    
    # Make the API call
    try:
        response = client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200
        )
        
        return response.choices[0].message.content
    
    except Exception as e:
        print(f"❌ API Error: {e}")
        return None

# Test it
if __name__ == "__main__":
    print("=" * 50)
    print("TESTING BASIC LLM CONNECTION")
    print("=" * 50)
    
    # Check if .env file exists
    if not os.path.exists(".env"):
        print("\n⚠️  WARNING: .env file not found!")
        print("Create a .env file with your Groq API key:")
        print("GROQ_API_KEY=gsk_your_actual_key_here")
    else:
        result = basic_llm_call("What is the capital of France? Reply in one sentence.")
        
        if result:
            print("\n✅ SUCCESS! LLM Response:")
            print("-" * 50)
            print(result)
            print("-" * 50)
        else:
            print("\n❌ Failed to get response. Check your API key and internet connection.")