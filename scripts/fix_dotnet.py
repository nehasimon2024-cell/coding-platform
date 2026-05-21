import json

# Load the existing dataset
with open('problem_dataset_new.json', 'r') as f:
    data = json.load(f)

# Fixed questions
fixed_questions = {
    "CS-BEG-E-1": {
        "id": "CS-BEG-E-1",
        "title": "Hello World in C#",
        "skill": ".NET, C#",
        "difficulty": "Easy",
        "level": "Beginner",
        "question_type": "coding",
        "tags": ["hello-world", "console", "csharp-basics"],
        "description": "Problem Statement\nWrite a C# program that prints 'Hello, World!' to the console.\n\nInput Format\nNo input required.\n\nOutput Format\nPrint exactly: Hello, World!\n\nExample\nInput:\n(none)\n\nOutput:\nHello, World!",
        "starter_code": {"csharp": "using System;\nclass Program {\n    static void Main() {\n        // Your code here\n    }\n}"},
        "test_cases": [{"input": "", "output": "Hello, World!"}],
        "hidden_test_cases": [{"input": "", "output": "Hello, World!"}],
        "solution": "using System;\nclass Program {\n    static void Main() {\n        Console.WriteLine(\"Hello, World!\");\n    }\n}"
    },
    "CS-BEG-E-2": {
        "id": "CS-BEG-E-2",
        "title": "Reverse a String in C#",
        "skill": ".NET, C#",
        "difficulty": "Easy",
        "level": "Beginner",
        "question_type": "coding",
        "tags": ["string", "array", "csharp-basics"],
        "description": "Problem Statement\nGiven a string, return its reverse.\n\nInput Format\nA single line containing a string s.\n\nOutput Format\nPrint the reversed string.\n\nRules\n- The string may contain spaces and special characters.\n- Empty string should return empty string.\n\nExample\nInput:\nhello\n\nOutput:\nolleh",
        "starter_code": {"csharp": "using System;\nclass Program {\n    static void Main() {\n        string s = Console.ReadLine();\n        // Your code here\n        Console.WriteLine();\n    }\n}"},
        "test_cases": [
            {"input": "hello", "output": "olleh"},
            {"input": "racecar", "output": "racecar"},
            {"input": "Hello World", "output": "dlroW olleH"}
        ],
        "hidden_test_cases": [
            {"input": "", "output": ""},
            {"input": "a", "output": "a"},
            {"input": "abcdef", "output": "fedcba"}
        ],
        "solution": "using System;\nclass Program {\n    static void Main() {\n        string s = Console.ReadLine();\n        char[] arr = s.ToCharArray();\n        Array.Reverse(arr);\n        Console.WriteLine(new string(arr));\n    }\n}"
    },
    "CS-BEG-E-3": {
        "id": "CS-BEG-E-3",
        "title": "Fibonacci Sequence",
        "skill": ".NET, C#",
        "difficulty": "Easy",
        "level": "Beginner",
        "question_type": "coding",
        "tags": ["math", "loop", "csharp-basics"],
        "description": "Problem Statement\nGiven a number n, print the first n numbers of the Fibonacci sequence.\n\nInput Format\nA single integer n.\n\nOutput Format\nPrint the first n Fibonacci numbers separated by spaces on a single line.\n\nRules\n- n will always be a positive integer.\n- Fibonacci sequence starts at 0.\n\nExample\nInput:\n10\n\nOutput:\n0 1 1 2 3 5 8 13 21 34",
        "starter_code": {"csharp": "using System;\nclass Program {\n    static void Main() {\n        int n = int.Parse(Console.ReadLine());\n        // Your code here\n    }\n}"},
        "test_cases": [
            {"input": "10", "output": "0 1 1 2 3 5 8 13 21 34"},
            {"input": "5", "output": "0 1 1 2 3"},
            {"input": "1", "output": "0"}
        ],
        "hidden_test_cases": [
            {"input": "2", "output": "0 1"},
            {"input": "7", "output": "0 1 1 2 3 5 8"},
            {"input": "15", "output": "0 1 1 2 3 5 8 13 21 34 55 89 144 233 377"}
        ],
        "solution": "using System;\nclass Program {\n    static void Main() {\n        int n = int.Parse(Console.ReadLine());\n        int a = 0, b = 1;\n        string[] result = new string[n];\n        for(int i = 0; i < n; i++) {\n            result[i] = a.ToString();\n            int temp = a + b;\n            a = b;\n            b = temp;\n        }\n        Console.WriteLine(string.Join(\" \", result));\n    }\n}"
    },
    "CS-BEG-E-4": {
        "id": "CS-BEG-E-4",
        "title": "Filter Even Numbers with LINQ",
        "skill": ".NET, C#",
        "difficulty": "Easy",
        "level": "Beginner",
        "question_type": "coding",
        "tags": ["linq", "collections", "filtering", "sorting", "csharp-basics"],
        "description": "Problem Statement\nGiven a list of integers, use LINQ to filter only even numbers and print them sorted in ascending order.\n\nInput Format\nFirst line contains n (number of integers).\nNext n lines each contain one integer.\n\nOutput Format\nPrint even numbers separated by spaces in ascending order.\nIf no even numbers exist, print nothing.\n\nExample\nInput:\n5\n5\n2\n8\n1\n4\n\nOutput:\n2 4 8",
        "starter_code": {"csharp": "using System;\nusing System.Linq;\nusing System.Collections.Generic;\nclass Program {\n    static void Main() {\n        int n = int.Parse(Console.ReadLine());\n        List<int> numbers = new List<int>();\n        for(int i = 0; i < n; i++) {\n            numbers.Add(int.Parse(Console.ReadLine()));\n        }\n        // Use LINQ to filter even numbers and sort ascending\n        // Print result separated by spaces\n    }\n}"},
        "test_cases": [
            {"input": "5\n5\n2\n8\n1\n4", "output": "2 4 8"},
            {"input": "3\n1\n3\n5", "output": ""},
            {"input": "4\n10\n3\n6\n2", "output": "2 6 10"}
        ],
        "hidden_test_cases": [
            {"input": "0", "output": ""},
            {"input": "3\n2\n2\n2", "output": "2 2 2"},
            {"input": "5\n100\n1\n50\n3\n20", "output": "20 50 100"}
        ],
        "solution": "using System;\nusing System.Linq;\nusing System.Collections.Generic;\nclass Program {\n    static void Main() {\n        int n = int.Parse(Console.ReadLine());\n        List<int> numbers = new List<int>();\n        for(int i = 0; i < n; i++) {\n            numbers.Add(int.Parse(Console.ReadLine()));\n        }\n        var evens = numbers.Where(x => x % 2 == 0).OrderBy(x => x).ToList();\n        Console.WriteLine(string.Join(\" \", evens));\n    }\n}"
    },
    "CS-BEG-M-1": {
        "id": "CS-BEG-M-1",
        "title": "Class Inheritance and Polymorphism",
        "skill": ".NET, C#",
        "difficulty": "Medium",
        "level": "Beginner",
        "question_type": "coding",
        "tags": ["oop", "inheritance", "polymorphism", "abstract-class", "csharp-basics"],
        "description": "Problem Statement\nYou are given a list of animals. Each animal is either a Dog or a Cat. Print what each animal says.\n\nInput Format\nFirst line contains n (number of animals).\nNext n lines each contain either 'Dog' or 'Cat'.\n\nOutput Format\nFor each animal print what it says — Dog prints 'Woof' and Cat prints 'Meow'.\n\nRules\n- Use inheritance and polymorphism.\n- Create an abstract Animal class with a Speak() method.\n- Dog and Cat must override Speak().\n\nExample\nInput:\n3\nDog\nCat\nDog\n\nOutput:\nWoof\nMeow\nWoof",
        "starter_code": {"csharp": "using System;\nusing System.Collections.Generic;\n\nabstract class Animal {\n    public abstract string Speak();\n}\n\nclass Dog : Animal {\n    // override Speak()\n}\n\nclass Cat : Animal {\n    // override Speak()\n}\n\nclass Program {\n    static void Main() {\n        int n = int.Parse(Console.ReadLine());\n        List<Animal> animals = new List<Animal>();\n        for(int i = 0; i < n; i++) {\n            string type = Console.ReadLine();\n            // Add Dog or Cat to animals list\n        }\n        foreach(var animal in animals) {\n            Console.WriteLine(animal.Speak());\n        }\n    }\n}"},
        "test_cases": [
            {"input": "3\nDog\nCat\nDog", "output": "Woof\nMeow\nWoof"},
            {"input": "2\nCat\nCat", "output": "Meow\nMeow"},
            {"input": "1\nDog", "output": "Woof"}
        ],
        "hidden_test_cases": [
            {"input": "4\nDog\nDog\nCat\nDog", "output": "Woof\nWoof\nMeow\nWoof"},
            {"input": "2\nCat\nDog", "output": "Meow\nWoof"},
            {"input": "1\nCat", "output": "Meow"}
        ],
        "solution": "using System;\nusing System.Collections.Generic;\n\nabstract class Animal {\n    public abstract string Speak();\n}\n\nclass Dog : Animal {\n    public override string Speak() => \"Woof\";\n}\n\nclass Cat : Animal {\n    public override string Speak() => \"Meow\";\n}\n\nclass Program {\n    static void Main() {\n        int n = int.Parse(Console.ReadLine());\n        List<Animal> animals = new List<Animal>();\n        for(int i = 0; i < n; i++) {\n            string type = Console.ReadLine();\n            if(type == \"Dog\") animals.Add(new Dog());\n            else animals.Add(new Cat());\n        }\n        foreach(var animal in animals) {\n            Console.WriteLine(animal.Speak());\n        }\n    }\n}"
    },
    "CS-BEG-M-2": {
        "id": "CS-BEG-M-2",
        "title": "Exception Handling in C#",
        "skill": ".NET, C#",
        "difficulty": "Medium",
        "level": "Beginner",
        "question_type": "coding",
        "tags": ["exception-handling", "try-catch-finally", "csharp-basics"],
        "description": "Problem Statement\nWrite a C# program that reads two integers a and b and prints the result of a divided by b.\nIf b is zero, print -1 instead.\nAlways print 'Division attempt complete.' after the operation.\n\nInput Format\nTwo integers a and b on separate lines.\n\nOutput Format\nFirst line: result of division or -1 if b is zero.\nSecond line: 'Division attempt complete.'\n\nRules\n- Use try/catch/finally.\n- Catch DivideByZeroException specifically.\n- Integer division only.\n\nExample\nInput:\n10\n2\n\nOutput:\n5\nDivision attempt complete.",
        "starter_code": {"csharp": "using System;\nclass Program {\n    static void Main() {\n        int a = int.Parse(Console.ReadLine());\n        int b = int.Parse(Console.ReadLine());\n        // Use try/catch/finally to handle division\n    }\n}"},
        "test_cases": [
            {"input": "10\n2", "output": "5\nDivision attempt complete."},
            {"input": "10\n0", "output": "-1\nDivision attempt complete."},
            {"input": "9\n3", "output": "3\nDivision attempt complete."}
        ],
        "hidden_test_cases": [
            {"input": "0\n5", "output": "0\nDivision attempt complete."},
            {"input": "-10\n2", "output": "-5\nDivision attempt complete."},
            {"input": "7\n0", "output": "-1\nDivision attempt complete."}
        ],
        "solution": "using System;\nclass Program {\n    static void Main() {\n        int a = int.Parse(Console.ReadLine());\n        int b = int.Parse(Console.ReadLine());\n        try {\n            Console.WriteLine(a / b);\n        } catch(DivideByZeroException) {\n            Console.WriteLine(-1);\n        } finally {\n            Console.WriteLine(\"Division attempt complete.\");\n        }\n    }\n}"
    },
    "CS-BEG-H-1": {
        "id": "CS-BEG-H-1",
        "title": "Generic Repository Pattern",
        "skill": ".NET, C#",
        "difficulty": "Hard",
        "level": "Beginner",
        "question_type": "coding",
        "tags": ["generics", "repository-pattern", "design-patterns", "csharp-intermediate"],
        "description": "Problem Statement\nImplement a simple in-memory repository using generics.\nYou will receive a series of commands and must execute them.\n\nCommands:\n- ADD id value: add item with given id\n- GET id: print item with given id, or 'null' if not found\n- DELETE id: remove item with given id\n- GETALL: print all values separated by spaces, or 'empty' if none\n\nInput Format\nFirst line contains n (number of commands).\nNext n lines each contain a command.\n\nOutput Format\nPrint output for GET and GETALL commands only.\n\nExample\nInput:\n4\nADD 1 Alice\nGET 1\nDELETE 1\nGET 1\n\nOutput:\nAlice\nnull",
        "starter_code": {"csharp": "using System;\nusing System.Collections.Generic;\n\npublic interface IRepository<T> where T : class {\n    T GetById(int id);\n    IEnumerable<T> GetAll();\n    void Add(int id, T entity);\n    void Delete(int id);\n}\n\npublic class InMemoryRepository<T> : IRepository<T> where T : class {\n    // Implement using Dictionary\n}\n\nclass Program {\n    static void Main() {\n        int n = int.Parse(Console.ReadLine());\n        var repo = new InMemoryRepository<string>();\n        for(int i = 0; i < n; i++) {\n            string[] parts = Console.ReadLine().Split(' ', 3);\n            // Handle ADD, GET, DELETE, GETALL commands\n        }\n    }\n}"},
        "test_cases": [
            {"input": "4\nADD 1 Alice\nGET 1\nDELETE 1\nGET 1", "output": "Alice\nnull"},
            {"input": "3\nADD 1 Alice\nADD 2 Bob\nGETALL", "output": "Alice Bob"},
            {"input": "1\nGETALL", "output": "empty"}
        ],
        "hidden_test_cases": [
            {"input": "5\nADD 1 Alice\nADD 2 Bob\nDELETE 1\nGETALL\nGET 1", "output": "Bob\nnull"},
            {"input": "3\nADD 1 X\nADD 1 Y\nGET 1", "output": "Y"},
            {"input": "2\nADD 1 Alice\nGET 2", "output": "null"}
        ],
        "solution": "using System;\nusing System.Collections.Generic;\nusing System.Linq;\n\npublic interface IRepository<T> where T : class {\n    T GetById(int id);\n    IEnumerable<T> GetAll();\n    void Add(int id, T entity);\n    void Delete(int id);\n}\n\npublic class InMemoryRepository<T> : IRepository<T> where T : class {\n    private Dictionary<int, T> _store = new Dictionary<int, T>();\n    public T GetById(int id) => _store.TryGetValue(id, out var v) ? v : null;\n    public IEnumerable<T> GetAll() => _store.Values;\n    public void Add(int id, T entity) => _store[id] = entity;\n    public void Delete(int id) => _store.Remove(id);\n}\n\nclass Program {\n    static void Main() {\n        int n = int.Parse(Console.ReadLine());\n        var repo = new InMemoryRepository<string>();\n        for(int i = 0; i < n; i++) {\n            string[] parts = Console.ReadLine().Split(' ', 3);\n            if(parts[0] == \"ADD\") repo.Add(int.Parse(parts[1]), parts[2]);\n            else if(parts[0] == \"GET\") Console.WriteLine(repo.GetById(int.Parse(parts[1])) ?? \"null\");\n            else if(parts[0] == \"DELETE\") repo.Delete(int.Parse(parts[1]));\n            else if(parts[0] == \"GETALL\") {\n                var all = repo.GetAll().ToList();\n                Console.WriteLine(all.Count == 0 ? \"empty\" : string.Join(\" \", all));\n            }\n        }\n    }\n}"
    }
}

# Update the questions in the dataset
for skill in data['skills']:
    if skill['skill'] == '.NET, C#':
        for level_name, difficulties in skill['levels'].items():
            for difficulty, problems in difficulties.items():
                for i, problem in enumerate(problems):
                    if problem['id'] in fixed_questions:
                        problems[i] = fixed_questions[problem['id']]
                        print(f"Fixed: {problem['id']} - {problem['title']}")

# Save the updated dataset
with open('problem_dataset_new.json', 'w') as f:
    json.dump(data, f, indent=2)

print("\nDone! JSON file updated successfully.")