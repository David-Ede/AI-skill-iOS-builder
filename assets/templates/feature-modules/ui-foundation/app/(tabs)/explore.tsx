import { Text, View } from "react-native";

export default function ExploreScreen() {
  return (
    <View style={{ flex: 1, justifyContent: "center", alignItems: "center", padding: 24 }}>
      <Text style={{ fontSize: 26, fontWeight: "700" }}>Explore</Text>
      <Text style={{ marginTop: 10, textAlign: "center" }}>
        Use this route as the second-route smoke baseline and discovery screen starter.
      </Text>
    </View>
  );
}
