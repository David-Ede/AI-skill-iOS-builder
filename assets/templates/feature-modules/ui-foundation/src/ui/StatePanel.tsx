import { Text, View } from "react-native";
import { useThemeColors } from "./theme";

type StatePanelProps = {
  state: "ready" | "loading" | "empty" | "error";
  description: string;
};

export function StatePanel({ state, description }: StatePanelProps) {
  const colors = useThemeColors();

  return (
    <View style={{ borderWidth: 1, borderColor: colors.border, borderRadius: 12, padding: 14, backgroundColor: colors.surface }}>
      <Text style={{ fontSize: 16, fontWeight: "600", color: colors.text }}>State: {state}</Text>
      <Text style={{ marginTop: 6, color: colors.textMuted }}>{description}</Text>
    </View>
  );
}
