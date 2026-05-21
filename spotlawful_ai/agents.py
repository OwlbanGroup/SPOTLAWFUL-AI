from __future__ import annotations

from typing import Any, Dict, List

from spotlawful_ai.agent_protocol import AgentRequest, AgentResponse, BaseAgent
from spotlawful_ai.legal_document_analysis import LegalDocumentAnalysis
from spotlawful_ai.ensemble_ai_model import EnsembleAIModel


class DocumentAnalysisAgent(BaseAgent):
    def __init__(self, ai_parser: Any = None):
        super().__init__("document_analysis")
        self.analyzer = LegalDocumentAnalysis(ai_parser=ai_parser or EnsembleAIModel())

    def handle(self, request: AgentRequest) -> AgentResponse:
        document_text = request.payload.get("document_text", "")
        if not document_text:
            return self.build_response(
                request,
                result={"error": "document_text is required"},
                status="error",
            )

        analysis = self.analyzer.analyze_document(document_text)
        return self.build_response(
            request,
            result={
                "parse_result": analysis["parse_result"],
                "compliance_issues": analysis["compliance_issues"],
            },
        )


class PredictionAgent(BaseAgent):
    def __init__(self, ai_model: Any = None):
        super().__init__("prediction")
        self.ai_model = ai_model or EnsembleAIModel()

    def handle(self, request: AgentRequest) -> AgentResponse:
        case_facts = request.payload.get("case_facts", "")
        historical_data = request.payload.get("historical_data", [])

        if not case_facts:
            return self.build_response(
                request,
                result={"error": "case_facts is required"},
                status="error",
            )

        prediction_score = self._predict_outcome(case_facts, historical_data)
        reasoning = self._build_reasoning(case_facts, historical_data, prediction_score)

        return self.build_response(
            request,
            result={
                "prediction_score": prediction_score,
                "predicted_outcome": "favorable" if prediction_score >= 0.5 else "unfavorable",
                "reasoning": reasoning,
            },
        )

    def _predict_outcome(self, case_facts: str, historical_data: List[Dict[str, Any]]) -> float:
        text_length_score = min(len(case_facts) / 1000.0, 1.0)
        data_signal = min(len(historical_data) / 20.0, 1.0) if historical_data else 0.0
        return round((0.6 * text_length_score) + (0.4 * data_signal), 3)

    def _build_reasoning(
        self,
        case_facts: str,
        historical_data: List[Dict[str, Any]],
        prediction_score: float,
    ) -> List[str]:
        reasoning = [
            f"Case facts length indicates signal strength of {min(len(case_facts) / 1000.0, 1.0):.2f}.",
            f"Historical cases provided: {len(historical_data)}.",
            f"Composite prediction score: {prediction_score:.3f}.",
        ]
        return reasoning


class ResearchAgent(BaseAgent):
    def __init__(self):
        super().__init__("research")

    def handle(self, request: AgentRequest) -> AgentResponse:
        research_topic = request.payload.get("research_topic", "")
        jurisdiction = request.payload.get("jurisdiction", "general")

        if not research_topic:
            return self.build_response(
                request,
                result={"error": "research_topic is required"},
                status="error",
            )

        sources = self._find_sources(research_topic, jurisdiction)
        summary = self._summarize_sources(research_topic, sources)

        return self.build_response(
            request,
            result={
                "research_topic": research_topic,
                "jurisdiction": jurisdiction,
                "sources": sources,
                "summary": summary,
            },
        )

    def _find_sources(self, research_topic: str, jurisdiction: str) -> List[Dict[str, str]]:
        topic_slug = research_topic.lower().replace(" ", "-")
        return [
            {
                "title": f"{research_topic.title()} overview",
                "type": "reference",
                "url": f"https://example.com/research/{jurisdiction}/{topic_slug}",
            },
            {
                "title": f"{research_topic.title()} precedent search",
                "type": "case-law",
                "url": f"https://example.com/cases/{jurisdiction}/{topic_slug}",
            },
        ]

    def _summarize_sources(self, research_topic: str, sources: List[Dict[str, str]]) -> str:
        return f"Found {len(sources)} research sources for {research_topic}."
