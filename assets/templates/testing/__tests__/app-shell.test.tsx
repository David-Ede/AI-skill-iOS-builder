/* eslint-disable @typescript-eslint/no-require-imports */
import React from "react";
import { render } from "@testing-library/react-native";

function loadHomeScreen() {
  try {
    return require("../app/(tabs)/index").default;
  } catch {
    return require("../app/index").default;
  }
}

function loadExploreScreen() {
  try {
    return require("../app/(tabs)/explore").default;
  } catch {
    return require("../app/explore").default;
  }
}

describe("app shell smoke", () => {
  it("renders the primary route", () => {
    const Screen = loadHomeScreen();
    const { queryByText } = render(<Screen />);
    const hasHome = queryByText(/home/i);
    const hasWelcome = queryByText(/welcome/i);
    expect(hasHome || hasWelcome).toBeTruthy();
  });

  it("renders the secondary route baseline", () => {
    const Screen = loadExploreScreen();
    const { queryByText } = render(<Screen />);
    expect(queryByText(/explore/i)).toBeTruthy();
  });
});
