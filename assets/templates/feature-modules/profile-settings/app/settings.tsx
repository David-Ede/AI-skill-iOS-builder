import { Text, View } from "react-native";
import { ProfileActions } from "../src/profile/ProfileActions";

export default function SettingsScreen() {
  return (
    <View style={{ flex: 1, padding: 24, justifyContent: "center", gap: 12 }}>
      <Text style={{ fontSize: 26, fontWeight: "700" }}>Settings</Text>
      <Text>Place app preferences and account controls here.</Text>
      <ProfileActions />
    </View>
  );
}
