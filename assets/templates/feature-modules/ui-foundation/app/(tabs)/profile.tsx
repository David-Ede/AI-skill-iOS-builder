import { Link } from "expo-router";
import { Text, View } from "react-native";

export default function ProfileScreen() {
  return (
    <View style={{ flex: 1, justifyContent: "center", alignItems: "center", padding: 24 }}>
      <Text style={{ fontSize: 26, fontWeight: "700" }}>Profile</Text>
      <Text style={{ marginTop: 8 }}>Avatar placeholder and account actions starter.</Text>
      <Link href="/settings" style={{ marginTop: 12, color: "#2563eb" }}>
        Go to Settings
      </Link>
    </View>
  );
}
