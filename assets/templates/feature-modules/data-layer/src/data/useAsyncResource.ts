import { useEffect, useState } from "react";

type AsyncState<T> =
  | { status: "loading" }
  | { status: "error"; error: string }
  | { status: "empty" }
  | { status: "ready"; value: T };

export function useAsyncResource<T>(loader: () => Promise<T | null>) {
  const [state, setState] = useState<AsyncState<T>>({ status: "loading" });

  useEffect(() => {
    let alive = true;

    async function run() {
      try {
        const result = await loader();
        if (!alive) return;
        if (result == null) {
          setState({ status: "empty" });
          return;
        }
        setState({ status: "ready", value: result });
      } catch (error) {
        if (!alive) return;
        setState({ status: "error", error: String(error) });
      }
    }

    run();
    return () => {
      alive = false;
    };
  }, [loader]);

  return state;
}
