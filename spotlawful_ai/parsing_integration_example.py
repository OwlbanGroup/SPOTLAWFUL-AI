from parsing_syntax_grammar_ai import ParsingSyntaxGrammarAI
import numpy as np

def main():
    parser = ParsingSyntaxGrammarAI()

    # Create dummy training data
    # For example, 100 samples, each with 10 features
    x_train = np.random.rand(100, 10)
    # Binary target variable
    y_train = np.random.randint(0, 2, 100)

    # Train the AI model
    print("Training the ParsingSyntaxGrammarAI model...")
    parser.train(x_train, y_train, epochs=5)

    # After training, parse a sample text
    sample_text = "This is an example sentence to parse."
    parse_tree = parser.parse(sample_text)
    parser.display_parse_tree(parse_tree)

if __name__ == "__main__":
    main()
