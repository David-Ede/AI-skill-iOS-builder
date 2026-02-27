import { Text, View } from "react-native";

type StatePanelProps = {
  state: "ready" | "loading" | "empty" | "error";
  description: string;
};

export function StatePanel({ state, description }: StatePanelProps) {
  return (
    <View style={{ borderWidth: 1, borderColor: "#cbd5e1", borderRadius: 12, padding: 14 }}>
      <Text style={{ fontSize: 16, fontWeight: "600" }}>State: {state}</Text>
      <Text style={{ marginTop: 6 }}>{description}</Text>
    </View>
  );
}
