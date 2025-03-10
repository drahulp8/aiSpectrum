"""
Summarizer module that analyzes multiple AI responses and produces a consensus 
summary highlighting the best parts of each.
"""

import openai
import json

class ResponseSummarizer:
    """Summarizes multiple AI responses to find consensus and highlight the best answers."""
    
    def __init__(self, api_key=None):
        """Initialize with optional API key."""
        self.api_key = api_key
        self.summarization_prompt = """
You are a meta-AI analyst that evaluates responses from multiple AI models.

User Query: {query}

I will provide you with responses from different AI models to this query.

AI Responses:
{responses}

Please analyze these responses and create a summary that:
1. Identifies the consensus points where models agree
2. Highlights unique insights from individual models
3. Addresses any contradictions between models
4. Provides the most accurate, comprehensive answer based on all responses
5. Cites which model provided which key insight when relevant

Your analysis should be clear, concise, and focused on giving the user the highest quality answer.
"""
    
    def _format_responses_for_prompt(self, response_dict):
        """Format the responses dictionary for the prompt."""
        formatted = ""
        for model_name, response_data in response_dict.items():
            if response_data.get("status") == "success":
                formatted += f"--- {model_name.upper()} RESPONSE ---\n"
                formatted += f"{response_data.get('content', 'No content')}\n\n"
        return formatted
    
    def summarize(self, query, responses):
        """
        Generate a meta-summary of all AI responses.
        
        Args:
            query (str): The original user query
            responses (dict): Dictionary of responses from different models
            
        Returns:
            dict: Summarized response with metadata
        """
        # Return early if no successful responses
        successful_responses = {k: v for k, v in responses.items() 
                               if v.get("status") == "success"}
        
        if not successful_responses:
            return {
                "content": "No successful responses were received from any AI models.",
                "model": "meta-summarizer",
                "status": "error"
            }
        
        # If only one successful response, return it directly
        if len(successful_responses) == 1:
            model_name = list(successful_responses.keys())[0]
            return {
                "content": f"Only {model_name} provided a successful response:\n\n" + 
                           successful_responses[model_name]["content"],
                "model": "meta-summarizer",
                "status": "success"
            }
        
        try:
            # Format responses for the prompt
            formatted_responses = self._format_responses_for_prompt(responses)
            
            # Prepare the prompt with the query and responses
            formatted_prompt = self.summarization_prompt.format(
                query=query,
                responses=formatted_responses
            )
            
            # Use OpenAI directly
            if self.api_key:
                client = openai.OpenAI(api_key=self.api_key)
                completion = client.chat.completions.create(
                    model="gpt-3.5-turbo",  # Using a capable but cost-effective model
                    messages=[
                        {"role": "system", "content": "You are an expert AI model analyst."},
                        {"role": "user", "content": formatted_prompt}
                    ],
                    temperature=0.0  # Keep it factual
                )
                
                summary = completion.choices[0].message.content
                
                return {
                    "content": summary,
                    "model": "meta-summarizer (OpenAI)",
                    "status": "success"
                }
            else:
                # If no API key, create a simple summary
                model_names = list(successful_responses.keys())
                simple_summary = f"Responses received from {', '.join(model_names)}.\n\n"
                simple_summary += "To see a detailed analysis and comparison of these responses, please add an OpenAI or Gemini API key in the settings."
                
                return {
                    "content": simple_summary,
                    "model": "meta-summarizer (basic)",
                    "status": "success"
                }
                
        except Exception as e:
            return {
                "content": f"Error generating summary: {str(e)}",
                "model": "meta-summarizer", 
                "status": "error"
            }


def summarize_responses(query, responses, api_key=None):
    """Helper function to summarize responses."""
    print("🔍 Summarizer called with API key:", "Available" if api_key else "Not available")
    print(f"🔍 Summarizing responses for query: {query[:50]}...")
    print(f"🔍 Number of responses to summarize: {len(responses)}")
    
    summarizer = ResponseSummarizer(api_key)
    result = summarizer.summarize(query, responses)
    
    print(f"🔍 Summarization complete with status: {result.get('status')}")
    if result.get('status') == 'error':
        print(f"🔍 Summarization error: {result.get('content')}")
    
    return result