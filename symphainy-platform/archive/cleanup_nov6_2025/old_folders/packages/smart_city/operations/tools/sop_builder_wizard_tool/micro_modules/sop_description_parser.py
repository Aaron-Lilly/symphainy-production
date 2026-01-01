"""
SOP Description Parser Micro-Module
Smart City Native + Micro-Modular Architecture
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import re


class SOPDescriptionParser:
    """
    SOP Description Parser following Smart City patterns.
    Handles parsing of free-form descriptions into SOP structures.
    """
    
    def __init__(self, logger, config):
        self.logger = logger
        self.config = config
        self.logger.info("SOPDescriptionParser micro-module initialized")
    
    async def description_to_sop(
        self, 
        user_input: str, 
        session_token: Optional[str]
    ) -> Dict[str, Any]:
        """Convert description to SOP structure."""
        try:
            # Parse the description to extract steps
            steps = await self._parse_description_to_steps(user_input)
            
            # Create SOP structure
            sop = {
                "title": await self._extract_title(user_input),
                "description": user_input,
                "steps": steps,
                "created_by": None,
                "created_at": datetime.utcnow().isoformat(),
                "version": "1.0.0",
                "metadata": {
                    "generated_from_description": True,
                    "session_token": session_token,
                    "parsing_method": "description_parser"
                }
            }
            
            return sop
            
        except Exception as e:
            self.logger.error(f"Error parsing description to SOP: {e}")
            return {
                "title": "Error Generating SOP",
                "description": "Failed to generate SOP from description",
                "steps": [],
                "created_at": datetime.utcnow().isoformat(),
                "version": "1.0.0",
                "metadata": {"error": str(e), "session_token": session_token}
            }
    
    async def _parse_description_to_steps(self, description: str) -> List[Dict[str, Any]]:
        """Parse description into individual steps."""
        try:
            steps = []
            
            # Split by common step indicators
            step_patterns = [
                r'\d+\.\s*([^\.]+\.)',  # "1. Step description."
                r'Step\s+\d+:\s*([^\.]+\.)',  # "Step 1: Step description."
                r'-\s*([^\.]+\.)',  # "- Step description."
                r'\*\s*([^\.]+\.)',  # "* Step description."
            ]
            
            # Try each pattern
            for pattern in step_patterns:
                matches = re.findall(pattern, description, re.IGNORECASE)
                if matches:
                    for i, match in enumerate(matches):
                        step_text = match.strip()
                        if len(step_text) > 5:  # Only include substantial steps
                            steps.append({
                                "step_number": i + 1,
                                "title": f"Step {i + 1}",
                                "description": step_text,
                                "responsible_role": await self._infer_responsible_role(step_text),
                                "expected_output": await self._infer_expected_output(step_text),
                                "created_at": datetime.utcnow().isoformat(),
                                "metadata": {"parsed_from_description": True}
                            })
                    break
            
            # If no structured steps found, try to split by sentences
            if not steps:
                sentences = re.split(r'[.!?]+', description)
                for i, sentence in enumerate(sentences):
                    sentence = sentence.strip()
                    if len(sentence) > 10:  # Only include substantial sentences
                        steps.append({
                            "step_number": i + 1,
                            "title": f"Step {i + 1}",
                            "description": sentence,
                            "responsible_role": await self._infer_responsible_role(sentence),
                            "expected_output": await self._infer_expected_output(sentence),
                            "created_at": datetime.utcnow().isoformat(),
                            "metadata": {"parsed_from_description": True}
                        })
            
            # If still no steps, create a single step from the whole description
            if not steps:
                steps.append({
                    "step_number": 1,
                    "title": "Main Process",
                    "description": description,
                    "responsible_role": await self._infer_responsible_role(description),
                    "expected_output": await self._infer_expected_output(description),
                    "created_at": datetime.utcnow().isoformat(),
                    "metadata": {"parsed_from_description": True}
                })
            
            return steps
            
        except Exception as e:
            self.logger.error(f"Error parsing description to steps: {e}")
            return []
    
    async def _extract_title(self, description: str) -> str:
        """Extract title from description."""
        try:
            # Try to find a title pattern
            title_patterns = [
                r'Title:\s*([^\n]+)',
                r'Subject:\s*([^\n]+)',
                r'Process:\s*([^\n]+)',
                r'Procedure:\s*([^\n]+)',
            ]
            
            for pattern in title_patterns:
                match = re.search(pattern, description, re.IGNORECASE)
                if match:
                    return match.group(1).strip()
            
            # If no explicit title, use first sentence
            first_sentence = description.split('.')[0].strip()
            if len(first_sentence) > 50:
                first_sentence = first_sentence[:50] + "..."
            
            return first_sentence or "Generated SOP"
            
        except Exception as e:
            self.logger.error(f"Error extracting title: {e}")
            return "Generated SOP"
    
    async def _infer_responsible_role(self, step_text: str) -> Optional[str]:
        """Infer responsible role from step text."""
        try:
            step_lower = step_text.lower()
            
            # AI/Automation keywords
            if any(word in step_lower for word in ["ai", "automate", "extract", "screen", "classify", "analyze", "process"]):
                return "AI"
            
            # Human keywords
            elif any(word in step_lower for word in ["review", "approve", "human", "sign", "validate", "check", "verify"]):
                return "Human"
            
            # Handoff keywords
            elif any(word in step_lower for word in ["handoff", "transfer", "pass", "send", "forward"]):
                return "Handoff"
            
            # Manager keywords
            elif any(word in step_lower for word in ["manager", "supervisor", "lead", "director"]):
                return "Manager"
            
            # Admin keywords
            elif any(word in step_lower for word in ["admin", "administrator", "system", "technical"]):
                return "Administrator"
            
            else:
                return None
                
        except Exception as e:
            self.logger.error(f"Error inferring responsible role: {e}")
            return None
    
    async def _infer_expected_output(self, step_text: str) -> Optional[str]:
        """Infer expected output from step text."""
        try:
            step_lower = step_text.lower()
            
            # Look for output indicators
            output_patterns = [
                r'output:\s*([^\.]+)',
                r'result:\s*([^\.]+)',
                r'produce:\s*([^\.]+)',
                r'generate:\s*([^\.]+)',
                r'create:\s*([^\.]+)',
            ]
            
            for pattern in output_patterns:
                match = re.search(pattern, step_text, re.IGNORECASE)
                if match:
                    return match.group(1).strip()
            
            # Infer from action words
            if any(word in step_lower for word in ["create", "generate", "produce", "build", "make"]):
                return "Generated content or document"
            elif any(word in step_lower for word in ["review", "check", "validate", "verify"]):
                return "Approval or validation result"
            elif any(word in step_lower for word in ["extract", "analyze", "process"]):
                return "Processed data or analysis"
            elif any(word in step_lower for word in ["send", "forward", "transmit"]):
                return "Transmitted message or document"
            else:
                return None
                
        except Exception as e:
            self.logger.error(f"Error inferring expected output: {e}")
            return None
    
    async def get_parsing_statistics(
        self, 
        description: str, 
        sop: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get parsing statistics."""
        try:
            steps = sop.get("steps", [])
            
            return {
                "original_description_length": len(description),
                "extracted_steps_count": len(steps),
                "steps_with_roles": sum(1 for step in steps if step.get("responsible_role")),
                "steps_with_outputs": sum(1 for step in steps if step.get("expected_output")),
                "parsing_confidence": min(100, len(steps) * 20),  # Simple confidence metric
                "parsing_method": "description_parser"
            }
            
        except Exception as e:
            self.logger.error(f"Error getting parsing statistics: {e}")
            return {"error": str(e)}
    
    async def get_parsing_recommendations(
        self, 
        description: str, 
        sop: Dict[str, Any]
    ) -> List[str]:
        """Get parsing recommendations."""
        try:
            recommendations = []
            steps = sop.get("steps", [])
            
            if len(steps) == 0:
                recommendations.append("No steps could be extracted. Try using numbered lists or bullet points.")
            elif len(steps) == 1:
                recommendations.append("Only one step was extracted. Consider breaking down the process into smaller steps.")
            elif len(steps) > 10:
                recommendations.append("Many steps were extracted. Consider grouping related steps together.")
            
            steps_without_roles = sum(1 for step in steps if not step.get("responsible_role"))
            if steps_without_roles > 0:
                recommendations.append(f"{steps_without_roles} steps don't have assigned roles. Consider specifying who should perform each step.")
            
            steps_without_outputs = sum(1 for step in steps if not step.get("expected_output"))
            if steps_without_outputs > 0:
                recommendations.append(f"{steps_without_outputs} steps don't have expected outputs. Consider specifying what each step should produce.")
            
            if not recommendations:
                recommendations.append("Parsing completed successfully. Review the generated steps and make adjustments as needed.")
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Error getting parsing recommendations: {e}")
            return [f"Error generating recommendations: {str(e)}"]

