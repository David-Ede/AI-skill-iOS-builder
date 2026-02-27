import { useMemo, useState } from "react";
import { Pressable, Text, TextInput, View } from "react-native";
import { useAuth } from "../src/auth/AuthContext";
import type { OAuthProvider } from "../src/auth/types";

export default function SignInScreen() {
  const { signIn, signInWithOAuth, status, lastError } = useAuth();
  const [email, setEmail] = useState("demo@example.com");
  const [password, setPassword] = useState("password");
  const [busy, setBusy] = useState(false);

  const label = useMemo(() => (status === "authenticated" ? "Signed in" : "Sign In"), [status]);

  async function runEmailSignIn() {
    setBusy(true);
    try {
      await signIn(email, password);
    } finally {
      setBusy(false);
    }
  }

  async function runOAuth(provider: OAuthProvider) {
    setBusy(true);
    try {
      await signInWithOAuth(provider);
    } finally {
      setBusy(false);
    }
  }

  return (
    <View style={{ flex: 1, justifyContent: "center", padding: 24, gap: 12 }}>
      <Text style={{ fontSize: 26, fontWeight: "700" }}>Sign In</Text>
      <TextInput
        value={email}
        onChangeText={setEmail}
        autoCapitalize="none"
        style={{ borderWidth: 1, borderColor: "#cbd5e1", borderRadius: 10, padding: 10 }}
      />
      <TextInput
        value={password}
        onChangeText={setPassword}
        secureTextEntry
        style={{ borderWidth: 1, borderColor: "#cbd5e1", borderRadius: 10, padding: 10 }}
      />
      <Pressable
        disabled={busy}
        onPress={runEmailSignIn}
        style={{ backgroundColor: "#0f172a", padding: 12, borderRadius: 10, opacity: busy ? 0.7 : 1 }}
      >
        <Text style={{ color: "#ffffff", textAlign: "center" }}>{label}</Text>
      </Pressable>
      <Pressable
        disabled={busy}
        onPress={() => runOAuth("apple")}
        style={{ backgroundColor: "#111827", padding: 12, borderRadius: 10, opacity: busy ? 0.7 : 1 }}
      >
        <Text style={{ color: "#ffffff", textAlign: "center" }}>Continue with Apple</Text>
      </Pressable>
      <Pressable
        disabled={busy}
        onPress={() => runOAuth("google")}
        style={{ backgroundColor: "#2563eb", padding: 12, borderRadius: 10, opacity: busy ? 0.7 : 1 }}
      >
        <Text style={{ color: "#ffffff", textAlign: "center" }}>Continue with Google</Text>
      </Pressable>
      <Text style={{ fontSize: 12, color: "#475569", textAlign: "center" }}>
        OAuth buttons are provider slots. Configure client IDs and backend token exchange before
        production.
      </Text>
      {lastError ? (
        <Text style={{ color: "#b91c1c", textAlign: "center", marginTop: 6 }}>{lastError}</Text>
      ) : null}
    </View>
  );
}
