# Enhanced RAG System for Claude-like Conversational Responses
# This enhancement focuses on better prompt engineering and response generation

from typing import List, Dict, Any, Optional
import re
from dataclasses import dataclass

@dataclass
class EnhancedSource:
    """Enhanced source with better context extraction."""
    doc_id: str
    score: float
    preview: str
    full_context: str
    section_title: str = ""
    page_number: Optional[int] = None

class ClaudeLikePromptEngineer:
    """Advanced prompt engineering for Claude-like responses."""
    
    def __init__(self):
        self.system_prompt = self._create_system_prompt()
    
    def _create_system_prompt(self) -> str:
        """Create a comprehensive system prompt for legal analysis."""
        return """You are an expert legal AI assistant with deep knowledge of Indian law and legal principles. Your role is to provide comprehensive, accurate, and contextual legal analysis based on the provided documents.

RESPONSE GUIDELINES:
1. **Comprehensive Analysis**: Don't just quote the law - explain its implications, context, and practical applications
2. **Current Status**: Always mention if laws have been struck down, amended, or are no longer valid
3. **Multiple Perspectives**: Consider different legal interpretations and viewpoints
4. **Practical Implications**: Explain what this means for legal practice, clients, or society
5. **Related Concepts**: Connect to related legal principles, cases, or statutes
6. **Clear Structure**: Use clear headings, bullet points, and logical flow
7. **Caveats**: Mention limitations, exceptions, or areas of legal uncertainty

TONE AND STYLE:
- Conversational yet professional
- Accessible to both legal professionals and educated laypersons
- Analytical and thoughtful
- Balanced and objective
- Include relevant context and background
"""

    def create_enhanced_legal_prompt(self, 
                                   question: str, 
                                   sources: List[EnhancedSource],
                                   conversation_context: str = "") -> str:
        """Create an enhanced prompt for legal analysis."""
        
        # Extract and organize source content
        source_content = self._organize_sources(sources)
        
        # Detect question type for tailored response
        question_type = self._classify_question(question)
        
        prompt = f"""{self.system_prompt}

DOCUMENT SOURCES:
{source_content}

CONVERSATION CONTEXT:
{conversation_context}

QUESTION TYPE: {question_type}
USER QUESTION: {question}

Please provide a comprehensive legal analysis that:
1. Directly answers the user's question
2. Provides relevant legal context and background
3. Explains the current legal status (especially important for Indian law)
4. Discusses practical implications and applications
5. Mentions any relevant case law or amendments
6. Concludes with actionable insights or recommendations where appropriate

IMPORTANT: If discussing Section 497 of the Indian Penal Code, note that it was struck down by the Supreme Court in Joseph Shine v. Union of India (2018) as unconstitutional.

Your response should be conversational, analytical, and provide value beyond simple fact retrieval."""

        return prompt
    
    def _organize_sources(self, sources: List[EnhancedSource]) -> str:
        """Organize sources into a coherent structure."""
        if not sources:
            return "No relevant sources found."
        
        organized = []
        for i, source in enumerate(sources, 1):
            # Clean up document path for display
            doc_name = self._clean_doc_path(source.doc_id)
            
            source_text = f"""
SOURCE {i} - {doc_name} (Relevance: {source.score:.1%})
{'-' * 50}
{source.full_context if hasattr(source, 'full_context') and source.full_context else source.preview}
"""
            organized.append(source_text)
        
        return "\n".join(organized)
    
    def _clean_doc_path(self, doc_path: str) -> str:
        """Clean document path for better display."""
        import os
        return os.path.basename(doc_path)
    
    def _classify_question(self, question: str) -> str:
        """Classify the question type to tailor response."""
        question_lower = question.lower()
        
        if any(word in question_lower for word in ['what is', 'define', 'definition']):
            return "DEFINITIONAL"
        elif any(word in question_lower for word in ['how to', 'process', 'procedure']):
            return "PROCEDURAL"
        elif any(word in question_lower for word in ['penalty', 'punishment', 'fine']):
            return "PENALTY_INQUIRY"
        elif any(word in question_lower for word in ['case law', 'judgment', 'ruling']):
            return "CASE_LAW_INQUIRY"
        elif any(word in question_lower for word in ['current', 'valid', 'still applicable']):
            return "STATUS_INQUIRY"
        elif any(word in question_lower for word in ['compare', 'difference', 'versus']):
            return "COMPARATIVE"
        else:
            return "GENERAL_LEGAL_INQUIRY"

