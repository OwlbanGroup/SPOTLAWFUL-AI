class UserEducation:
    def __init__(self):
        self.documentation = []
        self.tutorials = []
        self.training_programs = []

    def add_documentation(self, doc):
        self.documentation.append(doc)
        print(f"Added documentation: {doc}")

    def add_tutorial(self, tutorial):
        self.tutorials.append(tutorial)
        print(f"Added tutorial: {tutorial}")

    def add_training_program(self, program):
        self.training_programs.append(program)
        print(f"Added training program: {program}")

    def list_resources(self):
        return {
            "documentation": self.documentation,
            "tutorials": self.tutorials,
            "training_programs": self.training_programs
        }

    def provide_support(self):
        print("Providing ongoing support and knowledge base resources.")
