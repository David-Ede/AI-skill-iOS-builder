import { Stack } from "expo-router";
import { StatusBar } from "expo-status-bar";
import { useThemeColors, useThemeMode } from "../src/ui/theme";

export default function RootLayout() {
  const colors = useThemeColors();
  const mode = useThemeMode();

  return (
    <>
      <StatusBar style={mode === "dark" ? "light" : "dark"} />
      <Stack
        screenOptions={{
          headerShown: false,
          contentStyle: { backgroundColor: colors.background },
        }}
      />
    </>
  );
}
