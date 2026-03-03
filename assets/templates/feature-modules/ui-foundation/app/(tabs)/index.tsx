import { useMemo, useState } from "react";
import { Pressable, Text, View } from "react-native";
import { StatePanel } from "../../src/ui/StatePanel";
import { useThemeColors } from "../../src/ui/theme";

type HomeState = "ready" | "loading" | "empty" | "error";

export default function HomeScreen() {
  const [state, setState] = useState<HomeState>("ready");
  const colors = useThemeColors();

  const description = useMemo(() => {
    if (state === "loading") return "Loading data...";
    if (state === "empty") return "No records found yet.";
    if (state === "error") return "Something failed. Retry soon.";
    return "Data loaded and ready.";
  }, [state]);

  return (
    <View style={{ flex: 1, padding: 24, justifyContent: "center", gap: 14, backgroundColor: colors.background }}>
      <Text style={{ fontSize: 28, fontWeight: "700", color: colors.text }}>Home</Text>
      <StatePanel state={state} description={description} />
      <View style={{ flexDirection: "row", flexWrap: "wrap", gap: 10 }}>
        {(["ready", "loading", "empty", "error"] as HomeState[]).map((value) => (
          <Pressable
            key={value}
            onPress={() => setState(value)}
            style={{
              backgroundColor: state === value ? colors.buttonPrimaryBackground : colors.buttonSecondaryBackground,
              paddingHorizontal: 12,
              paddingVertical: 10,
              borderRadius: 10,
            }}
          >
            <Text style={{ color: state === value ? colors.buttonPrimaryText : colors.buttonSecondaryText }}>{value}</Text>
          </Pressable>
        ))}
      </View>
    </View>
  );
}
