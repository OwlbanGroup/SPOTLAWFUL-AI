import os

class LegalDocumentAnalysis:
    def __init__(self, ai_parser):
        self.ai_parser = ai_parser

    def analyze_document(self, document_text):
        # Use AI parser to analyze the document text
        parse_result = self.ai_parser.parse(document_text, hierarchical=True)
        # Perform compliance checks (placeholder for actual rules)
        compliance_issues = self.check_compliance(parse_result)
        return {
            'parse_result': parse_result,
            'compliance_issues': compliance_issues
        }

    def check_compliance(self, parse_result):
        # Placeholder for compliance checking logic
        # For example, check for required clauses, forbidden terms, etc.
        issues = []
        # Example check: ensure "termination clause" exists
        if not self.contains_clause(parse_result, "termination"):
            issues.append("Missing termination clause.")
        return issues

    def contains_clause(self, parse_result, clause_keyword):
        # Simple keyword search in parse result text
        # In real implementation, use semantic search or pattern matching
        text = self.flatten_parse_text(parse_result)
        return clause_keyword.lower() in text.lower()

    def flatten_parse_text(self, parse_result):
        # Recursively extract text from parse tree
        texts = []
        for node in parse_result:
            texts.append(node.get('text', ''))
            if 'children' in node and node['children']:
                texts.append(self.flatten_parse_text(node['children']))
        return ' '.join(texts)

# Example usage:
# from parsing_syntax_grammar_ai import ParsingSyntaxGrammarAI
# ai_parser = ParsingSyntaxGrammarAI()
# analyzer = LegalDocumentAnalysis(ai_parser)
# document_text = "Sample contract text ..."
# result = analyzer.analyze_document(document_text)
# print(result)
