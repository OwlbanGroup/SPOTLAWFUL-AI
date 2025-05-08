from parsing_syntax_grammar_ai import ParsingSyntaxGrammarAI

def main():
    parser = ParsingSyntaxGrammarAI()

    # Example training data for fine-tuning (optional)
    # Format: (text, annotations) where annotations include heads and deps for tokens
    # Corrected heads and deps lengths to match token count
    training_data = [
        ("This is a sentence.", {"heads": [1, 1, 3, 1, 1], "deps": ["nsubj", "ROOT", "det", "attr", "punct"]}),
        ("Another example sentence.", {"heads": [1, 2, 2, 2], "deps": ["det", "amod", "ROOT", "punct"]})
    ]

    # Train the AI model with example data
    print("Training the ParsingSyntaxGrammarAI model with example data...")
    parser.train(training_data=training_data, epochs=3)

    # After training, parse a sample text with flat parse tree
    sample_text = "This is an example sentence to parse."
    print("Parsing with flat parse tree:")
    parse_tree = parser.parse(sample_text, hierarchical=False)
    parser.display_parse_tree(parse_tree)

    # Parse the same text with hierarchical parse tree
    print("Parsing with hierarchical parse tree:")
    hierarchical_tree = parser.parse(sample_text, hierarchical=True)
    parser.display_parse_tree(hierarchical_tree)

    # Extract named entities
    print("Named entities in the sample text:")
    entities = parser.named_entities(sample_text)
    print(entities)

if __name__ == "__main__":
    main()
