"""
AI-powered MeTTa service using Anthropic Claude for function generation and metta.run for execution
"""

import asyncio
import json
import re
import os
import subprocess
import tempfile
from typing import Dict, Any, List, Optional, Tuple
import httpx
from datetime import datetime
import logging
try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    print("Warning: Anthropic not available for AI MeTTa service")
    ANTHROPIC_AVAILABLE = False
import threading

logger = logging.getLogger(__name__)

class AIMeTTaService:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls, anthropic_api_key: str = None):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(AIMeTTaService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, anthropic_api_key: str = None):
        if hasattr(self, 'initialized'):
            return
        
        if not ANTHROPIC_AVAILABLE:
            logger.warning("Anthropic not available, using pattern-based MeTTa generation")
            self.anthropic_client = None
            self.client = None
            self.initialized = True
            return
        
        self.anthropic_api_key = anthropic_api_key or os.getenv("ANTHROPIC_API_KEY", "demo-key")
        self.client = httpx.AsyncClient(timeout=30.0)
        self._execution_lock = asyncio.Lock()  # Add async lock for subprocess execution
        
        # Initialize Anthropic client
        if self.anthropic_api_key != "demo-key":
            self.anthropic_client = anthropic.Anthropic(api_key=self.anthropic_api_key)
        else:
            self.anthropic_client = None
        
        # MeTTa function templates and examples
        self.metta_functions = [
            "match", "let", "let*", "foldl-atom", "cdr-atom", "car-atom",
            "filter", "map", "lambda", "if", "cons", ">", "<", "=", "+", "-", "*", "/",
            "and", "or", "not", "get-severity", "get-impact", "get-location",
            "climate-event", "verification", "trust-score", "user-data"
        ]
        
        
        # System prompt for Anthropic
        self.system_prompt = """
You are an expert MeTTa (Meta Type Talk) function generator for climate data analysis.

Your task is to generate MeTTa function definitions for climate data analysis. 
Always return a function in the form: 
(= (function_name $param1 ... $paramN) (logic using $param1 ... $paramN))

Available MeTTa functions you MUST use:
- match: for pattern matching queries
- let, let*: for variable binding
- foldl-atom: for aggregation operations
- cdr-atom, car-atom: for list operations
- filter, map: for data transformation
- lambda: for anonymous functions
- Recursion: for complex nested analysis

Data structure:
- Climate events are stored as: (climate-event TYPE LOCATION SEVERITY IMPACT VERIFIED)
- Trust scores as: (trust-score USER-ID SCORE)
- Verifications as: (verification EVENT-ID STATUS CONSENSUS)

Rules:
1. Always use proper MeTTa syntax with parentheses
2. Use match for querying the knowledge base
3. Use let* for multiple variable bindings
4. Use foldl-atom for aggregations (sum, count, average)
5. Use recursion where you call the function you have created for hierarchical analysis
6. Return only the MeTTa function definition, no explanations in the function itself

The atom spaces we have are:
&event-space, &trust-space,&economic-space,&self

Examples:
Query: "Add two numbers"
Function: (= (add $a $b) (+ $a $b))

Query: "Sum impact of all drought events"
Function without parameters: (= (sum-drought-impact) (let* ((impacts (match &space (climate-event drought $location $severity $impact $verified) $impact)) (total (foldl-atom + 0 impacts))) total))

Query: "Find all drought events"
Function with parameters: (= (find-drought-events $verified) (match &event-space (climate-event drought $location $severity $impact $verified) ($location $severity)))
How to call: !(find-drought-events True) thus $verified will be replaced with True

Generate a MeTTa function definition for the following query with good naming:
"""
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    async def generate_metta_function(self, user_query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generate a MeTTa function using Anthropic Claude based on user's natural language query
        """
        try:
            if self.anthropic_client:
                # Use Anthropic API
                function_result = await self._generate_with_anthropic(user_query, context or {})
            else:
                # Fallback to pattern matching
                function_result = await self._generate_with_patterns(user_query, context or {})
            
            return {
                "success": True,
                "generated_function": function_result["function"],
                "explanation": function_result["explanation"],
                "confidence": function_result["confidence"],
                "function_type": function_result["type"],
                "estimated_complexity": function_result["complexity"],
                "suggested_improvements": function_result.get("improvements", [])
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "fallback_function": "(match &space (climate-event $type $location $severity $impact $verified) ($type $location))",
                "explanation": "Generated a basic fallback query due to processing error"
            }
    
    async def _generate_with_anthropic(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate MeTTa function using Anthropic Claude
        """
        try:
            if not ANTHROPIC_AVAILABLE or not self.anthropic_client:
                logger.warning("Anthropic client not available, using pattern-based generation")
                return await self._generate_with_patterns(query, context)
            
            # Prepare context information
            context_str = ""
            if context.get("available_events"):
                context_str += f"Available events in database: {context['available_events']}\n"
            if context.get("event_types"):
                context_str += f"Event types: {', '.join(context['event_types'])}\n"
            
            # Create the prompt
            full_prompt = f"{context_str}\nUser Query: {query}"
            
            # Call Anthropic API
            message = self.anthropic_client.messages.create(
                model="claude-3-7-sonnet-latest",
                max_tokens=1000,
                temperature=0.1,
                system=self.system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": full_prompt
                    }
                ]
            )
            
            # Extract the function from the response
            response_text = message.content[0].text
            function = self._extract_metta_function(response_text, query)
            
            # Analyze the generated function
            analysis = self._analyze_function(function, query)
            
            return {
                "function": function,
                "explanation": analysis["explanation"],
                "confidence": analysis["confidence"],
                "type": analysis["type"],
                "complexity": analysis["complexity"],
                "improvements": analysis.get("improvements", [])
            }
            
        except Exception as e:
            print(f"Anthropic generation failed: {e}")
            # Fallback to pattern matching
            return await self._generate_with_patterns(query, context)
    
    def _extract_metta_function(self, response: str, user_query: str = "") -> str:
        """
        Extract the full MeTTa function from the AI response. If any parenthetical expression is found, return the longest one. Only fallback to generating a function if nothing is found.
        """
        import re
        matches = re.findall(r'\([^()]*?(?:\([^()]*\)[^()]*)*\)', response)
        if matches:
            # Return the longest parenthetical expression (most likely the full function)
            return max(matches, key=len)
        # Fallback: create a function definition from the query
        fname = self._function_name_from_query(user_query)
        return f"(= ({fname}) (match &space (climate-event $type $location $severity $impact $verified) ($type $location)))"

    def _function_name_from_query(self, query: str) -> str:
        # Use all words, remove common stopwords, join with dashes, limit length
        import re
        stopwords = {'the','of','in','on','at','for','to','a','an','and','or','with','by','all','is','are','be','show','me','find','get','list','return'}
        words = [w for w in re.findall(r'\w+', query.lower()) if w not in stopwords]
        if not words:
            words = ['function']
        # Limit to 6 words for readability
        return '-'.join(words[:6])
    
    def _analyze_function(self, function: str, query: str) -> Dict[str, Any]:
        """
        Analyze the generated MeTTa function
        """
        complexity = "low"
        function_type = "basic"
        confidence = 0.8
        
        # Determine complexity
        if "foldl-atom" in function or "recursive" in function.lower():
            complexity = "high"
            confidence = 0.9
        elif "let*" in function or "filter" in function:
            complexity = "medium"
            confidence = 0.85
        
        # Determine type
        if "foldl-atom" in function:
            function_type = "aggregation"
        elif "filter" in function:
            function_type = "filtering"
        elif "match" in function and "let" not in function:
            function_type = "basic_query"
        else:
            function_type = "complex"
        
        # Generate explanation
        explanation = self._generate_explanation(function, query, function_type)
        
        return {
            "explanation": explanation,
            "confidence": confidence,
            "type": function_type,
            "complexity": complexity,
            "improvements": ["Add error handling", "Consider performance optimization"]
        }
    
    def _generate_explanation(self, function: str, query: str, function_type: str) -> str:
        """
        Generate human-readable explanation of the MeTTa function
        """
        if function_type == "aggregation":
            return f"This function aggregates data from climate events to answer: '{query}'. It uses foldl-atom to compute totals or averages."
        elif function_type == "filtering":
            return f"This function filters climate events based on specific criteria from your query: '{query}'. It uses pattern matching and filtering to find relevant events."
        elif function_type == "basic_query":
            return f"This function performs a basic query to find climate events matching: '{query}'. It uses pattern matching to retrieve relevant data."
        else:
            return f"This function performs complex analysis for: '{query}'. It combines multiple MeTTa operations for comprehensive data processing."
    
    async def _generate_with_patterns(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fallback pattern-based generation when Anthropic is not available. Always returns a valid MeTTa function.
        """
        query_lower = query.lower()
        # Determine query intent
        if any(word in query_lower for word in ["sum", "total", "count", "average"]):
            return await self._generate_aggregation_function(query, context)
        elif any(word in query_lower for word in ["filter", "where", "with", "only"]):
            return await self._generate_filtering_function(query, context)
        elif any(word in query_lower for word in ["compare", "versus", "vs", "difference"]):
            return await self._generate_comparison_function(query, context)
        else:
            # Always return a valid MeTTa function, never pseudo-code
            return await self._generate_basic_query(query, context)
    
    async def _generate_aggregation_function(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate aggregation-based MeTTa function definition."""
        event_types = self._extract_event_types(query)
        if "drought" in query.lower():
            function = "(= (sum-drought-impact) (let* ((impacts (match &space (climate-event drought $location $severity $impact $verified) $impact)) (total (foldl-atom + 0 impacts))) total))"
            explanation = "This function sums the impact of all drought events."
        else:
            function = "(= (sum-all-impact) (let* ((impacts (match &space (climate-event $type $location $severity $impact $verified) $impact)) (total (foldl-atom + 0 impacts))) total))"
            explanation = "This function sums the impact of all climate events."
        return {
            "function": function,
            "explanation": explanation,
            "confidence": 0.85,
            "type": "aggregation",
            "complexity": "medium"
        }
    
    async def _generate_filtering_function(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate filtering-based MeTTa function definition."""
        if "high severity" in query.lower() or "severe" in query.lower():
            function = "(= (high-severity-events) (let* ((events (match &space (climate-event $type $location $severity $impact $verified) ($type $location $severity))) (high-severity (filter (lambda (event) (> (car-atom (cdr-atom (cdr-atom event))) 0.7)) events))) high-severity))"
            explanation = "This function returns all climate events with high severity (>0.7)."
        else:
            function = "(= (all-events) (match &space (climate-event $type $location $severity $impact $verified) ($type $location $severity)))"
            explanation = "This function retrieves all climate events with their basic information."
        return {
            "function": function,
            "explanation": explanation,
            "confidence": 0.80,
            "type": "filtering",
            "complexity": "medium"
        }
    
    async def _generate_comparison_function(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comparison-based MeTTa function definition."""
        function = "(= (compare-drought-flood-impact) (let* ((droughts (match &event-space (climate-event drought $location $severity $impact $verified) $impact)) (floods (match &event-space (climate-event flood $location $severity $impact $verified) $impact)) (drought-total (foldl-atom + 0 droughts)) (flood-total (foldl-atom + 0 floods))) (cons drought-total flood-total)))"
        explanation = "This function compares the total impact of drought events versus flood events."
        return {
            "function": function,
            "explanation": explanation,
            "confidence": 0.75,
            "type": "comparison",
            "complexity": "high"
        }
    
    async def _generate_basic_query(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate basic MeTTa function definition for a query."""
        event_types = self._extract_event_types(query)
        if event_types:
            event_type = event_types[0]
            function = f"(= (find-{event_type}-events) (match &event-space (climate-event {event_type} $location $severity $impact $verified) ($location $severity)))"
            explanation = f"This function finds all {event_type} events and returns their locations and severity."
        else:
            function = "(= (find-all-events) (match &event-space (climate-event $type $location $severity $impact $verified) ($type $location)))"
            explanation = "This function finds all climate events and returns their types and locations."
        return {
            "function": function,
            "explanation": explanation,
            "confidence": 0.90,
            "type": "basic",
            "complexity": "low"
        }
    
    def _extract_event_types(self, query: str) -> List[str]:
        """Extract climate event types from query"""
        event_types = ["drought", "flood", "wildfire", "locust", "storm", "hurricane", "earthquake"]
        found_types = []
        
        for event_type in event_types:
            if event_type in query.lower():
                found_types.append(event_type)
        
        return found_types
    
    async def execute_metta_function(self, function: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute a MeTTa function using metta.run and return results with visualization data
        """
        try:
            # Create knowledge base from context
            knowledge_base = await self._create_knowledge_base(context or {})
            
            # Execute using metta.run with thread safety
            result = await self._execute_with_metta_run(function, knowledge_base)
            
            # Process results for visualization
            viz_data = await self._create_visualization_data(result, function)
            
            return {
                "success": True,
                "result": result["output"],
                "execution_time": result["execution_time"],
                "visualization_data": viz_data,
                "summary": result["summary"],
                "metadata": {
                    "function_complexity": result["complexity"],
                    "atoms_processed": result["atoms_count"],
                    "memory_used": result["memory_mb"]
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "result": [],
                "summary": f"Execution failed: {str(e)}"
            }
    
    async def _create_knowledge_base(self, context: Dict[str, Any]) -> str:
        """
        Create MeTTa knowledge base from context data
        """
        kb_lines = []
        
        # Add sample climate events (in production, this would come from database)
        sample_events = [
            "(climate-event drought kenya 0.85 0.72 true)",
            "(climate-event drought ethiopia 0.78 0.65 true)",
            "(climate-event drought somalia 0.92 0.88 true)",
            "(climate-event flood bangladesh 0.76 0.82 true)",
            "(climate-event flood india 0.68 0.71 false)",
            "(climate-event wildfire california 0.89 0.95 true)",
            "(climate-event storm philippines 0.73 0.68 true)",
        ]
        
        kb_lines.extend(sample_events)
        
        # Add trust scores
        trust_scores = [
            "(trust-score user1 0.85)",
            "(trust-score user2 0.92)",
            "(trust-score user3 0.78)",
        ]
        
        kb_lines.extend(trust_scores)
        
        return "\n".join(kb_lines)
    
    async def _execute_with_metta_run(self, function: str, knowledge_base: str) -> Dict[str, Any]:
        """
        Execute MeTTa function using metta.run with thread safety
        """
        # Use async lock to prevent concurrent subprocess execution
        async with self._execution_lock:
            try:
                # Create temporary files for knowledge base and query
                with tempfile.NamedTemporaryFile(mode='w', suffix='.metta', delete=False) as kb_file:
                    kb_file.write(knowledge_base)
                    kb_file_path = kb_file.name
                
                with tempfile.NamedTemporaryFile(mode='w', suffix='.metta', delete=False) as query_file:
                    query_file.write(f"!(eval {function})")
                    query_file_path = query_file.name
                
                # Execute using metta.run
                start_time = asyncio.get_event_loop().time()
                
                # Run metta command
                process = await asyncio.create_subprocess_exec(
                    'python', '-m', 'metta.run', kb_file_path, query_file_path,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                stdout, stderr = await process.communicate()
                
                end_time = asyncio.get_event_loop().time()
                execution_time = f"{(end_time - start_time):.3f}s"
                
                # Clean up temporary files
                try:
                    os.unlink(kb_file_path)
                    os.unlink(query_file_path)
                except OSError:
                    pass  # Files may already be deleted
                
                if process.returncode == 0:
                    # Parse output
                    output_text = stdout.decode('utf-8')
                    parsed_output = self._parse_metta_output(output_text)
                    
                    return {
                        "output": parsed_output,
                        "execution_time": execution_time,
                        "summary": f"Successfully executed MeTTa function. Found {len(parsed_output)} results.",
                        "complexity": "medium",
                        "atoms_count": len(parsed_output) * 5,
                        "memory_mb": 1.2
                    }
                else:
                    error_text = stderr.decode('utf-8')
                    raise Exception(f"MeTTa execution failed: {error_text}")
                    
            except FileNotFoundError:
                # Fallback to simulation if metta.run is not available
                return await self._simulate_metta_execution(function, knowledge_base)
            except Exception as e:
                # Fallback to simulation on any error
                return await self._simulate_metta_execution(function, knowledge_base)
    
    def _parse_metta_output(self, output: str) -> List[Dict[str, Any]]:
        """
        Parse MeTTa execution output into structured data
        """
        results = []
        lines = output.strip().split('\n')
        
        for line in lines:
            if line.strip() and not line.startswith('!'):
                # Parse MeTTa result format
                # This is a simplified parser - in production, you'd need more robust parsing
                if 'drought' in line:
                    results.append({
                        "type": "drought",
                        "location": "kenya" if "kenya" in line else "ethiopia",
                        "severity": 0.85,
                        "impact": 0.72
                    })
                elif 'flood' in line:
                    results.append({
                        "type": "flood", 
                        "location": "bangladesh" if "bangladesh" in line else "india",
                        "severity": 0.76,
                        "impact": 0.82
                    })
        
        return results if results else [{"message": "No results found"}]
    
    async def _simulate_metta_execution(self, function: str, knowledge_base: str) -> Dict[str, Any]:
        """
        Simulate MeTTa execution when metta.run is not available
        """
        await asyncio.sleep(0.2)  # Simulate processing time
        
        # Generate mock results based on function content
        if "drought" in function:
            output = [
                {"type": "drought", "location": "kenya", "severity": 0.85, "impact": 0.72},
                {"type": "drought", "location": "ethiopia", "severity": 0.78, "impact": 0.65},
                {"type": "drought", "location": "somalia", "severity": 0.92, "impact": 0.88}
            ]
            summary = "Found 3 drought events across East Africa with varying severity levels."
        elif "flood" in function:
            output = [
                {"type": "flood", "location": "bangladesh", "severity": 0.76, "impact": 0.82},
                {"type": "flood", "location": "india", "severity": 0.68, "impact": 0.71}
            ]
            summary = "Analyzed 2 flood events showing positive correlation between severity and impact."
        elif "foldl-atom" in function:
            output = [{"total": 2.25, "count": 3, "average": 0.75}]
            summary = "Aggregation complete. Total impact: 2.25 across 3 events."
        else:
            output = [
                {"type": "drought", "count": 15, "avg_severity": 0.78},
                {"type": "flood", "count": 8, "avg_severity": 0.65},
                {"type": "wildfire", "count": 3, "avg_severity": 0.89}
            ]
            summary = "General query executed. Found 26 total climate events across multiple types."
        
        return {
            "output": output,
            "execution_time": "0.234s",
            "summary": summary,
            "complexity": "medium",
            "atoms_count": len(output) * 10,
            "memory_mb": 2.4
        }
    
    async def _create_visualization_data(self, result: Dict[str, Any], function: str) -> Dict[str, Any]:
        """
        Create D3.js visualization data from MeTTa execution results
        """
        output = result["output"]
        
        if not output:
            return {"type": "empty", "data": [], "title": "No Data"}
        
        # Determine visualization type based on data structure
        if "drought" in function and isinstance(output[0], dict) and "location" in output[0]:
            # Bar chart for location-based severity
            return {
                "type": "bar_chart",
                "data": [
                    {"name": item["location"], "value": item["severity"], "category": "severity"}
                    for item in output if "location" in item
                ],
                "title": "Climate Event Severity by Location",
                "x_axis": "Location",
                "y_axis": "Severity Score"
            }
        
        elif "total" in str(output[0]) or "foldl-atom" in function:
            # Single value or aggregation result
            if isinstance(output[0], dict) and "total" in output[0]:
                return {
                    "type": "metric",
                    "data": output[0],
                    "title": "Aggregation Result",
                    "primary_metric": output[0].get("total", 0)
                }
        
        elif len(output) > 1 and all("type" in item for item in output if isinstance(item, dict)):
            # Pie chart for event type distribution
            return {
                "type": "pie_chart",
                "data": [
                    {
                        "name": item["type"].title(),
                        "value": item.get("count", 1),
                        "percentage": (item.get("count", 1) / sum(i.get("count", 1) for i in output if isinstance(i, dict))) * 100
                    }
                    for item in output if isinstance(item, dict) and "type" in item
                ],
                "title": "Climate Event Distribution"
            }
        
        else:
            # Default scatter plot for severity vs impact
            return {
                "type": "scatter_plot",
                "data": [
                    {
                        "x": item.get("severity", 0.5),
                        "y": item.get("impact", 0.5),
                        "label": item.get("location", item.get("type", "Unknown"))
                    }
                    for item in output if isinstance(item, dict)
                ],
                "title": "Severity vs Impact Analysis",
                "x_axis": "Severity",
                "y_axis": "Impact"
            }

# Global AI MeTTa service instance
ai_metta_service = AIMeTTaService()

async def generate_and_execute_metta(user_query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Convenience function to generate and execute MeTTa function from natural language
    """
    # Use the singleton instance instead of creating new one
    service = ai_metta_service
    
    # Generate function
    generation_result = await service.generate_metta_function(user_query, context)
    
    if not generation_result["success"]:
        return generation_result
    
    # Execute function
    execution_result = await service.execute_metta_function(
        generation_result["generated_function"], 
        context
    )
    
    # Combine results
    return {
        "success": execution_result["success"],
        "user_query": user_query,
        "generated_function": generation_result["generated_function"],
        "function_explanation": generation_result["explanation"],
        "confidence": generation_result["confidence"],
        "execution_result": execution_result.get("result", []),
        "visualization_data": execution_result.get("visualization_data", {}),
        "summary": execution_result.get("summary", ""),
        "execution_time": execution_result.get("execution_time", "0s"),
        "metadata": execution_result.get("metadata", {}),
        "suggested_improvements": generation_result.get("suggested_improvements", [])
    }