import pandas as pd
import os
import time
import numpy as np
from evidently import Dataset, DataDefinition, Report
from evidently.descriptors import (
    # LLM-based (rate limited)
    ContextQualityLLMEval, FaithfulnessLLMEval,
    # Non-LLM metrics (no rate limits)
    TextLength, WordCount, SemanticSimilarity, BERTScore, Sentiment,
    OOVWordsPercentage, NonLetterCharacterPercentage, SentenceCount,
    Contains, DoesNotContain, RegExp, ExactMatch
)
from evidently.presets import TextEvals

from dotenv import load_dotenv
import time

load_dotenv()  # take environment variables from .env.
os.environ["GEMINI_API_KEY"] = os.getenv("GEMINI_API_KEY", None)

# ===== SAMPLE CONTROL CONFIGURATION =====
TOTAL_SAMPLES = 3        # Total dataset size
ANALYSIS_SAMPLES = 3     # Samples for non-LLM analysis (can be same as total)
LLM_SAMPLES = 3          # Samples for LLM evaluation (keep low for rate limits)
BATCH_SIZE = 1           # LLM batch size
DELAY_BETWEEN_BATCHES = 10  # Seconds between LLM batches

# Set API key

# Generate larger synthetic RAG dataset with patterns
np.random.seed(42)

