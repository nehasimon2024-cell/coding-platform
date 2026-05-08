# 1. Install Everything Globally

Run once:

```powershell
npm install -g jest jest-environment-jsdom babel-jest @babel/core @babel/preset-env @babel/preset-react react react-dom @testing-library/react @testing-library/jest-dom
```

---

# 2. Set NODE_PATH (Important)

PowerShell:

```powershell
$env:NODE_PATH = (npm root -g)
```

Verify:

```powershell
echo $env:NODE_PATH
```

Expected something like:

```txt
C:\Users\<you>\AppData\Roaming\npm\node_modules
```

---

# 3. Create Minimal package.json

## package.json

```json
{
  "type": "module"
}
```

Reason:

- enables ES modules
- allows `import`
- avoids Node warnings

---

# 4. Create Babel Config

## babel.config.cjs

```js
module.exports = {
  presets: [
    ["@babel/preset-env"],
    ["@babel/preset-react", { runtime: "automatic" }],
  ],
};
```

Reason:

- transpiles JSX
- transpiles modern JS

---

# 5. Create Jest Config

## jest.config.cjs

```js
module.exports = {
  testEnvironment: "jsdom",
  transform: {
    "^.+\\.[jt]sx?$": "babel-jest",
  },
};
```

Reason:

- jsdom simulates browser
- babel-jest transpiles JSX

---

# 6. Create React Component

## Hello.jsx

```jsx
export default function Hello() {
  return <h1>Hello World</h1>;
}
```

---

# 7. Create Test

## Hello.test.jsx

```jsx
import React from "react";
import { render, screen } from "@testing-library/react";
import "@testing-library/jest-dom";

import Hello from "./Hello.jsx";

test("renders hello world", () => {
  render(<Hello />);
  expect(screen.getByText("Hello World")).toBeInTheDocument();
});
```

---

# 8. Run Tests

```powershell
npx -y jest
```

---

# Final Successful Output

```txt
PASS  ./Hello.test.jsx
√ renders hello world

Test Suites: 1 passed
Tests: 1 passed
```

---
