import { Text, View } from "react-native";
import { ProfileActions } from "../src/profile/ProfileActions";
import { useThemeColors } from "../src/ui/theme";

export default function SettingsScreen() {
  const colors = useThemeColors();

  return (
    <View style={{ flex: 1, padding: 24, justifyContent: "center", gap: 12, backgroundColor: colors.background }}>
      <Text style={{ fontSize: 26, fontWeight: "700", color: colors.text }}>Settings</Text>
      <Text style={{ color: colors.textMuted }}>Place app preferences and account controls here.</Text>
      <ProfileActions />
    </View>
  );
}
