import { Text, View } from "react-native";

export function ProfileActions() {
  return (
    <View style={{ gap: 8 }}>
      <Text>Account action placeholders:</Text>
      <Text>- Sign out</Text>
      <Text>- Delete account</Text>
      <Text>- Notification preferences</Text>
    </View>
  );
}