class EnhancedResponseGenerator:
    """Generate Claude-like responses using better LLM integration."""
    
    def __init__(self, llm_client):
        self.llm_client = llm_client
        self.prompt_engineer = ClaudeLikePromptEngineer()
    
    def generate_enhanced_response(self, 
                                 question: str,
                                 sources: List[Dict],
                                 conversation_history: List[Dict] = None) -> Dict[str, Any]:
        """Generate an enhanced, Claude-like response."""
        
        # Convert sources to enhanced format
        enhanced_sources = self._convert_sources(sources)
        
        # Build conversation context
        context = self._build_conversation_context(conversation_history)
        
        # Create enhanced prompt
        prompt = self.prompt_engineer.create_enhanced_legal_prompt(
            question, enhanced_sources, context
        )
        
        # Generate response with better parameters
        response = self._generate_with_advanced_settings(prompt)
        
        # Post-process response
        enhanced_response = self._post_process_response(response, question, enhanced_sources)
        
        return enhanced_response
    
    def _convert_sources(self, sources: List[Dict]) -> List[EnhancedSource]:
        """Convert basic sources to enhanced format."""
        enhanced = []
        for source in sources:
            enhanced_source = EnhancedSource(
                doc_id=source.get('doc_id', ''),
                score=source.get('score', 0.0),
                preview=source.get('preview', ''),
                full_context=self._extract_full_context(source),
                section_title=self._extract_section_title(source.get('preview', ''))
            )
            enhanced.append(enhanced_source)
        return enhanced
    
    def _extract_full_context(self, source: Dict) -> str:
        """Extract fuller context from source (implement based on your data structure)."""
        # This should retrieve more context around the matched text
        # For now, return the preview but in practice you'd get more surrounding text
        return source.get('preview', '')
    
    def _extract_section_title(self, text: str) -> str:
        """Extract section titles from legal text."""
        # Look for patterns like "Section 497", "Article 14", etc.
        section_patterns = [
            r'Section \d+',
            r'Article \d+',
            r'Rule \d+',
            r'Chapter [IVX]+',
        ]
        
        for pattern in section_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group()
        return ""
    
    def _build_conversation_context(self, history: List[Dict]) -> str:
        """Build conversation context from history."""
        if not history:
            return "This is the start of our conversation."
        
        context_parts = []
        for entry in history[-3:]:  # Last 3 exchanges
            if entry.get('role') == 'user':
                context_parts.append(f"User asked: {entry.get('content', '')}")
            elif entry.get('role') == 'assistant':
                context_parts.append(f"Assistant responded about: {entry.get('summary', '')}")
        
        return "\n".join(context_parts)
    
    def _generate_with_advanced_settings(self, prompt: str) -> str:
        """Generate response with advanced LLM settings."""
        try:
            # Example for different LLM clients
            if hasattr(self.llm_client, 'chat'):
                # For chat-based models
                response = self.llm_client.chat(
                    messages=[
                        {"role": "system", "content": "You are an expert legal AI assistant."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,  # Lower temperature for more factual responses
                    max_tokens=1500,  # Longer responses
                    top_p=0.9,
                    frequency_penalty=0.1,
                    presence_penalty=0.1
                )
                return response.choices[0].message.content
            
            elif hasattr(self.llm_client, 'generate'):
                # For completion-based models
                response = self.llm_client.generate(
                    prompt=prompt,
                    temperature=0.3,
                    max_tokens=1500,
                    top_p=0.9,
                    repetition_penalty=1.1,
                    stop_sequences=["Human:", "User:", "Question:"]
                )
                return response.text
            
            else:
                # Fallback for basic models
                return self.llm_client(prompt)
                
        except Exception as e:
            return f"I apologize, but I encountered an error while generating the response: {str(e)}"
    
    def _post_process_response(self, response: str, question: str, sources: List[EnhancedSource]) -> Dict[str, Any]:
        """Post-process and enhance the response."""
        
        # Add legal disclaimers if needed
        if self._needs_disclaimer(response):
            response += "\n\n*Disclaimer: This information is for educational purposes only and should not be considered as legal advice. Please consult with a qualified legal professional for specific legal matters.*"
        
        # Add source citations in a more readable format
        citations = self._create_citations(sources)
        
        # Calculate confidence based on source quality and LLM certainty
        confidence = self._calculate_enhanced_confidence(response, sources)
        
        # Extract key points for summary
        key_points = self._extract_key_points(response)
        
        return {
            "answer": response,
            "confidence": confidence,
            "sources": self._format_sources_for_display(sources),
            "citations": citations,
            "key_points": key_points,
            "response_type": "enhanced_legal_analysis",
            "disclaimer_added": self._needs_disclaimer(response)
        }
    
    def _needs_disclaimer(self, response: str) -> bool:
        """Check if response needs legal disclaimer."""
        legal_advice_indicators = [
            "you should", "recommend", "advise", "suggest that you",
            "in your case", "for your situation"
        ]
        return any(indicator in response.lower() for indicator in legal_advice_indicators)
    
    def _create_citations(self, sources: List[EnhancedSource]) -> List[str]:
        """Create properly formatted citations."""
        citations = []
        for i, source in enumerate(sources, 1):
            doc_name = source.doc_id.split('\\')[-1] if '\\' in source.doc_id else source.doc_id
            if source.section_title:
                citation = f"[{i}] {doc_name} - {source.section_title}"
            else:
                citation = f"[{i}] {doc_name}"
            citations.append(citation)
        return citations
    
    def _calculate_enhanced_confidence(self, response: str, sources: List[EnhancedSource]) -> float:
        """Calculate enhanced confidence score."""
        base_confidence = sum(source.score for source in sources) / len(sources) if sources else 0.0
        
        # Adjust based on response quality indicators
        quality_indicators = [
            ("specific section numbers" in response.lower(), 0.1),
            ("case law" in response.lower(), 0.1),
            ("supreme court" in response.lower(), 0.05),
            ("struck down" in response.lower(), 0.05),
            ("unconstitutional" in response.lower(), 0.05),
        ]
        
        for indicator, boost in quality_indicators:
            if indicator:
                base_confidence += boost
        
        return min(base_confidence, 1.0)
    
    def _extract_key_points(self, response: str) -> List[str]:
        """Extract key points from the response."""
        # Simple extraction - look for numbered points or strong statements
        lines = response.split('\n')
        key_points = []
        
        for line in lines:
            line = line.strip()
            if (line.startswith(('1.', '2.', '3.', '•', '-')) or 
                'important' in line.lower() or 
                'note that' in line.lower() or
                'however' in line.lower()):
                key_points.append(line)
        
        return key_points[:5]  # Return top 5 key points
    
    def _format_sources_for_display(self, sources: List[EnhancedSource]) -> List[Dict]:
        """Format sources for better display."""
        formatted = []
        for source in sources:
            formatted.append({
                "document": source.doc_id.split('\\')[-1] if '\\' in source.doc_id else source.doc_id,
                "relevance_score": f"{source.score:.1%}",
                "section": source.section_title,
                "preview": source.preview[:200] + "..." if len(source.preview) > 200 else source.preview
            })
        return formatted

# Integration Example
class EnhancedLegalRAGSystem:
    """Enhanced RAG system with Claude-like responses."""
    
    def __init__(self, existing_rag_system):
        self.base_system = existing_rag_system
        self.response_generator = EnhancedResponseGenerator(existing_rag_system.llm)
        self.conversation_history = []
    
    def query_with_enhancement(self, question: str, **kwargs) -> Dict[str, Any]:
        """Enhanced query method that generates Claude-like responses."""
        
        # Get basic RAG results
        basic_result = self.base_system.query(question, **kwargs)
        
        # Generate enhanced response
        enhanced_result = self.response_generator.generate_enhanced_response(
            question=question,
            sources=basic_result.get('sources', []),
            conversation_history=self.conversation_history
        )
        
        # Update conversation history
        self._update_conversation_history(question, enhanced_result)
        
        return enhanced_result
    
    def _update_conversation_history(self, question: str, response: Dict):
        """Update conversation history for context."""
        self.conversation_history.append({
            "role": "user",
            "content": question,
            "timestamp": "current"  # Add proper timestamp
        })
        
        self.conversation_history.append({
            "role": "assistant",
            "content": response.get("answer", ""),
            "summary": question[:100],  # Brief summary
            "confidence": response.get("confidence", 0.0),
            "timestamp": "current"
        })
        
        # Keep only last 10 exchanges
        if len(self.conversation_history) > 20:
            self.conversation_history = self.conversation_history[-20:]

# Usage Example
"""
# Initialize your enhanced system
enhanced_rag = EnhancedLegalRAGSystem(your_existing_rag_system)

# Query with enhancement
result = enhanced_rag.query_with_enhancement(
    "What is the current legal status of Section 497 of the Indian Penal Code?"
)

print("Enhanced Answer:", result["answer"])
print("Confidence:", result["confidence"])
print("Key Points:", result["key_points"])
"""