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
    },
"CS-INT1-M-1": {
        "id": "CS-INT1-M-1",
        "title": "Delegates and Events",
        "skill": ".NET, C#",
        "difficulty": "Medium",
        "level": "Intermediate_1",
        "question_type": "coding",
        "tags": ["events", "delegates", "event-handler", "csharp-intermediate"],
        "description": "Problem Statement\nYou are building a simple event system. Given a number of button clicks, print a message for each handler that responds to the click.\n\nEach button has two handlers:\n- Handler 1 always prints: 'Handler 1 called'\n- Handler 2 always prints: 'Handler 2 called'\n\nInput Format\nFirst line contains n (number of clicks).\n\nOutput Format\nFor each click, print:\nHandler 1 called\nHandler 2 called\n\nExample\nInput:\n2\n\nOutput:\nHandler 1 called\nHandler 2 called\nHandler 1 called\nHandler 2 called",
        "starter_code": {"csharp": "using System;\n\npublic class Button {\n    public event EventHandler Click;\n    public void OnClick() {\n        // Raise Click event here\n    }\n}\n\nclass Program {\n    static void Main() {\n        int n = int.Parse(Console.ReadLine());\n        var btn = new Button();\n        // Subscribe two handlers to btn.Click\n        // Handler 1 prints: Handler 1 called\n        // Handler 2 prints: Handler 2 called\n        for(int i = 0; i < n; i++) {\n            btn.OnClick();\n        }\n    }\n}"},
        "test_cases": [
            {"input": "1", "output": "Handler 1 called\nHandler 2 called"},
            {"input": "2", "output": "Handler 1 called\nHandler 2 called\nHandler 1 called\nHandler 2 called"},
            {"input": "3", "output": "Handler 1 called\nHandler 2 called\nHandler 1 called\nHandler 2 called\nHandler 1 called\nHandler 2 called"}
        ],
        "hidden_test_cases": [
            {"input": "0", "output": ""},
            {"input": "4", "output": "Handler 1 called\nHandler 2 called\nHandler 1 called\nHandler 2 called\nHandler 1 called\nHandler 2 called\nHandler 1 called\nHandler 2 called"}
        ],
        "solution": "using System;\n\npublic class Button {\n    public event EventHandler Click;\n    public void OnClick() {\n        Click?.Invoke(this, EventArgs.Empty);\n    }\n}\n\nclass Program {\n    static void Main() {\n        int n = int.Parse(Console.ReadLine());\n        var btn = new Button();\n        btn.Click += (s, e) => Console.WriteLine(\"Handler 1 called\");\n        btn.Click += (s, e) => Console.WriteLine(\"Handler 2 called\");\n        for(int i = 0; i < n; i++) {\n            btn.OnClick();\n        }\n    }\n}"
    },
    "CS-INT1-M-2": {
        "id": "CS-INT1-M-2",
        "title": "LINQ Join and GroupBy",
        "skill": ".NET, C#",
        "difficulty": "Medium",
        "level": "Intermediate_1",
        "question_type": "coding",
        "tags": ["linq", "join", "group-by", "aggregation", "csharp-intermediate"],
        "description": "Problem Statement\nYou are given a list of customers and orders. Join them and print the total amount spent by each customer in ascending order of customer name.\n\nInput Format\nFirst line: number of customers c\nNext c lines: customer id and name separated by space\nNext line: number of orders o\nNext o lines: customer id and order amount separated by space\n\nOutput Format\nFor each customer who has orders, print:\ncustomer_name total_spent\nSorted alphabetically by customer name.\n\nExample\nInput:\n2\n1 Alice\n2 Bob\n3\n1 50\n1 30\n2 100\n\nOutput:\nAlice 80\nBob 100",
        "starter_code": {"csharp": "using System;\nusing System.Linq;\nusing System.Collections.Generic;\n\nclass Program {\n    static void Main() {\n        int c = int.Parse(Console.ReadLine());\n        var customers = new Dictionary<int, string>();\n        for(int i = 0; i < c; i++) {\n            var parts = Console.ReadLine().Split(' ');\n            customers[int.Parse(parts[0])] = parts[1];\n        }\n        int o = int.Parse(Console.ReadLine());\n        var orders = new List<(int customerId, int amount)>();\n        for(int i = 0; i < o; i++) {\n            var parts = Console.ReadLine().Split(' ');\n            orders.Add((int.Parse(parts[0]), int.Parse(parts[1])));\n        }\n        // Use LINQ to join and group by customer name\n        // Print customer name and total spent sorted alphabetically\n    }\n}"},
        "test_cases": [
            {"input": "2\n1 Alice\n2 Bob\n3\n1 50\n1 30\n2 100", "output": "Alice 80\nBob 100"},
            {"input": "2\n1 Alice\n2 Bob\n2\n2 200\n2 50", "output": "Bob 250"},
            {"input": "3\n1 Alice\n2 Bob\n3 Charlie\n4\n1 100\n3 50\n1 25\n3 75", "output": "Alice 125\nCharlie 125"}
        ],
        "hidden_test_cases": [
            {"input": "2\n1 Alice\n2 Bob\n0", "output": ""},
            {"input": "3\n1 Alice\n2 Bob\n3 Charlie\n3\n1 500\n2 300\n3 100", "output": "Alice 500\nBob 300\nCharlie 100"},
            {"input": "2\n1 Alice\n2 Bob\n3\n1 10\n1 20\n1 30", "output": "Alice 60"}
        ],
        "solution": "using System;\nusing System.Linq;\nusing System.Collections.Generic;\n\nclass Program {\n    static void Main() {\n        int c = int.Parse(Console.ReadLine());\n        var customers = new Dictionary<int, string>();\n        for(int i = 0; i < c; i++) {\n            var parts = Console.ReadLine().Split(' ');\n            customers[int.Parse(parts[0])] = parts[1];\n        }\n        int o = int.Parse(Console.ReadLine());\n        var orders = new List<(int customerId, int amount)>();\n        for(int i = 0; i < o; i++) {\n            var parts = Console.ReadLine().Split(' ');\n            orders.Add((int.Parse(parts[0]), int.Parse(parts[1])));\n        }\n        var result = orders\n            .Where(ord => customers.ContainsKey(ord.customerId))\n            .GroupBy(ord => customers[ord.customerId])\n            .Select(g => new { Name = g.Key, Total = g.Sum(x => x.amount) })\n            .OrderBy(x => x.Name);\n        foreach(var r in result) {\n            Console.WriteLine($\"{r.Name} {r.Total}\");\n        }\n    }\n}"
    },

