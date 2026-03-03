import { Link } from "expo-router";
import { Text, View } from "react-native";
import { useThemeColors } from "../../src/ui/theme";

export default function ProfileScreen() {
  const colors = useThemeColors();

  return (
    <View style={{ flex: 1, justifyContent: "center", alignItems: "center", padding: 24, backgroundColor: colors.background }}>
      <Text style={{ fontSize: 26, fontWeight: "700", color: colors.text }}>Profile</Text>
      <Text style={{ marginTop: 8, color: colors.textMuted }}>
        Avatar placeholder and account actions starter.
      </Text>
      <Link href="/settings" style={{ marginTop: 12, color: colors.tint }}>
        Go to Settings
      </Link>
    </View>
  );
}
