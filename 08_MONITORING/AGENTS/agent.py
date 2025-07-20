# Simple RAGAS Agent Evaluation using Gemini
# Install required packages: pip install ragas langchain-google-genai

import os
from dotenv import load_dotenv
import pandas as pd
from datasets import Dataset

# RAGAS imports
from ragas import evaluate
from ragas.metrics import (
    tool_call_accuracy,
    agent_goal_accuracy,
    AgentTrajectoryEvaluator
)

# Langchain imports for Gemini
from langchain_google_genai import ChatGoogleGenerativeAI

# Load environment variables
load_dotenv()

# Set up Gemini API key
os.environ["GOOGLE_API_KEY"] = os.getenv("GEMINI_API_KEY")

def create_agent_sample_data():
    """Create a single sample of agent interaction data for evaluation"""
    
    # Sample agent trajectory - represents a weather query agent
    sample_data = {
        'user_input': ['What is the weather like in New York today?'],
        
        'reference': ['The weather in New York today is sunny with a temperature of 75°F (24°C), humidity at 60%, and light winds from the southwest at 8 mph.'],
        
        'response': ['Based on the weather data I retrieved, New York is experiencing sunny weather today with a pleasant temperature of 75°F. The humidity is moderate at 60% and there are light southwest winds at 8 mph. Perfect weather for outdoor activities!'],
        
        # Agent trajectory - sequence of steps the agent took
        'agent_trajectory': [[
            {
                'tool_name': 'weather_api',
                'tool_input': {'location': 'New York', 'date': 'today'},
                'tool_output': {
                    'temperature': '75°F',
                    'condition': 'sunny',
                    'humidity': '60%',
                    'wind': '8 mph SW'
                }
            }
        ]],
        
        # Expected tools that should be called for this query
        'reference_tools': [['weather_api']],
        
        # Ground truth for whether the agent achieved its goal
        'expected_goal_achieved': [True]
    }
    
    return sample_data

def create_complex_agent_sample():
    """Create a more complex agent sample with multiple tool calls"""
    
    complex_sample = {
        'user_input': ['Book a flight from Boston to Seattle for next Friday and check the weather forecast for Seattle'],
        
        'reference': ['I found flights from Boston to Seattle on Friday starting at $285. The weather in Seattle next Friday is expected to be partly cloudy with temperatures around 62°F and light rain possible in the evening.'],
        
        'response': ['I\'ve found several flight options from Boston to Seattle for next Friday. The best option is a direct flight departing at 9:15 AM for $285. Regarding the weather, Seattle will be partly cloudy next Friday with a high of 62°F and a chance of light rain in the evening, so you might want to pack a light jacket.'],
        
        'agent_trajectory': [[
            {
                'tool_name': 'flight_search',
                'tool_input': {
                    'origin': 'Boston',
                    'destination': 'Seattle', 
                    'date': 'next Friday'
                },
                'tool_output': {
                    'flights': [
                        {'time': '9:15 AM', 'price': '$285', 'airline': 'Alaska'},
                        {'time': '2:30 PM', 'price': '$310', 'airline': 'Delta'}
                    ]
                }
            },
            {
                'tool_name': 'weather_forecast',
                'tool_input': {
                    'location': 'Seattle',
                    'date': 'next Friday'
                },
                'tool_output': {
                    'condition': 'partly cloudy',
                    'temperature': '62°F',
                    'precipitation': 'light rain possible evening'
                }
            }
        ]],
        
        'reference_tools': [['flight_search', 'weather_forecast']],
        'expected_goal_achieved': [True]
    }
    
    return complex_sample

def setup_gemini_evaluator():
    """Initialize Gemini model for RAGAS evaluation"""
    
    # Initialize Gemini model
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        temperature=0.1,
        google_api_key=os.getenv("GEMINI_API_KEY")
    )
    
    return llm

