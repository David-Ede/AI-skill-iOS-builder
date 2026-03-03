import { useMemo, useState } from "react";
import { Pressable, Text, TextInput, View } from "react-native";
import { useAuth } from "../src/auth/AuthContext";
import type { OAuthProvider } from "../src/auth/types";
import { useThemeColors } from "../src/ui/theme";

export default function SignInScreen() {
  const { signIn, signInWithOAuth, status, lastError } = useAuth();
  const [email, setEmail] = useState("demo@example.com");
  const [password, setPassword] = useState("password");
  const [busy, setBusy] = useState(false);
  const colors = useThemeColors();

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
    <View style={{ flex: 1, justifyContent: "center", padding: 24, gap: 12, backgroundColor: colors.background }}>
      <Text style={{ fontSize: 26, fontWeight: "700", color: colors.text }}>Sign In</Text>
      <TextInput
        value={email}
        onChangeText={setEmail}
        autoCapitalize="none"
        placeholderTextColor={colors.textMuted}
        style={{ borderWidth: 1, borderColor: colors.border, borderRadius: 10, padding: 10, color: colors.text, backgroundColor: colors.surface }}
      />
      <TextInput
        value={password}
        onChangeText={setPassword}
        secureTextEntry
        placeholderTextColor={colors.textMuted}
        style={{ borderWidth: 1, borderColor: colors.border, borderRadius: 10, padding: 10, color: colors.text, backgroundColor: colors.surface }}
      />
      <Pressable
        disabled={busy}
        onPress={runEmailSignIn}
        style={{ backgroundColor: colors.buttonPrimaryBackground, padding: 12, borderRadius: 10, opacity: busy ? 0.7 : 1 }}
      >
        <Text style={{ color: colors.buttonPrimaryText, textAlign: "center" }}>{label}</Text>
      </Pressable>
      <Pressable
        disabled={busy}
        onPress={() => runOAuth("apple")}
        style={{ backgroundColor: colors.buttonPrimaryBackground, padding: 12, borderRadius: 10, opacity: busy ? 0.7 : 1 }}
      >
        <Text style={{ color: colors.buttonPrimaryText, textAlign: "center" }}>Continue with Apple</Text>
      </Pressable>
      <Pressable
        disabled={busy}
        onPress={() => runOAuth("google")}
        style={{ backgroundColor: colors.tint, padding: 12, borderRadius: 10, opacity: busy ? 0.7 : 1 }}
      >
        <Text style={{ color: "#ffffff", textAlign: "center" }}>Continue with Google</Text>
      </Pressable>
      <Text style={{ fontSize: 12, color: colors.textMuted, textAlign: "center" }}>
        OAuth buttons are provider slots. Configure client IDs and backend token exchange before
        production.
      </Text>
      {lastError ? (
        <Text style={{ color: colors.danger, textAlign: "center", marginTop: 6 }}>{lastError}</Text>
      ) : null}
    </View>
  );
}
