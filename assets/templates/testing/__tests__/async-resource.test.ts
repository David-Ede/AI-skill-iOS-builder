import { useAsyncResource } from "../src/data/useAsyncResource";

describe("async resource module", () => {
  it("exports hook function", () => {
    expect(typeof useAsyncResource).toBe("function");
  });
});