"CS-INT1-E-1": {
        "id": "CS-INT1-E-1",
        "title": "Async/Await Task Processing",
        "skill": ".NET, C#",
        "difficulty": "Easy",
        "level": "Intermediate_1",
        "question_type": "coding",
        "tags": ["async-await", "tasks", "csharp-intermediate"],
        "description": "Problem Statement\nWrite a C# program that simulates async task processing. Given n tasks each with a name and a result value, process them asynchronously and print each result in the format 'Task {name} completed with result: {value}'.\n\nInput Format\nFirst line: number of tasks n\nNext n lines: task name and result value separated by space\n\nOutput Format\nFor each task print:\nTask {name} completed with result: {value}\n\nRules\n- Use async/await and Task.Run to process each task\n- Print results in the order they are received\n\nExample\nInput:\n3\nFetch 42\nCompute 100\nLoad 7\n\nOutput:\nTask Fetch completed with result: 42\nTask Compute completed with result: 100\nTask Load completed with result: 7",
        "starter_code": {"csharp": "using System;\nusing System.Threading.Tasks;\n\nclass Program {\n    static async Task<string> ProcessTask(string name, int value) {\n        return await Task.Run(() => \"\");\n    }\n\n    static async Task Main() {\n        int n = int.Parse(Console.ReadLine());\n        for(int i = 0; i < n; i++) {\n            var parts = Console.ReadLine().Split(' ');\n            string name = parts[0];\n            int value = int.Parse(parts[1]);\n            // Call ProcessTask and print result\n        }\n    }\n}"},
        "test_cases": [
            {"input": "3\nFetch 42\nCompute 100\nLoad 7", "output": "Task Fetch completed with result: 42\nTask Compute completed with result: 100\nTask Load completed with result: 7"},
            {"input": "1\nDownload 99", "output": "Task Download completed with result: 99"},
            {"input": "2\nRead 10\nWrite 20", "output": "Task Read completed with result: 10\nTask Write completed with result: 20"}
        ],
        "hidden_test_cases": [
            {"input": "1\nPing 0", "output": "Task Ping completed with result: 0"},
            {"input": "3\nA 1\nB 2\nC 3", "output": "Task A completed with result: 1\nTask B completed with result: 2\nTask C completed with result: 3"},
            {"input": "2\nSync 500\nAsync 250", "output": "Task Sync completed with result: 500\nTask Async completed with result: 250"}
        ],
        "solution": "using System;\nusing System.Threading.Tasks;\n\nclass Program {\n    static async Task<string> ProcessTask(string name, int value) {\n        return await Task.Run(() => $\"Task {name} completed with result: {value}\");\n    }\n\n    static async Task Main() {\n        int n = int.Parse(Console.ReadLine());\n        for(int i = 0; i < n; i++) {\n            var parts = Console.ReadLine().Split(' ');\n            string name = parts[0];\n            int value = int.Parse(parts[1]);\n            string result = await ProcessTask(name, value);\n            Console.WriteLine(result);\n        }\n    }\n}"
    },
    "CS-INT1-M-3": {
        "id": "CS-INT1-M-3",
        "title": "Dependency Injection with IServiceCollection",
        "skill": ".NET, C#",
        "difficulty": "Medium",
        "level": "Intermediate_1",
        "question_type": "coding",
        "tags": ["dependency-injection", "ioc", "interfaces", "csharp-intermediate"],
        "description": "Problem Statement\nImplement a simple dependency injection pattern manually without any framework. Given a list of email send commands, use an interface and its implementation to send emails and print confirmation messages.\n\nInput Format\nFirst line: number of emails n\nNext n lines: recipient and message separated by comma\n\nOutput Format\nFor each email print:\nEmail sent to {recipient}: {message}\n\nRules\n- Define an IEmailService interface with a Send method\n- Implement it with EmailService class\n- Use the interface reference to call Send (demonstrating DI principle)\n\nExample\nInput:\n2\nuser@example.com,Hello\nadmin@example.com,Welcome\n\nOutput:\nEmail sent to user@example.com: Hello\nEmail sent to admin@example.com: Welcome",
        "starter_code": {"csharp": "using System;\n\npublic interface IEmailService {\n    void Send(string recipient, string message);\n}\n\npublic class EmailService : IEmailService {\n    // Implement Send method\n    // Print: Email sent to {recipient}: {message}\n}\n\nclass Program {\n    static void Main() {\n        int n = int.Parse(Console.ReadLine());\n        IEmailService emailService = new EmailService();\n        for(int i = 0; i < n; i++) {\n            var parts = Console.ReadLine().Split(',');\n            // Call emailService.Send\n        }\n    }\n}"},
        "test_cases": [
            {"input": "2\nuser@example.com,Hello\nadmin@example.com,Welcome", "output": "Email sent to user@example.com: Hello\nEmail sent to admin@example.com: Welcome"},
            {"input": "1\ntest@test.com,Test message", "output": "Email sent to test@test.com: Test message"},
            {"input": "3\na@a.com,Hi\nb@b.com,Bye\nc@c.com,Hello", "output": "Email sent to a@a.com: Hi\nEmail sent to b@b.com: Bye\nEmail sent to c@c.com: Hello"}
        ],
        "hidden_test_cases": [
            {"input": "1\nneha@company.com,Welcome aboard", "output": "Email sent to neha@company.com: Welcome aboard"},
            {"input": "2\nx@x.com,Message 1\ny@y.com,Message 2", "output": "Email sent to x@x.com: Message 1\nEmail sent to y@y.com: Message 2"},
            {"input": "3\none@one.com,First\ntwo@two.com,Second\nthree@three.com,Third", "output": "Email sent to one@one.com: First\nEmail sent to two@two.com: Second\nEmail sent to three@three.com: Third"}
        ],
        "solution": "using System;\n\npublic interface IEmailService {\n    void Send(string recipient, string message);\n}\n\npublic class EmailService : IEmailService {\n    public void Send(string recipient, string message) {\n        Console.WriteLine($\"Email sent to {recipient}: {message}\");\n    }\n}\n\nclass Program {\n    static void Main() {\n        int n = int.Parse(Console.ReadLine());\n        IEmailService emailService = new EmailService();\n        for(int i = 0; i < n; i++) {\n            var parts = Console.ReadLine().Split(',');\n            emailService.Send(parts[0], parts[1]);\n        }\n    }\n}"
    },
    "CS-INT1-H-1": {
        "id": "CS-INT1-H-1",
        "title": "Middleware Pipeline Pattern",
        "skill": ".NET, C#",
        "difficulty": "Hard",
        "level": "Intermediate_1",
        "question_type": "coding",
        "tags": ["middleware", "pipeline", "logging", "csharp-intermediate"],
        "description": "Problem Statement\nSimulate a middleware pipeline in C#. Given a list of HTTP requests in the format 'METHOD /path STATUS', pass each through a logging middleware that prints the request and response details.\n\nInput Format\nFirst line: number of requests n\nNext n lines: METHOD /path STATUS (e.g. GET /api/users 200)\n\nOutput Format\nFor each request print:\n{METHOD} {path}\nResponse: {STATUS}\n\nRules\n- Implement a middleware class with an Invoke method\n- Middleware must log the request before passing to next, and log response after\n- Use a delegate to represent the next middleware\n\nExample\nInput:\n2\nGET /api/users 200\nPOST /api/items 201\n\nOutput:\nGET /api/users\nResponse: 200\nPOST /api/items\nResponse: 201",
        "starter_code": {"csharp": "using System;\nusing System.Threading.Tasks;\n\npublic class RequestContext {\n    public string Method { get; set; }\n    public string Path { get; set; }\n    public int StatusCode { get; set; }\n}\n\npublic class LoggingMiddleware {\n    private readonly Func<RequestContext, Task> _next;\n    public LoggingMiddleware(Func<RequestContext, Task> next) {\n        _next = next;\n    }\n    public async Task Invoke(RequestContext ctx) {\n        // Log request: print \"{Method} {Path}\"\n        // Call _next\n        // Log response: print \"Response: {StatusCode}\"\n    }\n}\n\nclass Program {\n    static async Task Main() {\n        int n = int.Parse(Console.ReadLine());\n        var middleware = new LoggingMiddleware(async ctx => await Task.CompletedTask);\n        for(int i = 0; i < n; i++) {\n            var parts = Console.ReadLine().Split(' ');\n            var ctx = new RequestContext {\n                Method = parts[0],\n                Path = parts[1],\n                StatusCode = int.Parse(parts[2])\n            };\n            await middleware.Invoke(ctx);\n        }\n    }\n}"},
        "test_cases": [
            {"input": "2\nGET /api/users 200\nPOST /api/items 201", "output": "GET /api/users\nResponse: 200\nPOST /api/items\nResponse: 201"},
            {"input": "1\nDELETE /api/user/1 204", "output": "DELETE /api/user/1\nResponse: 204"},
            {"input": "3\nGET / 200\nPOST /login 200\nGET /dashboard 403", "output": "GET /\nResponse: 200\nPOST /login\nResponse: 200\nGET /dashboard\nResponse: 403"}
        ],
        "hidden_test_cases": [
            {"input": "1\nGET /health 200", "output": "GET /health\nResponse: 200"},
            {"input": "2\nPUT /api/user/1 200\nDELETE /api/user/2 404", "output": "PUT /api/user/1\nResponse: 200\nDELETE /api/user/2\nResponse: 404"},
            {"input": "3\nGET /a 200\nGET /b 404\nPOST /c 500", "output": "GET /a\nResponse: 200\nGET /b\nResponse: 404\nPOST /c\nResponse: 500"}
        ],
        "solution": "using System;\nusing System.Threading.Tasks;\n\npublic class RequestContext {\n    public string Method { get; set; }\n    public string Path { get; set; }\n    public int StatusCode { get; set; }\n}\n\npublic class LoggingMiddleware {\n    private readonly Func<RequestContext, Task> _next;\n    public LoggingMiddleware(Func<RequestContext, Task> next) {\n        _next = next;\n    }\n    public async Task Invoke(RequestContext ctx) {\n        Console.WriteLine($\"{ctx.Method} {ctx.Path}\");\n        await _next(ctx);\n        Console.WriteLine($\"Response: {ctx.StatusCode}\");\n    }\n}\n\nclass Program {\n    static async Task Main() {\n        int n = int.Parse(Console.ReadLine());\n        var middleware = new LoggingMiddleware(async ctx => await Task.CompletedTask);\n        for(int i = 0; i < n; i++) {\n            var parts = Console.ReadLine().Split(' ');\n            var ctx = new RequestContext {\n                Method = parts[0],\n                Path = parts[1],\n                StatusCode = int.Parse(parts[2])\n            };\n            await middleware.Invoke(ctx);\n        }\n    }\n}"
    },

