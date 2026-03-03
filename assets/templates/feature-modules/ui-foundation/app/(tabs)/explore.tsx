import { Text, View } from "react-native";
import { useThemeColors } from "../../src/ui/theme";

export default function ExploreScreen() {
  const colors = useThemeColors();

  return (
    <View style={{ flex: 1, justifyContent: "center", alignItems: "center", padding: 24, backgroundColor: colors.background }}>
      <Text style={{ fontSize: 26, fontWeight: "700", color: colors.text }}>Explore</Text>
      <Text style={{ marginTop: 10, textAlign: "center", color: colors.textMuted }}>
        Use this route as the second-route smoke baseline and discovery screen starter.
      </Text>
    </View>
  );
}
