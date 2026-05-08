import React from "react";
import { render, screen } from "@testing-library/react";
import "@testing-library/jest-dom";

import Hello from "./Hello.jsx";

test("renders hello world", () => {
  render(<Hello />);

  expect(screen.getByText("Hello World")).toBeInTheDocument();
});