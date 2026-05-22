import json

# Load the existing dataset
with open('problem_dataset_new.json', 'r') as f:
    data = json.load(f)

# Fixed questions
fixed_questions = {
    "VB-BEG-E-1": {
        "id": "VB-BEG-E-1",
        "title": "Hello World in VB.NET",
        "skill": ".NET, VB.NET",
        "difficulty": "Easy",
        "level": "Beginner",
        "question_type": "coding",
        "tags": ["hello-world", "console", "vbnet-basics"],
        "description": "Problem Statement\nWrite a VB.NET program that prints 'Hello, World!' to the console.\n\nInput Format\nNo input required.\n\nOutput Format\nPrint exactly: Hello, World!\n\nExample\nInput:\n(none)\n\nOutput:\nHello, World!",
        "starter_code": {"vb": "Module Program\n    Sub Main()\n        ' Your code here\n    End Sub\nEnd Module"},
        "test_cases": [{"input": "", "output": "Hello, World!"}],
        "hidden_test_cases": [{"input": "", "output": "Hello, World!"}],
        "solution": "Module Program\n    Sub Main()\n        Console.WriteLine(\"Hello, World!\")\n    End Sub\nEnd Module"
    },
    "VB-BEG-E-2": {
        "id": "VB-BEG-E-2",
        "title": "Reverse a String in VB.NET",
        "skill": ".NET, VB.NET",
        "difficulty": "Easy",
        "level": "Beginner",
        "question_type": "coding",
        "tags": ["string", "array", "vbnet-basics"],
        "description": "Problem Statement\nGiven a string, print its reverse.\n\nInput Format\nA single line containing a string s.\n\nOutput Format\nPrint the reversed string.\n\nRules\n- The string may contain spaces and special characters.\n- Empty string should return empty string.\n\nExample\nInput:\nhello\n\nOutput:\nolleh",
        "starter_code": {"vb": "Module Program\n    Sub Main()\n        Dim s As String = Console.ReadLine()\n        ' Your code here\n    End Sub\nEnd Module"},
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
        "solution": "Module Program\n    Sub Main()\n        Dim s As String = Console.ReadLine()\n        Dim arr As Char() = s.ToCharArray()\n        Array.Reverse(arr)\n        Console.WriteLine(New String(arr))\n    End Sub\nEnd Module"
    },
    "VB-BEG-E-3": {
        "id": "VB-BEG-E-3",
        "title": "Fibonacci Loop in VB.NET",
        "skill": ".NET, VB.NET",
        "difficulty": "Easy",
        "level": "Beginner",
        "question_type": "coding",
        "tags": ["math", "loop", "vbnet-basics"],
        "description": "Problem Statement\nGiven a number n, print the first n numbers of the Fibonacci sequence.\n\nInput Format\nA single integer n.\n\nOutput Format\nPrint the first n Fibonacci numbers separated by spaces on a single line.\n\nRules\n- n will always be a positive integer.\n- Fibonacci sequence starts at 0.\n\nExample\nInput:\n10\n\nOutput:\n0 1 1 2 3 5 8 13 21 34",
        "starter_code": {"vb": "Module Program\n    Sub Main()\n        Dim n As Integer = Integer.Parse(Console.ReadLine())\n        ' Your code here\n    End Sub\nEnd Module"},
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
        "solution": "Module Program\n    Sub Main()\n        Dim n As Integer = Integer.Parse(Console.ReadLine())\n        Dim a As Integer = 0, b As Integer = 1\n        Dim result As New System.Collections.Generic.List(Of String)\n        For i As Integer = 0 To n - 1\n            result.Add(a.ToString())\n            Dim temp As Integer = a + b\n            a = b\n            b = temp\n        Next\n        Console.WriteLine(String.Join(\" \", result))\n    End Sub\nEnd Module"
    },
    "VB-BEG-M-1": {
        "id": "VB-BEG-M-1",
        "title": "OOP: Class with Properties and Method",
        "skill": ".NET, VB.NET",
        "difficulty": "Medium",
        "level": "Beginner",
        "question_type": "coding",
        "tags": ["oop", "classes", "properties", "vbnet-basics"],
        "description": "Problem Statement\nGiven a car's make, model and year, create a Car class and print its description.\n\nInput Format\nFirst line: make\nSecond line: model\nThird line: year\n\nOutput Format\nPrint: {year} {make} {model}\n\nExample\nInput:\nToyota\nCamry\n2023\n\nOutput:\n2023 Toyota Camry",
        "starter_code": {"vb": "Module Program\n    Public Class Car\n        Public Property Make As String\n        Public Property Model As String\n        Public Property Year As Integer\n        Public Function Describe() As String\n            ' Return formatted string: Year Make Model\n        End Function\n    End Class\n\n    Sub Main()\n        Dim make As String = Console.ReadLine()\n        Dim model As String = Console.ReadLine()\n        Dim year As Integer = Integer.Parse(Console.ReadLine())\n        ' Create Car and print Describe()\n    End Sub\nEnd Module"},
        "test_cases": [
            {"input": "Toyota\nCamry\n2023", "output": "2023 Toyota Camry"},
            {"input": "Ford\nF-150\n2020", "output": "2020 Ford F-150"},
            {"input": "Honda\nCivic\n2019", "output": "2019 Honda Civic"}
        ],
        "hidden_test_cases": [
            {"input": "BMW\nM3\n2022", "output": "2022 BMW M3"},
            {"input": "Tesla\nModel3\n2024", "output": "2024 Tesla Model3"},
            {"input": "Audi\nA4\n2021", "output": "2021 Audi A4"}
        ],
        "solution": "Module Program\n    Public Class Car\n        Public Property Make As String\n        Public Property Model As String\n        Public Property Year As Integer\n        Public Function Describe() As String\n            Return $\"{Year} {Make} {Model}\"\n        End Function\n    End Class\n\n    Sub Main()\n        Dim make As String = Console.ReadLine()\n        Dim model As String = Console.ReadLine()\n        Dim year As Integer = Integer.Parse(Console.ReadLine())\n        Dim car As New Car With {.Make = make, .Model = model, .Year = year}\n        Console.WriteLine(car.Describe())\n    End Sub\nEnd Module"
    },
    "VB-BEG-M-2": {
        "id": "VB-BEG-M-2",
        "title": "LINQ Filter with VB.NET",
        "skill": ".NET, VB.NET",
        "difficulty": "Medium",
        "level": "Beginner",
        "question_type": "coding",
        "tags": ["linq", "filtering", "sorting", "vbnet-basics"],
        "description": "Problem Statement\nGiven a list of integers, use LINQ to filter numbers greater than 10 and print them sorted descending.\n\nInput Format\nFirst line: number of integers n\nNext n lines: each integer\n\nOutput Format\nPrint filtered numbers one per line in descending order.\nIf no numbers match, print nothing.\n\nExample\nInput:\n5\n5\n15\n3\n20\n10\n\nOutput:\n20\n15",
        "starter_code": {"vb": "Imports System.Linq\n\nModule Program\n    Sub Main()\n        Dim n As Integer = Integer.Parse(Console.ReadLine())\n        Dim numbers As New System.Collections.Generic.List(Of Integer)\n        For i As Integer = 0 To n - 1\n            numbers.Add(Integer.Parse(Console.ReadLine()))\n        Next\n        ' Use LINQ to filter > 10 and sort descending\n        ' Print each result\n    End Sub\nEnd Module"},
        "test_cases": [
            {"input": "5\n5\n15\n3\n20\n10", "output": "20\n15"},
            {"input": "3\n1\n2\n3", "output": ""},
            {"input": "4\n11\n12\n13\n14", "output": "14\n13\n12\n11"}
        ],
        "hidden_test_cases": [
            {"input": "3\n10\n10\n10", "output": ""},
            {"input": "4\n100\n5\n50\n3", "output": "100\n50"},
            {"input": "2\n11\n12", "output": "12\n11"}
        ],
        "solution": "Imports System.Linq\n\nModule Program\n    Sub Main()\n        Dim n As Integer = Integer.Parse(Console.ReadLine())\n        Dim numbers As New System.Collections.Generic.List(Of Integer)\n        For i As Integer = 0 To n - 1\n            numbers.Add(Integer.Parse(Console.ReadLine()))\n        Next\n        Dim result = From num In numbers Where num > 10 Order By num Descending Select num\n        For Each num In result\n            Console.WriteLine(num)\n        Next\n    End Sub\nEnd Module"
    },
    "VB-BEG-H-1": {
        "id": "VB-BEG-H-1",
        "title": "Interface Implementation in VB.NET",
        "skill": ".NET, VB.NET",
        "difficulty": "Hard",
        "level": "Beginner",
        "question_type": "coding",
        "tags": ["interfaces", "oop", "vbnet-basics"],
        "description": "Problem Statement\nGiven width and height of a rectangle, implement an IShape interface and print its area and perimeter.\n\nInput Format\nFirst line: width (decimal)\nSecond line: height (decimal)\n\nOutput Format\nPrint:\nArea={area}\nPerimeter={perimeter}\n\nRules\n- Area = width * height\n- Perimeter = 2 * (width + height)\n- Print values with 1 decimal place\n\nExample\nInput:\n5\n3\n\nOutput:\nArea=15.0\nPerimeter=16.0",
        "starter_code": {"vb": "Module Program\n    Interface IShape\n        Function Area() As Double\n        Function Perimeter() As Double\n    End Interface\n\n    Class Rectangle\n        Implements IShape\n        Public Property Width As Double\n        Public Property Height As Double\n        ' Implement Area and Perimeter\n    End Class\n\n    Sub Main()\n        Dim width As Double = Double.Parse(Console.ReadLine())\n        Dim height As Double = Double.Parse(Console.ReadLine())\n        ' Create Rectangle and print Area and Perimeter\n    End Sub\nEnd Module"},
        "test_cases": [
            {"input": "5\n3", "output": "Area=15.0\nPerimeter=16.0"},
            {"input": "10\n4", "output": "Area=40.0\nPerimeter=28.0"},
            {"input": "7\n7", "output": "Area=49.0\nPerimeter=28.0"}
        ],
        "hidden_test_cases": [
            {"input": "0\n10", "output": "Area=0.0\nPerimeter=20.0"},
            {"input": "2.5\n4", "output": "Area=10.0\nPerimeter=13.0"},
            {"input": "1\n1", "output": "Area=1.0\nPerimeter=4.0"}
        ],
        "solution": "Module Program\n    Interface IShape\n        Function Area() As Double\n        Function Perimeter() As Double\n    End Interface\n\n    Class Rectangle\n        Implements IShape\n        Public Property Width As Double\n        Public Property Height As Double\n        Public Function Area() As Double Implements IShape.Area\n            Return Width * Height\n        End Function\n        Public Function Perimeter() As Double Implements IShape.Perimeter\n            Return 2 * (Width + Height)\n        End Function\n    End Class\n\n    Sub Main()\n        Dim width As Double = Double.Parse(Console.ReadLine())\n        Dim height As Double = Double.Parse(Console.ReadLine())\n        Dim rect As New Rectangle With {.Width = width, .Height = height}\n        Console.WriteLine($\"Area={rect.Area():F1}\")\n        Console.WriteLine($\"Perimeter={rect.Perimeter():F1}\")\n    End Sub\nEnd Module"
    },
"VB-INT1-E-1": {
        "id": "VB-INT1-E-1",
        "title": "Async/Await in VB.NET",
        "skill": ".NET, VB.NET",
        "difficulty": "Easy",
        "level": "Intermediate_1",
        "question_type": "coding",
        "tags": ["async-await", "tasks", "vbnet-intermediate"],
        "description": "Problem Statement\nWrite a VB.NET program that simulates async task processing. Given n tasks each with a name and result value, process them asynchronously and print each result.\n\nInput Format\nFirst line: number of tasks n\nNext n lines: task name and result value separated by space\n\nOutput Format\nFor each task print:\nTask {name} completed with result: {value}\n\nExample\nInput:\n3\nFetch 42\nCompute 100\nLoad 7\n\nOutput:\nTask Fetch completed with result: 42\nTask Compute completed with result: 100\nTask Load completed with result: 7",
        "starter_code": {"vb": "Imports System.Threading.Tasks\n\nModule Program\n    Async Function ProcessTask(name As String, value As Integer) As Task(Of String)\n        Return Await Task.Run(Function() \"\")\n    End Function\n\n    Async Function Main() As Task\n        Dim n As Integer = Integer.Parse(Console.ReadLine())\n        For i As Integer = 0 To n - 1\n            Dim parts As String() = Console.ReadLine().Split(\" \")\n            Dim name As String = parts(0)\n            Dim value As Integer = Integer.Parse(parts(1))\n            ' Call ProcessTask and print result\n        Next\n    End Function\nEnd Module"},
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
        "solution": "Imports System.Threading.Tasks\n\nModule Program\n    Async Function ProcessTask(name As String, value As Integer) As Task(Of String)\n        Return Await Task.Run(Function() $\"Task {name} completed with result: {value}\")\n    End Function\n\n    Async Function Main() As Task\n        Dim n As Integer = Integer.Parse(Console.ReadLine())\n        For i As Integer = 0 To n - 1\n            Dim parts As String() = Console.ReadLine().Split(\" \")\n            Dim name As String = parts(0)\n            Dim value As Integer = Integer.Parse(parts(1))\n            Dim result As String = Await ProcessTask(name, value)\n            Console.WriteLine(result)\n        Next\n    End Function\nEnd Module"
    },
    "VB-INT1-M-1": {
        "id": "VB-INT1-M-1",
        "title": "Generic Stack in VB.NET",
        "skill": ".NET, VB.NET",
        "difficulty": "Medium",
        "level": "Intermediate_1",
        "question_type": "coding",
        "tags": ["generics", "stack", "data-structures", "vbnet-intermediate"],
        "description": "Problem Statement\nImplement a generic Stack class in VB.NET and process a series of commands.\n\nCommands:\n- PUSH value: push value onto stack\n- POP: pop and print top value\n- PEEK: print top value without removing\n- ISEMPTY: print True or False\n\nInput Format\nFirst line: number of commands n\nNext n lines: each command\n\nOutput Format\nPrint output for POP, PEEK and ISEMPTY commands only.\n\nExample\nInput:\n4\nPUSH 1\nPUSH 2\nPEEK\nPOP\n\nOutput:\n2\n2",
        "starter_code": {"vb": "Module Program\n    Public Class Stack(Of T)\n        Private _items As New System.Collections.Generic.List(Of T)()\n        Public Sub Push(item As T)\n            ' Add item to stack\n        End Sub\n        Public Function Pop() As T\n            ' Remove and return top item\n        End Function\n        Public Function Peek() As T\n            ' Return top item without removing\n        End Function\n        Public ReadOnly Property IsEmpty As Boolean\n            Get\n                ' Return True if empty\n            End Get\n        End Property\n    End Class\n\n    Sub Main()\n        Dim n As Integer = Integer.Parse(Console.ReadLine())\n        Dim stack As New Stack(Of String)()\n        For i As Integer = 0 To n - 1\n            Dim line As String = Console.ReadLine()\n            ' Handle PUSH, POP, PEEK, ISEMPTY commands\n        Next\n    End Sub\nEnd Module"},
        "test_cases": [
            {"input": "4\nPUSH 1\nPUSH 2\nPEEK\nPOP", "output": "2\n2"},
            {"input": "2\nISEMPTY\nPUSH 5", "output": "True"},
            {"input": "4\nPUSH a\nPUSH b\nPOP\nISEMPTY", "output": "b\nFalse"}
        ],
        "hidden_test_cases": [
            {"input": "3\nPUSH 10\nPOP\nISEMPTY", "output": "10\nTrue"},
            {"input": "3\nPUSH x\nPUSH y\nPEEK", "output": "y"},
            {"input": "1\nISEMPTY", "output": "True"}
        ],
        "solution": "Module Program\n    Public Class Stack(Of T)\n        Private _items As New System.Collections.Generic.List(Of T)()\n        Public Sub Push(item As T)\n            _items.Add(item)\n        End Sub\n        Public Function Pop() As T\n            Dim last As T = _items(_items.Count - 1)\n            _items.RemoveAt(_items.Count - 1)\n            Return last\n        End Function\n        Public Function Peek() As T\n            Return _items(_items.Count - 1)\n        End Function\n        Public ReadOnly Property IsEmpty As Boolean\n            Get\n                Return _items.Count = 0\n            End Get\n        End Property\n    End Class\n\n    Sub Main()\n        Dim n As Integer = Integer.Parse(Console.ReadLine())\n        Dim stack As New Stack(Of String)()\n        For i As Integer = 0 To n - 1\n            Dim line As String = Console.ReadLine()\n            Dim parts As String() = line.Split(\" \")\n            If parts(0) = \"PUSH\" Then\n                stack.Push(parts(1))\n            ElseIf parts(0) = \"POP\" Then\n                Console.WriteLine(stack.Pop())\n            ElseIf parts(0) = \"PEEK\" Then\n                Console.WriteLine(stack.Peek())\n            ElseIf parts(0) = \"ISEMPTY\" Then\n                Console.WriteLine(stack.IsEmpty)\n            End If\n        Next\n    End Sub\nEnd Module"
    },
    "VB-INT1-M-2": {
        "id": "VB-INT1-M-2",
        "title": "Delegates and Events in VB.NET",
        "skill": ".NET, VB.NET",
        "difficulty": "Medium",
        "level": "Intermediate_1",
        "question_type": "coding",
        "tags": ["events", "delegates", "vbnet-intermediate"],
        "description": "Problem Statement\nYou are building a simple timer event system. Given n ticks, fire a Tick event for each and print a message from the handler.\n\nInput Format\nFirst line: number of ticks n\n\nOutput Format\nFor each tick print:\nTick!\n\nRules\n- Create a SimpleTimer class with a Tick event\n- Subscribe a handler that prints 'Tick!'\n- Use RaiseEvent to fire the event\n\nExample\nInput:\n3\n\nOutput:\nTick!\nTick!\nTick!",
        "starter_code": {"vb": "Module Program\n    Public Class SimpleTimer\n        Public Event Tick()\n        Public Sub Start(seconds As Integer)\n            ' Raise Tick event for each second\n        End Sub\n    End Class\n\n    Sub Main()\n        Dim n As Integer = Integer.Parse(Console.ReadLine())\n        Dim t As New SimpleTimer()\n        ' Subscribe handler that prints Tick!\n        ' Start timer with n ticks\n    End Sub\nEnd Module"},
        "test_cases": [
            {"input": "3", "output": "Tick!\nTick!\nTick!"},
            {"input": "1", "output": "Tick!"},
            {"input": "5", "output": "Tick!\nTick!\nTick!\nTick!\nTick!"}
        ],
        "hidden_test_cases": [
            {"input": "0", "output": ""},
            {"input": "2", "output": "Tick!\nTick!"},
            {"input": "4", "output": "Tick!\nTick!\nTick!\nTick!"}
        ],
        "solution": "Module Program\n    Public Class SimpleTimer\n        Public Event Tick()\n        Public Sub Start(seconds As Integer)\n            For i As Integer = 1 To seconds\n                RaiseEvent Tick()\n            Next\n        End Sub\n    End Class\n\n    Sub Main()\n        Dim n As Integer = Integer.Parse(Console.ReadLine())\n        Dim t As New SimpleTimer()\n        AddHandler t.Tick, Sub() Console.WriteLine(\"Tick!\")\n        t.Start(n)\n    End Sub\nEnd Module"
    },
    "VB-INT1-H-1": {
        "id": "VB-INT1-H-1",
        "title": "Custom Attributes and Reflection in VB.NET",
        "skill": ".NET, VB.NET",
        "difficulty": "Hard",
        "level": "Intermediate_1",
        "question_type": "coding",
        "tags": ["reflection", "attributes", "meta-programming", "vbnet-intermediate"],
        "description": "Problem Statement\nGiven a list of property names and descriptions, print each property's description.\n\nInput Format\nFirst line: number of properties n\nNext n lines: property name and description separated by comma\n\nOutput Format\nFor each property print:\n{name}: {description}\n\nExample\nInput:\n2\nName,Full name of the user\nAge,Age of the user\n\nOutput:\nName: Full name of the user\nAge: Age of the user",
        "starter_code": {"vb": "Imports System.Reflection\n\nModule Program\n    <AttributeUsage(AttributeTargets.All)>\n    Public Class DescriptionAttribute\n        Inherits Attribute\n        Public Property Text As String\n        Public Sub New(text As String)\n            Me.Text = text\n        End Sub\n    End Class\n\n    Sub Main()\n        Dim n As Integer = Integer.Parse(Console.ReadLine())\n        Dim properties As New System.Collections.Generic.Dictionary(Of String, String)()\n        For i As Integer = 0 To n - 1\n            Dim parts As String() = Console.ReadLine().Split(\",\")\n            properties.Add(parts(0), parts(1))\n        Next\n        ' Print each property name and description\n    End Sub\nEnd Module"},
        "test_cases": [
            {"input": "2\nName,Full name of the user\nAge,Age of the user", "output": "Name: Full name of the user\nAge: Age of the user"},
            {"input": "1\nEmail,Email address", "output": "Email: Email address"},
            {"input": "3\nId,Unique identifier\nRole,User role\nDept,Department", "output": "Id: Unique identifier\nRole: User role\nDept: Department"}
        ],
        "hidden_test_cases": [
            {"input": "2\nFirst,First name\nLast,Last name", "output": "First: First name\nLast: Last name"},
            {"input": "1\nPhone,Phone number", "output": "Phone: Phone number"},
            {"input": "3\nA,Alpha\nB,Beta\nC,Gamma", "output": "A: Alpha\nB: Beta\nC: Gamma"}
        ],
        "solution": "Imports System.Reflection\n\nModule Program\n    <AttributeUsage(AttributeTargets.All)>\n    Public Class DescriptionAttribute\n        Inherits Attribute\n        Public Property Text As String\n        Public Sub New(text As String)\n            Me.Text = text\n        End Sub\n    End Class\n\n    Sub Main()\n        Dim n As Integer = Integer.Parse(Console.ReadLine())\n        Dim properties As New System.Collections.Generic.Dictionary(Of String, String)()\n        For i As Integer = 0 To n - 1\n            Dim parts As String() = Console.ReadLine().Split(\",\")\n            properties.Add(parts(0), parts(1))\n        Next\n        For Each kvp In properties\n            Console.WriteLine($\"{kvp.Key}: {kvp.Value}\")\n        Next\n    End Sub\nEnd Module"
    },

"VB-INT2-E-1": {
        "id": "VB-INT2-E-1",
        "title": "Pattern Matching with Select Case",
        "skill": ".NET, VB.NET",
        "difficulty": "Easy",
        "level": "Intermediate_2",
        "question_type": "coding",
        "tags": ["pattern-matching", "select-case", "control-flow", "vbnet-intermediate"],
        "description": "Problem Statement\nGiven an integer, use Select Case to categorize it and print the appropriate message.\n\nInput Format\nA single integer.\n\nOutput Format\nPrint one of:\n- 'Negative' if less than 0\n- 'Zero' if equal to 0\n- 'Positive small' if between 1 and 100\n- 'Large or other type' if greater than 100\n\nExample\nInput:\n50\n\nOutput:\nPositive small",
        "starter_code": {"vb": "Module Program\n    Sub Main()\n        Dim value As Integer = Integer.Parse(Console.ReadLine())\n        Select Case value\n            ' Handle negative, zero, 1-100, else\n        End Select\n    End Sub\nEnd Module"},
        "test_cases": [
            {"input": "-5", "output": "Negative"},
            {"input": "0", "output": "Zero"},
            {"input": "50", "output": "Positive small"},
            {"input": "200", "output": "Large or other type"}
        ],
        "hidden_test_cases": [
            {"input": "-100", "output": "Negative"},
            {"input": "100", "output": "Positive small"},
            {"input": "101", "output": "Large or other type"}
        ],
        "solution": "Module Program\n    Sub Main()\n        Dim value As Integer = Integer.Parse(Console.ReadLine())\n        Select Case value\n            Case Is < 0\n                Console.WriteLine(\"Negative\")\n            Case 0\n                Console.WriteLine(\"Zero\")\n            Case 1 To 100\n                Console.WriteLine(\"Positive small\")\n            Case Else\n                Console.WriteLine(\"Large or other type\")\n        End Select\n    End Sub\nEnd Module"
    },
    "VB-SP1-E-1": {
        "id": "VB-SP1-E-1",
        "title": "XML Literals in VB.NET",
        "skill": ".NET, VB.NET",
        "difficulty": "Easy",
        "level": "Specialist_1",
        "question_type": "coding",
        "tags": ["xml-literals", "linq-to-xml", "vbnet-advanced"],
        "description": "Problem Statement\nGiven a list of books with title and price, use XML literals and LINQ to XML to find and print titles of books cheaper than a given price.\n\nInput Format\nFirst line: number of books n\nNext n lines: title and price separated by comma\nLast line: maximum price threshold\n\nOutput Format\nPrint titles of books cheaper than the threshold, one per line.\nIf none found, print 'No results'\n\nExample\nInput:\n2\nVB.NET Mastery,29.99\nASP.NET Core,39.99\n35\n\nOutput:\nVB.NET Mastery",
        "starter_code": {"vb": "Imports System.Xml.Linq\n\nModule Program\n    Sub Main()\n        Dim n As Integer = Integer.Parse(Console.ReadLine())\n        Dim books As New System.Collections.Generic.List(Of (Title As String, Price As Decimal))()\n        For i As Integer = 0 To n - 1\n            Dim parts As String() = Console.ReadLine().Split(\",\")\n            books.Add((parts(0), Decimal.Parse(parts(1))))\n        Next\n        Dim threshold As Decimal = Decimal.Parse(Console.ReadLine())\n        ' Build XML literal and query with LINQ to XML\n        ' Print titles of books cheaper than threshold\n    End Sub\nEnd Module"},
        "test_cases": [
            {"input": "2\nVB.NET Mastery,29.99\nASP.NET Core,39.99\n35", "output": "VB.NET Mastery"},
            {"input": "2\nVB.NET Mastery,29.99\nASP.NET Core,39.99\n50", "output": "VB.NET Mastery\nASP.NET Core"},
            {"input": "2\nVB.NET Mastery,29.99\nASP.NET Core,39.99\n20", "output": "No results"}
        ],
        "hidden_test_cases": [
            {"input": "3\nBook A,10.00\nBook B,20.00\nBook C,30.00\n25", "output": "Book A\nBook B"},
            {"input": "1\nBook A,50.00\n30", "output": "No results"},
            {"input": "3\nBook A,10.00\nBook B,20.00\nBook C,30.00\n100", "output": "Book A\nBook B\nBook C"}
        ],
        "solution": "Imports System.Xml.Linq\n\nModule Program\n    Sub Main()\n        Dim n As Integer = Integer.Parse(Console.ReadLine())\n        Dim books As New System.Collections.Generic.List(Of (Title As String, Price As Decimal))()\n        For i As Integer = 0 To n - 1\n            Dim parts As String() = Console.ReadLine().Split(\",\")\n            books.Add((parts(0), Decimal.Parse(parts(1))))\n        Next\n        Dim threshold As Decimal = Decimal.Parse(Console.ReadLine())\n        Dim catalog = New XElement(\"Catalog\", books.Select(Function(b) New XElement(\"Book\", New XElement(\"Title\", b.Title), New XElement(\"Price\", b.Price))))\n        Dim cheapBooks = From b In catalog.Elements(\"Book\") Where CDec(b.Element(\"Price\").Value) < threshold Select b.Element(\"Title\").Value\n        Dim result = cheapBooks.ToList()\n        If result.Count = 0 Then\n            Console.WriteLine(\"No results\")\n        Else\n            For Each title In result\n                Console.WriteLine(title)\n            Next\n        End If\n    End Sub\nEnd Module"
    },
}

# Update the questions in the dataset
for skill in data['skills']:
    if skill['skill'] == '.NET, VB.NET':
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