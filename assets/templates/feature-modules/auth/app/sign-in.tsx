import { useMemo, useState } from "react";
import { Pressable, Text, TextInput, View } from "react-native";
import { useAuth } from "../src/auth/AuthContext";

export default function SignInScreen() {
  const { signIn, status } = useAuth();
  const [email, setEmail] = useState("demo@example.com");
  const [password, setPassword] = useState("password");
  const label = useMemo(() => (status === "authenticated" ? "Signed in" : "Sign In"), [status]);

  return (
    <View style={{ flex: 1, justifyContent: "center", padding: 24, gap: 12 }}>
      <Text style={{ fontSize: 26, fontWeight: "700" }}>Sign In</Text>
      <TextInput value={email} onChangeText={setEmail} autoCapitalize="none" style={{ borderWidth: 1, borderColor: "#cbd5e1", borderRadius: 10, padding: 10 }} />
      <TextInput value={password} onChangeText={setPassword} secureTextEntry style={{ borderWidth: 1, borderColor: "#cbd5e1", borderRadius: 10, padding: 10 }} />
      <Pressable onPress={() => signIn(email, password)} style={{ backgroundColor: "#0f172a", padding: 12, borderRadius: 10 }}>
        <Text style={{ color: "#ffffff", textAlign: "center" }}>{label}</Text>
      </Pressable>
    </View>
  );
}