def evaluate_agent_performance(sample_data, use_complex=False):
    """Evaluate agent performance using RAGAS metrics"""
    
    print("🤖 Setting up RAGAS Agent Evaluation with Gemini...")
    
    # Setup Gemini evaluator
    llm = setup_gemini_evaluator()
    
    # Create dataset from sample
    if use_complex:
        data = create_complex_agent_sample()
        print("📋 Using complex multi-tool agent sample")
    else:
        data = create_agent_sample_data()
        print("📋 Using simple single-tool agent sample")
    
    # Convert to RAGAS dataset format
    dataset = Dataset.from_dict(data)
    
    print(f"\n📊 Sample Data Overview:")
    print(f"User Input: {data['user_input'][0]}")
    print(f"Agent Response: {data['response'][0][:100]}...")
    print(f"Tools Used: {[step['tool_name'] for step in data['agent_trajectory'][0]]}")
    
    # Define evaluation metrics for agents
    metrics = [
        tool_call_accuracy,           # Evaluates if correct tools were called
        agent_goal_accuracy,          # Evaluates if agent achieved the user's goal
    ]
    
    print(f"\n🔍 Running RAGAS evaluation with {len(metrics)} agent metrics...")
    
    try:
        # Run evaluation
        result = evaluate(
            dataset=dataset,
            metrics=metrics,
            llm=llm,
            embeddings=None  # Using default embeddings
        )
        
        return result
        
    except Exception as e:
        print(f"❌ Evaluation failed: {e}")
        return None

def display_results(result):
    """Display evaluation results in a readable format"""
    
    if result is None:
        print("❌ No results to display")
        return
    
    print("\n" + "="*50)
    print("🎯 RAGAS AGENT EVALUATION RESULTS")
    print("="*50)
    
    # Overall scores
    print(f"\n📈 Overall Metrics:")
    for metric, score in result.items():
        if isinstance(score, (int, float)):
            print(f"  {metric}: {score:.3f}")
    
    # Convert to DataFrame for detailed view
    df = result.to_pandas()
    
    print(f"\n📋 Detailed Results:")
    print(f"Dataset size: {len(df)} sample(s)")
    
    # Display key columns
    key_columns = ['user_input', 'response', 'tool_call_accuracy', 'agent_goal_accuracy']
    available_columns = [col for col in key_columns if col in df.columns]
    
    if available_columns:
        print(f"\nKey Results:")
        for col in available_columns:
            if col in ['tool_call_accuracy', 'agent_goal_accuracy']:
                value = df[col].iloc[0] if len(df) > 0 else 'N/A'
                print(f"  {col}: {value}")
    
    # Save results
    df.to_csv("ragas_agent_evaluation_results.csv", index=False)
    print(f"\n💾 Results saved to: ragas_agent_evaluation_results.csv")

def main():
    """Main execution function"""
    
    print("🚀 RAGAS Agent Evaluation with Gemini")
    print("="*40)
    
    # Check API key
    if not os.getenv("GEMINI_API_KEY"):
        print("❌ GEMINI_API_KEY not found in environment variables")
        print("Please set GEMINI_API_KEY in your .env file")
        return
    
    try:
        # Evaluate simple agent sample
        print("\n🔍 Evaluating Simple Agent Sample...")
        simple_result = evaluate_agent_performance(None, use_complex=False)
        
        if simple_result:
            print("\n📊 Simple Agent Results:")
            display_results(simple_result)
        
        # Evaluate complex agent sample
        print(f"\n{'-'*50}")
        print("🔍 Evaluating Complex Multi-Tool Agent Sample...")
        complex_result = evaluate_agent_performance(None, use_complex=True)
        
        if complex_result:
            print("\n📊 Complex Agent Results:")
            display_results(complex_result)
        
    except Exception as e:
        print(f"❌ Error during evaluation: {e}")
        print("💡 Make sure you have:")
        print("   1. Set GEMINI_API_KEY in .env file")
        print("   2. Installed: pip install ragas langchain-google-genai")
        print("   3. Valid Gemini API access")

if __name__ == "__main__":
    main()

# Example .env file content:
"""
GEMINI_API_KEY=your_gemini_api_key_here
"""

# Required packages:
"""
pip install ragas
pip install langchain-google-genai
pip install datasets
pip install pandas
pip install python-dotenv
"""