"CS-INT2-E-1": {
        "id": "CS-INT2-E-1",
        "title": "C# Record Types",
        "skill": ".NET, C#",
        "difficulty": "Easy",
        "level": "Intermediate_2",
        "question_type": "coding",
        "tags": ["records", "immutability", "with-expression", "csharp-9", "csharp-intermediate"],
        "description": "Problem Statement\nGiven a person's name and age, create a Person record, then create a copy with an updated age using a with-expression. Print both.\n\nInput Format\nFirst line: name\nSecond line: original age\nThird line: new age\n\nOutput Format\nPrint original then updated in format:\nPerson { Name = {name}, Age = {age} }\n\nExample\nInput:\nAlice\n30\n31\n\nOutput:\nPerson { Name = Alice, Age = 30 }\nPerson { Name = Alice, Age = 31 }",
        "starter_code": {"csharp": "using System;\n\nrecord Person(string Name, int Age);\n\nclass Program {\n    static void Main() {\n        string name = Console.ReadLine();\n        int age = int.Parse(Console.ReadLine());\n        int newAge = int.Parse(Console.ReadLine());\n        // Create a Person record\n        // Use with-expression to create updated copy\n        // Print both\n    }\n}"},
        "test_cases": [
            {"input": "Alice\n30\n31", "output": "Person { Name = Alice, Age = 30 }\nPerson { Name = Alice, Age = 31 }"},
            {"input": "Bob\n25\n26", "output": "Person { Name = Bob, Age = 25 }\nPerson { Name = Bob, Age = 26 }"},
            {"input": "Charlie\n40\n41", "output": "Person { Name = Charlie, Age = 40 }\nPerson { Name = Charlie, Age = 41 }"}
        ],
        "hidden_test_cases": [
            {"input": "Diana\n22\n23", "output": "Person { Name = Diana, Age = 22 }\nPerson { Name = Diana, Age = 23 }"},
            {"input": "Eve\n35\n36", "output": "Person { Name = Eve, Age = 35 }\nPerson { Name = Eve, Age = 36 }"},
            {"input": "Frank\n50\n51", "output": "Person { Name = Frank, Age = 50 }\nPerson { Name = Frank, Age = 51 }"}
        ],
        "solution": "using System;\n\nrecord Person(string Name, int Age);\n\nclass Program {\n    static void Main() {\n        string name = Console.ReadLine();\n        int age = int.Parse(Console.ReadLine());\n        int newAge = int.Parse(Console.ReadLine());\n        var person = new Person(name, age);\n        var updated = person with { Age = newAge };\n        Console.WriteLine(person);\n        Console.WriteLine(updated);\n    }\n}"
    },
    "CS-INT2-M-1": {
        "id": "CS-INT2-M-1",
        "title": "Producer-Consumer with Channels",
        "skill": ".NET, C#",
        "difficulty": "Medium",
        "level": "Intermediate_2",
        "question_type": "coding",
        "tags": ["channels", "producer-consumer", "async", "concurrency", "csharp-advanced"],
        "description": "Problem Statement\nSimulate a producer-consumer pattern. Given n integers, produce and consume them one by one printing each step.\n\nInput Format\nFirst line: number of items n\nNext n lines: each integer value\n\nOutput Format\nFor each item print:\nProduced: {value}\nConsumed: {value}\n\nExample\nInput:\n3\n10\n20\n30\n\nOutput:\nProduced: 10\nConsumed: 10\nProduced: 20\nConsumed: 20\nProduced: 30\nConsumed: 30",
        "starter_code": {"csharp": "using System;\nusing System.Collections.Generic;\nusing System.Threading.Tasks;\n\nclass Program {\n    static async Task Main() {\n        int n = int.Parse(Console.ReadLine());\n        var queue = new Queue<int>();\n        // For each item produce then consume using async/await\n    }\n}"},
        "test_cases": [
            {"input": "3\n10\n20\n30", "output": "Produced: 10\nConsumed: 10\nProduced: 20\nConsumed: 20\nProduced: 30\nConsumed: 30"},
            {"input": "1\n42", "output": "Produced: 42\nConsumed: 42"},
            {"input": "2\n5\n15", "output": "Produced: 5\nConsumed: 5\nProduced: 15\nConsumed: 15"}
        ],
        "hidden_test_cases": [
            {"input": "4\n1\n2\n3\n4", "output": "Produced: 1\nConsumed: 1\nProduced: 2\nConsumed: 2\nProduced: 3\nConsumed: 3\nProduced: 4\nConsumed: 4"},
            {"input": "1\n0", "output": "Produced: 0\nConsumed: 0"},
            {"input": "3\n100\n200\n300", "output": "Produced: 100\nConsumed: 100\nProduced: 200\nConsumed: 200\nProduced: 300\nConsumed: 300"}
        ],
        "solution": "using System;\nusing System.Collections.Generic;\nusing System.Threading.Tasks;\n\nclass Program {\n    static async Task Main() {\n        int n = int.Parse(Console.ReadLine());\n        var queue = new Queue<int>();\n        for(int i = 0; i < n; i++) {\n            int value = int.Parse(Console.ReadLine());\n            await Task.Run(() => { queue.Enqueue(value); Console.WriteLine($\"Produced: {value}\"); });\n            await Task.Run(() => { int item = queue.Dequeue(); Console.WriteLine($\"Consumed: {item}\"); });\n        }\n    }\n}"
    },
    "CS-SP1-E-1": {
        "id": "CS-SP1-E-1",
        "title": "Span<T> for Zero-Allocation Slicing",
        "skill": ".NET, C#",
        "difficulty": "Easy",
        "level": "Specialist_1",
        "question_type": "coding",
        "tags": ["span", "memory", "zero-allocation", "performance", "csharp-advanced"],
        "description": "Problem Statement\nGiven a string, start index, length and target substring, use Span<char> to slice the string and check if it equals the target.\n\nInput Format\nFirst line: the string\nSecond line: start index\nThird line: length\nFourth line: target substring\n\nOutput Format\nPrint 'true' or 'false'\n\nRules\n- Use AsSpan() to slice\n- Use SequenceEqual() to compare\n\nExample\nInput:\nHello, World!\n7\n5\nWorld\n\nOutput:\ntrue",
        "starter_code": {"csharp": "using System;\n\nclass Program {\n    static void Main() {\n        string s = Console.ReadLine();\n        int start = int.Parse(Console.ReadLine());\n        int length = int.Parse(Console.ReadLine());\n        string target = Console.ReadLine();\n        // Use AsSpan to slice and SequenceEqual to compare\n    }\n}"},
        "test_cases": [
            {"input": "Hello, World!\n7\n5\nWorld", "output": "true"},
            {"input": "Hello, World!\n0\n5\nHello", "output": "true"},
            {"input": "Hello, World!\n0\n5\nWorld", "output": "false"}
        ],
        "hidden_test_cases": [
            {"input": "abcdefgh\n2\n3\ncde", "output": "true"},
            {"input": "abcdefgh\n0\n3\nabc", "output": "true"},
            {"input": "abcdefgh\n5\n3\nabc", "output": "false"}
        ],
        "solution": "using System;\n\nclass Program {\n    static void Main() {\n        string s = Console.ReadLine();\n        int start = int.Parse(Console.ReadLine());\n        int length = int.Parse(Console.ReadLine());\n        string target = Console.ReadLine();\n        ReadOnlySpan<char> span = s.AsSpan(start, length);\n        Console.WriteLine(span.SequenceEqual(target));\n    }\n}"
    },
    "CS-SP1-M-1": {
        "id": "CS-SP1-M-1",
        "title": "Middleware Pipeline Pattern",
        "skill": ".NET, C#",
        "difficulty": "Medium",
        "level": "Specialist_1",
        "question_type": "coding",
        "tags": ["pipeline", "middleware", "functional", "delegates", "csharp-advanced"],
        "description": "Problem Statement\nBuild a composable middleware pipeline. Given n middleware names and a request string, pass the request through all middleware in order. Each middleware prints '{name}: processing {request}'.\n\nInput Format\nFirst line: number of middleware n\nNext n lines: middleware name\nLast line: request string\n\nOutput Format\nFor each middleware print:\n{name}: processing {request}\n\nExample\nInput:\n3\nLogger\nAuth\nHandler\nGET /api/users\n\nOutput:\nLogger: processing GET /api/users\nAuth: processing GET /api/users\nHandler: processing GET /api/users",
        "starter_code": {"csharp": "using System;\nusing System.Collections.Generic;\nusing System.Threading.Tasks;\n\nclass Program {\n    static async Task Main() {\n        int n = int.Parse(Console.ReadLine());\n        var middlewares = new List<string>();\n        for(int i = 0; i < n; i++) middlewares.Add(Console.ReadLine());\n        string request = Console.ReadLine();\n        // Build and execute the pipeline using delegates/Func\n    }\n}"},
        "test_cases": [
            {"input": "3\nLogger\nAuth\nHandler\nGET /api/users", "output": "Logger: processing GET /api/users\nAuth: processing GET /api/users\nHandler: processing GET /api/users"},
            {"input": "1\nLogger\nPOST /api/items", "output": "Logger: processing POST /api/items"},
            {"input": "2\nAuth\nHandler\nDELETE /api/user/1", "output": "Auth: processing DELETE /api/user/1\nHandler: processing DELETE /api/user/1"}
        ],
        "hidden_test_cases": [
            {"input": "2\nLogger\nAuth\nGET /health", "output": "Logger: processing GET /health\nAuth: processing GET /health"},
            {"input": "3\nA\nB\nC\nrequest", "output": "A: processing request\nB: processing request\nC: processing request"},
            {"input": "1\nHandler\nGET /", "output": "Handler: processing GET /"}
        ],
        "solution": "using System;\nusing System.Collections.Generic;\nusing System.Threading.Tasks;\n\nclass Program {\n    static async Task Main() {\n        int n = int.Parse(Console.ReadLine());\n        var middlewares = new List<string>();\n        for(int i = 0; i < n; i++) middlewares.Add(Console.ReadLine());\n        string request = Console.ReadLine();\n        Func<Task> pipeline = () => Task.CompletedTask;\n        for(int i = middlewares.Count - 1; i >= 0; i--) {\n            string name = middlewares[i];\n            var next = pipeline;\n            pipeline = async () => { Console.WriteLine($\"{name}: processing {request}\"); await next(); };\n        }\n        await pipeline();\n    }\n}"
    },
    "CS-SP1-H-1": {
        "id": "CS-SP1-H-1",
        "title": "Build Dynamic Query with Expression Trees",
        "skill": ".NET, C#",
        "difficulty": "Hard",
        "level": "Specialist_1",
        "question_type": "coding",
        "tags": ["expression-trees", "dynamic-linq", "reflection", "csharp-advanced"],
        "description": "Problem Statement\nGiven a list of products with name and price, use expression trees to dynamically filter them by a property name and value.\n\nInput Format\nFirst line: number of products n\nNext n lines: product name and price separated by comma\nNext line: filter property (Name or Price)\nNext line: filter value\n\nOutput Format\nPrint matching product names one per line.\nIf no matches print 'No results'\n\nExample\nInput:\n3\nLaptop,1000\nPhone,500\nTablet,1000\nPrice\n1000\n\nOutput:\nLaptop\nTablet",
        "starter_code": {"csharp": "using System;\nusing System.Collections.Generic;\nusing System.Linq;\nusing System.Linq.Expressions;\n\nclass Product {\n    public string Name { get; set; }\n    public int Price { get; set; }\n}\n\nclass Program {\n    static Expression<Func<Product, bool>> BuildPredicate(string propName, string value) {\n        // Use Expression.Parameter, Property, Constant, Equal, Lambda\n        return null;\n    }\n\n    static void Main() {\n        int n = int.Parse(Console.ReadLine());\n        var products = new List<Product>();\n        for(int i = 0; i < n; i++) {\n            var parts = Console.ReadLine().Split(',');\n            products.Add(new Product { Name = parts[0], Price = int.Parse(parts[1]) });\n        }\n        string prop = Console.ReadLine();\n        string value = Console.ReadLine();\n        // Use BuildPredicate to filter and print results\n    }\n}"},
        "test_cases": [
            {"input": "3\nLaptop,1000\nPhone,500\nTablet,1000\nPrice\n1000", "output": "Laptop\nTablet"},
            {"input": "3\nLaptop,1000\nPhone,500\nTablet,800\nName\nPhone", "output": "Phone"},
            {"input": "3\nLaptop,1000\nPhone,500\nTablet,800\nPrice\n200", "output": "No results"}
        ],
        "hidden_test_cases": [
            {"input": "2\nWatch,300\nRing,300\nPrice\n300", "output": "Watch\nRing"},
            {"input": "2\nWatch,300\nRing,400\nName\nWatch", "output": "Watch"},
            {"input": "2\nWatch,300\nRing,400\nPrice\n999", "output": "No results"}
        ],
        "solution": "using System;\nusing System.Collections.Generic;\nusing System.Linq;\nusing System.Linq.Expressions;\n\nclass Product {\n    public string Name { get; set; }\n    public int Price { get; set; }\n}\n\nclass Program {\n    static Expression<Func<Product, bool>> BuildPredicate(string propName, string value) {\n        var param = Expression.Parameter(typeof(Product), \"x\");\n        var prop = Expression.Property(param, propName);\n        Expression constant = propName == \"Price\" ? Expression.Constant(int.Parse(value)) : (Expression)Expression.Constant(value);\n        var body = Expression.Equal(prop, constant);\n        return Expression.Lambda<Func<Product, bool>>(body, param);\n    }\n\n    static void Main() {\n        int n = int.Parse(Console.ReadLine());\n        var products = new List<Product>();\n        for(int i = 0; i < n; i++) {\n            var parts = Console.ReadLine().Split(',');\n            products.Add(new Product { Name = parts[0], Price = int.Parse(parts[1]) });\n        }\n        string prop = Console.ReadLine();\n        string value = Console.ReadLine();\n        var predicate = BuildPredicate(prop, value);\n        var results = products.AsQueryable().Where(predicate).ToList();\n        if(results.Count == 0) Console.WriteLine(\"No results\");\n        else results.ForEach(p => Console.WriteLine(p.Name));\n    }\n}"
    },
    "CS-SP2-E-1": {
        "id": "CS-SP2-E-1",
        "title": "stackalloc and unsafe Buffers",
        "skill": ".NET, C#",
        "difficulty": "Easy",
        "level": "Specialist_2",
        "question_type": "coding",
        "tags": ["unsafe", "stackalloc", "performance", "low-level", "csharp-advanced"],
        "description": "Problem Statement\nGiven n, allocate n bytes on the stack using stackalloc, fill with values 0 to n-1 and compute their sum.\n\nInput Format\nA single integer n\n\nOutput Format\nPrint the sum of bytes 0 to n-1\n\nRules\n- Use stackalloc to allocate the buffer\n- Use unsafe context\n\nExample\nInput:\n10\n\nOutput:\n45",
        "starter_code": {"csharp": "using System;\n\nclass Program {\n    static unsafe void Main() {\n        int n = int.Parse(Console.ReadLine());\n        // Use stackalloc to allocate n bytes\n        // Fill with 0..n-1 and print the sum\n    }\n}"},
        "test_cases": [
            {"input": "10", "output": "45"},
            {"input": "5", "output": "10"},
            {"input": "256", "output": "32640"}
        ],
        "hidden_test_cases": [
            {"input": "1", "output": "0"},
            {"input": "4", "output": "6"},
            {"input": "100", "output": "4950"}
        ],
        "solution": "using System;\n\nclass Program {\n    static unsafe void Main() {\n        int n = int.Parse(Console.ReadLine());\n        byte* buf = stackalloc byte[n];\n        for(int i = 0; i < n; i++) buf[i] = (byte)i;\n        int sum = 0;\n        for(int i = 0; i < n; i++) sum += buf[i];\n        Console.WriteLine(sum);\n    }\n}"
    },

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