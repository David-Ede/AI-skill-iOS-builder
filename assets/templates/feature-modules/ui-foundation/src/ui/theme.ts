import { useColorScheme } from "react-native";

export type ThemeMode = "light" | "dark";

export type ThemeColors = {
  background: string;
  surface: string;
  border: string;
  text: string;
  textMuted: string;
  tint: string;
  tabIconDefault: string;
  tabIconSelected: string;
  buttonPrimaryBackground: string;
  buttonPrimaryText: string;
  buttonSecondaryBackground: string;
  buttonSecondaryText: string;
  danger: string;
};

const lightTheme: ThemeColors = {
  background: "#f8fafc",
  surface: "#ffffff",
  border: "#cbd5e1",
  text: "#0f172a",
  textMuted: "#475569",
  tint: "#2563eb",
  tabIconDefault: "#64748b",
  tabIconSelected: "#2563eb",
  buttonPrimaryBackground: "#0f172a",
  buttonPrimaryText: "#ffffff",
  buttonSecondaryBackground: "#e2e8f0",
  buttonSecondaryText: "#0f172a",
  danger: "#b91c1c",
};

const darkTheme: ThemeColors = {
  background: "#020617",
  surface: "#0f172a",
  border: "#334155",
  text: "#f8fafc",
  textMuted: "#cbd5e1",
  tint: "#60a5fa",
  tabIconDefault: "#94a3b8",
  tabIconSelected: "#60a5fa",
  buttonPrimaryBackground: "#f8fafc",
  buttonPrimaryText: "#0f172a",
  buttonSecondaryBackground: "#1e293b",
  buttonSecondaryText: "#f8fafc",
  danger: "#fca5a5",
};

export function resolveThemeMode(colorScheme: ReturnType<typeof useColorScheme>): ThemeMode {
  return colorScheme === "dark" ? "dark" : "light";
}

export function getThemeColors(mode: ThemeMode): ThemeColors {
  return mode === "dark" ? darkTheme : lightTheme;
}

export function useThemeMode(): ThemeMode {
  return resolveThemeMode(useColorScheme());
}

export function useThemeColors(): ThemeColors {
  return getThemeColors(useThemeMode());
}