def create_rag_dataset(num_samples):
    """Create RAG dataset with specified number of samples"""
    
    # Base data - will be repeated/truncated as needed
    questions_base = [
        "What is artificial intelligence?", "How does machine learning work?",
        "Explain deep learning concepts", "What are neural networks?",
        "How does natural language processing work?", "What is computer vision?",
        "Explain reinforcement learning", "What is supervised learning?",
        "How do transformers work?", "What is the difference between AI and ML?",
        "Explain gradient descent", "What are convolutional neural networks?",
        "How does backpropagation work?", "What is overfitting in ML?",
        "Explain cross-validation", "What are decision trees?",
        "How does k-means clustering work?", "What is feature engineering?",
        "Explain ensemble methods", "What is regularization?"
    ]

    contexts_base = [
        "AI is artificial intelligence that simulates human thinking",
        "Machine learning uses algorithms to learn from data patterns",
        "Deep learning uses multi-layered neural networks for complex tasks",
        "Neural networks are computing systems inspired by biological brains",
        "NLP processes and understands human language using computational methods",
        "Computer vision enables machines to interpret visual information",
        "Reinforcement learning trains agents through rewards and penalties",
        "Supervised learning uses labeled data to train predictive models",
        "Transformers use attention mechanisms for sequence processing",
        "AI is broader concept while ML is a subset focused on learning",
        "Gradient descent optimizes model parameters by minimizing loss",
        "CNNs use convolution operations for processing grid-like data",
        "Backpropagation calculates gradients to update neural network weights",
        "Overfitting occurs when models memorize training data too closely",
        "Cross-validation splits data to evaluate model generalization",
        "Decision trees make predictions using tree-like decision structures",
        "K-means groups data points into k clusters based on similarity",
        "Feature engineering creates meaningful inputs for machine learning",
        "Ensemble methods combine multiple models for better predictions",
        "Regularization prevents overfitting by constraining model complexity"
    ]

    good_responses = [
        "AI refers to artificial intelligence, which simulates human cognitive abilities",
        "Machine learning algorithms analyze data to identify patterns and make predictions",
        "Deep learning employs neural networks with multiple layers for complex pattern recognition",
        "Neural networks are computational models inspired by the human brain structure",
        "Natural language processing uses computational techniques to understand human language",
        "Computer vision allows machines to analyze and interpret visual data",
        "Reinforcement learning trains models through trial and error with reward feedback",
        "Supervised learning uses labeled examples to train predictive algorithms",
        "Transformers utilize attention mechanisms to process sequential data effectively",
        "AI encompasses all intelligent systems while ML specifically focuses on learning algorithms"
    ]

    poor_responses = [
        "AI is just computers doing stuff",
        "ML works by magic algorithms", 
        "Deep learning is very deep and complex",
        "Neural networks are like brain cells",
        "NLP processes words somehow",
        "Computer vision sees things with cameras",
        "Reinforcement learning gives rewards",
        "Supervised learning supervises data",
        "Transformers transform data",
        "AI and ML are the same thing"
    ]

    # Extend arrays to match num_samples
    questions = (questions_base * ((num_samples // len(questions_base)) + 1))[:num_samples]
    contexts = (contexts_base * ((num_samples // len(contexts_base)) + 1))[:num_samples]
    
    # Create quality pattern: first half good, second half poor
    responses = []
    for i in range(num_samples):
        if i < num_samples // 2:  # First half are good
            responses.append(good_responses[i % len(good_responses)])
        else:  # Second half are poor
            responses.append(poor_responses[i % len(poor_responses)])
    
    # Create targets
    targets = [ctx.replace("uses", "utilizes").replace("algorithms", "methods") for ctx in contexts]
    
    return pd.DataFrame({
        'question': questions,
        'context': contexts,
        'response': responses,
        'target': targets,
        'timestamp': pd.date_range('2024-01-01', periods=num_samples, freq='H'),
        'user_id': [f"user_{i % max(1, num_samples//4)}" for i in range(num_samples)]
    })

def select_samples_for_analysis(data, num_samples, strategy="all"):
    """Select samples for analysis based on strategy"""
    
    if strategy == "all" or num_samples >= len(data):
        return data.head(num_samples)
    elif strategy == "balanced":
        # Half from beginning (good), half from end (poor)
        half = num_samples // 2
        good_samples = data.head(half)
        poor_samples = data.tail(num_samples - half)
        return pd.concat([good_samples, poor_samples]).reset_index(drop=True)
    elif strategy == "random":
        return data.sample(n=num_samples, random_state=42)
    elif strategy == "worst_first":
        return data.tail(num_samples)
    else:
        return data.head(num_samples)

# ===== MAIN EXECUTION =====
print(f"🔧 Configuration:")
print(f"  Total samples: {TOTAL_SAMPLES}")
print(f"  Analysis samples: {ANALYSIS_SAMPLES}")
print(f"  LLM samples: {LLM_SAMPLES}")
print(f"  Batch size: {BATCH_SIZE}")

# Create dataset
print(f"\n📝 Creating RAG dataset with {TOTAL_SAMPLES} samples...")
data = create_rag_dataset(TOTAL_SAMPLES)

# Select samples for analysis
analysis_data = select_samples_for_analysis(data, ANALYSIS_SAMPLES, strategy="all")
print(f"Selected {len(analysis_data)} samples for analysis")

print(f"Response quality distribution: {len([r for r in analysis_data['response'] if len(r) > 50])} detailed vs {len([r for r in analysis_data['response'] if len(r) <= 50])} brief")

# PHASE 1: Comprehensive non-LLM metrics (no rate limits)
print("\n=== PHASE 1: Non-LLM RAG Metrics ===")

non_llm_dataset = Dataset.from_pandas(
    analysis_data,
    data_definition=DataDefinition(text_columns=["question", "context", "response", "target"]),
    descriptors=[
        # Response quality metrics
        TextLength("response", alias="response_length"),
        WordCount("response", alias="response_words"),
        SentenceCount("response", alias="response_sentences"),
        
        # Semantic similarity metrics
        SemanticSimilarity(columns=["response", "target"], alias="response_target_similarity"),
        SemanticSimilarity(columns=["response", "context"], alias="response_context_similarity"),
        SemanticSimilarity(columns=["question", "context"], alias="question_context_relevance"),
        
        # Advanced similarity
        BERTScore(columns=["response", "target"], alias="bert_score"),
        BERTScore(columns=["response", "context"], alias="context_bert_score"),
        
        # Content quality checks
        OOVWordsPercentage("response", alias="response_oov_percentage"),
        NonLetterCharacterPercentage("response", alias="response_non_letter_pct"),
        Sentiment("response", alias="response_sentiment"),
        
        # Response completeness patterns
        Contains("response", items=["algorithm", "learning", "data", "model"], mode="any", alias="contains_ml_terms"),
        DoesNotContain("response", items=["I don't know", "unclear", "unsure"], alias="no_uncertainty"),
        RegExp("response", reg_exp=r'\b\w{10,}\b', alias="has_complex_words"),
        
        # Context utilization
        Contains("response", items=["machine", "learning", "neural", "data"], mode="any", alias="uses_context_terms"),
    ]
)

# Generate comprehensive report
print("Generating comprehensive non-LLM report...")
non_llm_report = Report([TextEvals()])
non_llm_result = non_llm_report.run(non_llm_dataset, None)
non_llm_result.save_html("rag_comprehensive_metrics.html")

print("✅ Comprehensive metrics saved to rag_comprehensive_metrics.html")

# Display key metrics
results_df = non_llm_dataset.as_dataframe()
print("\n📊 Key Quality Metrics Summary:")
print(f"Average response length: {results_df['response_length'].mean():.1f} chars")
print(f"Average response-target similarity: {results_df['response_target_similarity'].mean():.3f}")
print(f"Average question-context relevance: {results_df['question_context_relevance'].mean():.3f}")
print(f"Responses with ML terms: {results_df['contains_ml_terms'].sum()}/{len(results_df)}")
print(f"Responses without uncertainty: {results_df['no_uncertainty'].sum()}/{len(results_df)}")

# PHASE 2: LLM-based evaluation with rate limiting
print(f"\n=== PHASE 2: LLM-based Evaluation (Processing {LLM_SAMPLES} samples) ===")

# Select samples for LLM evaluation
llm_data = select_samples_for_analysis(analysis_data, LLM_SAMPLES, strategy="balanced")
print(f"Selected {len(llm_data)} samples for LLM evaluation")

try:
    llm_results = []
    
    for i in range(0, len(llm_data), BATCH_SIZE):
        batch_data = llm_data.iloc[i:i+BATCH_SIZE].copy()
        
        print(f"Processing LLM batch {i//BATCH_SIZE + 1} (rows {i}-{i+len(batch_data)-1})...")
        
        llm_dataset = Dataset.from_pandas(
            batch_data,
            data_definition=DataDefinition(text_columns=["question", "context", "response"]),
            descriptors=[
                ContextQualityLLMEval("context", question="question", 
                                    provider="gemini", model="gemini-1.5-flash"),
                # FaithfulnessLLMEval("response", context="context", 
                #                   provider="gemini", model="gemini-1.5-flash"),  # Uncomment to add faithfulness
            ]
        )
        
        batch_result = llm_dataset.as_dataframe()
        llm_results.append(batch_result)
        
        if i + BATCH_SIZE < len(llm_data):
            print(f"⏳ Waiting {DELAY_BETWEEN_BATCHES}s to avoid rate limits...")
            time.sleep(DELAY_BETWEEN_BATCHES)
    
    # Combine LLM results
    combined_llm_df = pd.concat(llm_results, ignore_index=True)
    
    # Save LLM results to CSV for inspection
    combined_llm_df.to_csv("llm_evaluation_results.csv", index=False)
    print(f"LLM results saved to llm_evaluation_results.csv")
    
    # Create a simple HTML report manually since TextEvals preset might not work with LLM-only data
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>RAG LLM Evaluation Results</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            table {{ border-collapse: collapse; width: 100%; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
            .metric {{ margin: 20px 0; }}
        </style>
    </head>
    <body>
        <h1>RAG LLM Evaluation Results</h1>
        <div class="metric">
            <h2>Processing Summary</h2>
            <p>Total samples processed: {len(combined_llm_df)}</p>
            <p>Batch size: {BATCH_SIZE}</p>
            <p>Model used: gemini-1.5-flash</p>
        </div>
        
        <div class="metric">
            <h2>Context Quality Results</h2>
            {combined_llm_df[['question', 'context', 'response'] + [col for col in combined_llm_df.columns if 'Context Quality' in col]].to_html(index=False, escape=False)}
        </div>
        
        <div class="metric">
            <h2>Full Results Table</h2>
            {combined_llm_df.to_html(index=False, escape=False)}
        </div>
    </body>
    </html>
    """
    
    with open("rag_llm_evaluation.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print("✅ LLM evaluation saved to rag_llm_evaluation.html")
    print("\n🤖 LLM Evaluation Summary:")
    if 'Context Quality' in combined_llm_df.columns:
        valid_contexts = combined_llm_df['Context Quality'].value_counts()
        print(f"Context Quality: {valid_contexts.to_dict()}")
    if 'Faithfulness' in combined_llm_df.columns:
        faithful_responses = combined_llm_df['Faithfulness'].value_counts()
        print(f"Faithfulness: {faithful_responses.to_dict()}")

except Exception as e:
    print(f"⚠️  LLM evaluation failed: {e}")
    print("💡 Try: 1) Increase DELAY_BETWEEN_BATCHES, 2) Reduce LLM_SAMPLES, 3) Check API quota")

print("\n🎉 RAG Monitoring Complete!")
print("\nFiles Generated:")
print("1. rag_comprehensive_metrics.html - Complete non-LLM analysis")
if 'combined_llm_df' in locals():
    print("2. rag_llm_evaluation.html - LLM-based quality assessment")

print(f"\n📈 Dataset Patterns Detected:")
print(f"- Response length variance: {results_df['response_length'].std():.1f}")
print(f"- Quality correlation: {results_df['response_target_similarity'].corr(results_df['response_length']):.3f}")
print(f"- Context relevance range: {results_df['question_context_relevance'].min():.3f} - {results_df['question_context_relevance'].max():.3f}")

print(f"\n🔧 To modify sample sizes, change these variables at the top:")
print(f"  TOTAL_SAMPLES = {TOTAL_SAMPLES}")
print(f"  ANALYSIS_SAMPLES = {ANALYSIS_SAMPLES}")
print(f"  LLM_SAMPLES = {LLM_SAMPLES}")