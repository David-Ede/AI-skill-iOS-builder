import { Text, View } from "react-native";
import { useThemeColors } from "../ui/theme";

export function ProfileActions() {
  const colors = useThemeColors();

  return (
    <View style={{ gap: 8 }}>
      <Text style={{ color: colors.text }}>Account action placeholders:</Text>
      <Text style={{ color: colors.textMuted }}>- Sign out</Text>
      <Text style={{ color: colors.textMuted }}>- Delete account</Text>
      <Text style={{ color: colors.textMuted }}>- Notification preferences</Text>
    </View>
  );
}
