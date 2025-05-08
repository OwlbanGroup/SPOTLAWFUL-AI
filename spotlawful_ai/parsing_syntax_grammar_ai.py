import spacy
from spacy.tokens import Doc
from spacy.training import Example

class ParsingSyntaxGrammarAI:
    def __init__(self):
        # Load spaCy English model for parsing
        self.nlp = spacy.load("en_core_web_sm")

    def train(self, training_data=None, labels=None, epochs=10):
        """
        Optional training/fine-tuning method.
        training_data: list of tuples (text, annotations) for training
        labels: not used currently, placeholder for compatibility
        epochs: number of training iterations
        """
        if training_data is None:
            print("No training data provided, skipping training.")
            return

        # Enable the parser component for training
        if "parser" not in self.nlp.pipe_names:
            print("Parser component not found in the pipeline.")
            return

        parser = self.nlp.get_pipe("parser")
        optimizer = self.nlp.resume_training()

        for epoch in range(epochs):
            losses = {}
            for text, annotations in training_data:
                doc = self.nlp.make_doc(text)
                example = Example.from_dict(doc, annotations)
                self.nlp.update([example], sgd=optimizer, losses=losses)
            print(f"Epoch {epoch+1}/{epochs} - Losses: {losses}")

    def predict(self, text):
        """
        Predict using spaCy's parsing capabilities.
        """
        try:
            doc = self.nlp(text)
            return doc
        except Exception as e:
            print(f"Error during prediction: {e}")
            return None

    def parse(self, text, hierarchical=False):
        """
        Parse the text and return a detailed parse tree structure.
        If hierarchical=True, returns a nested tree structure.
        """
        try:
            doc = self.nlp(text)
        except Exception as e:
            print(f"Error during parsing: {e}")
            return None

        if not hierarchical:
            parse_tree = []
            for token in doc:
                parse_tree.append({
                    "text": token.text,
                    "lemma": token.lemma_,
                    "pos": token.pos_,
                    "tag": token.tag_,
                    "dep": token.dep_,
                    "head_text": token.head.text,
                    "head_pos": token.head.pos_,
                    "children": [child.text for child in token.children]
                })
            return parse_tree
        else:
            # Build hierarchical parse tree
            def token_to_dict(token):
                return {
                    "text": token.text,
                    "lemma": token.lemma_,
                    "pos": token.pos_,
                    "tag": token.tag_,
                    "dep": token.dep_,
                    "children": [token_to_dict(child) for child in token.children]
                }
            roots = [token for token in doc if token.head == token]
            return [token_to_dict(root) for root in roots]

    def display_parse_tree(self, parse_tree):
        """
        Display the parse tree in a readable format.
        """
        import json
        print("Parse Tree:")
        print(json.dumps(parse_tree, indent=2))

    def named_entities(self, text):
        """
        Extract named entities from the text.
        """
        try:
            doc = self.nlp(text)
            entities = [{"text": ent.text, "label": ent.label_} for ent in doc.ents]
            return entities
        except Exception as e:
            print(f"Error extracting named entities: {e}")
            return None
