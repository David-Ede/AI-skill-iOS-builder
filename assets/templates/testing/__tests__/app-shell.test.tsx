/* eslint-disable @typescript-eslint/no-require-imports */
import React from "react";
import { render } from "@testing-library/react-native";

function loadScreen() {
  try {
    return require("../app/(tabs)/index").default;
  } catch {
    return require("../app/index").default;
  }
}

describe("app shell smoke", () => {
  it("renders the primary route", () => {
    const Screen = loadScreen();
    const { queryByText } = render(<Screen />);
    const hasHome = queryByText(/home/i);
    const hasWelcome = queryByText(/welcome/i);
    expect(hasHome || hasWelcome).toBeTruthy();
  });
});
